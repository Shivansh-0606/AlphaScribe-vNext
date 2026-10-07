#!/usr/bin/env python3
"""AlphaScribe one-command local launcher.

Run everything (MongoDB + FastAPI backend + Next.js frontend) from a single
terminal. Everything it installs is kept inside the project:

  .venv/        Python virtual environment (backend deps)
  .mongo/       portable MongoDB binary + data files
  web/node_modules/   frontend deps

Usage:
    python scripts/run.py            # set up (first run) and start all services
    python scripts/run.py --dev      # `next dev` bound to 127.0.0.1 (HMR, but every
                                     # route compiles on first visit: 6-14 s)
    python scripts/run.py --rebuild  # force a fresh production web build
    python scripts/run.py --setup    # only install/download, don't start
    python scripts/run.py --clean    # remove .venv, .mongo, node_modules and exit

The web app is served from a production build (`next build` + `next start`,
127.0.0.1 only). The build is skipped when web/.next is current (see
web_build_reason); `--dev` skips it entirely.

First run downloads a portable MongoDB (~250 MB), installs deps and builds the
web app, so it takes a few minutes. Subsequent runs start in seconds unless the
web sources changed. Press Ctrl+C to stop.
"""
from __future__ import annotations

import hashlib
import ipaddress
import os
import platform
import shutil
import signal
import socket
import subprocess
import sys
import tarfile
import threading
import time
import urllib.request
import venv
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths / config
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
WEB = ROOT / "web"
VENV = ROOT / ".venv"
MONGO_DIR = ROOT / ".mongo"
MONGO_DATA = MONGO_DIR / "data"

IS_WIN = os.name == "nt"
MONGO_VERSION = os.environ.get("MONGO_VERSION", "7.0.14")

MONGO_PORT = 27017
BACKEND_PORT = 8001
FRONTEND_PORT = 3001  # 3000 is often taken by the Hermes WhatsApp bridge

# What invalidates the production web build (tests/docs deliberately don't).
WEB_SRC_DIRS = ("app", "components", "features", "lib", "providers", "public", "styles")
WEB_SRC_FILES = ("package.json", "package-lock.json", "next.config.*", "postcss.config.*",
                 "tsconfig.json")
WEB_ENV_FILES = (".env", ".env.local", ".env.production", ".env.production.local")
# in web/.next, next to BUILD_ID: "<env hash>\n<source-path-list hash>\n<build start time>"
WEB_BUILD_STAMP = "BUILD_ENV_HASH"

# ANSI colors (enabled on Windows 10+ via the os.system("") trick below)
RESET = "\033[0m"
COLORS = {"setup": "\033[36m", "mongo": "\033[35m", "api": "\033[32m", "web": "\033[34m"}
_PROCS: list[tuple[str, subprocess.Popen]] = []


def log(msg: str, tag: str = "setup") -> None:
    sys.stdout.write(f"{COLORS.get(tag, '')}[{tag}]{RESET} {msg}\n")
    sys.stdout.flush()


def die(msg: str) -> None:
    log(f"ERROR: {msg}", "setup")
    shutdown()
    sys.exit(1)


def run(cmd: list, cwd: Path | None = None) -> None:
    log("$ " + " ".join(str(c) for c in cmd))
    subprocess.check_call(cmd, cwd=str(cwd) if cwd else None)


def venv_python() -> Path:
    return VENV / ("Scripts" if IS_WIN else "bin") / ("python.exe" if IS_WIN else "python")


def port_open(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        return s.connect_ex((host, port)) == 0


def wait_port(port: int, timeout: float = 40.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if port_open(port):
            return True
        time.sleep(0.5)
    return False


def backend_bind_host():
    """(host for `uvicorn --host`, log line). `localhost` makes asyncio bind every
    address it resolves to, i.e. 127.0.0.1 AND ::1. Without the ::1 listener a
    browser pays a ~300 ms IPv6-fallback wait on new connections to
    http://localhost:8001 (measured in Chrome). It is used only when every
    resolved address is loopback and 127.0.0.1 is among them (this script's own
    port checks use it); otherwise plain 127.0.0.1, so a hosts-file or DNS
    surprise can never expose the backend to the network."""
    try:
        infos = socket.getaddrinfo("localhost", BACKEND_PORT, socket.AF_UNSPEC,
                                   socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
    except OSError as e:
        return "127.0.0.1", f"could not resolve localhost ({e}) - binding 127.0.0.1 only"
    addrs = sorted({info[4][0].split("%")[0] for info in infos})
    try:
        loopback = all(ipaddress.ip_address(a).is_loopback for a in addrs)
    except ValueError:
        loopback = False
    if not addrs or not loopback or "127.0.0.1" not in addrs:
        return "127.0.0.1", (f"localhost resolves to {addrs or 'nothing'} (not all loopback, or no "
                             f"127.0.0.1) - binding 127.0.0.1 only")
    return "localhost", f"binding localhost = {', '.join(addrs)} (loopback only)"


def free_port(port: int) -> None:
    """Kill whatever process is listening on `port` (e.g. a stale backend from a
    previous run that would otherwise serve outdated code)."""
    try:
        if IS_WIN:
            out = subprocess.run(["netstat", "-ano", "-p", "tcp"],
                                 capture_output=True, text=True).stdout
            pids = set()
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 5 and parts[1].endswith(f":{port}") and parts[3] == "LISTENING":
                    pids.add(parts[4])
            for pid in pids:
                subprocess.run(["taskkill", "/F", "/PID", pid],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            out = subprocess.run(["lsof", "-ti", f"tcp:{port}"],
                                 capture_output=True, text=True).stdout
            for pid in out.split():
                subprocess.run(["kill", "-9", pid],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:  # noqa: BLE001
        pass
    time.sleep(1.0)


# ---------------------------------------------------------------------------
# Setup steps
# ---------------------------------------------------------------------------
def ensure_venv() -> None:
    if venv_python().exists():
        return
    log("creating virtual environment in .venv ...")
    venv.create(VENV, with_pip=True)


def ensure_backend_deps() -> None:
    sentinel = VENV / ".deps_ok"
    if sentinel.exists():
        return
    py = str(venv_python())
    log("installing backend dependencies into .venv (first run — a few minutes) ...")
    run([py, "-m", "pip", "install", "--upgrade", "pip"])
    run([py, "-m", "pip", "install", "-r", str(BACKEND / "requirements.txt")])
    sentinel.write_text("ok")


def check_gemini_key() -> None:
    """Warn (don't block) if no Gemini API key is configured — the app runs but
    AI features will error until a key is added to backend/.env."""
    env = BACKEND / ".env"
    has_key = False
    if env.exists():
        for line in env.read_text(encoding="utf-8", errors="ignore").splitlines():
            s = line.strip()
            if s.startswith("GEMINI_API_KEY=") and s.split("=", 1)[1].strip():
                has_key = True
                break
    if not has_key:
        log("WARNING: no GEMINI_API_KEY in backend/.env — the app will start, but")
        log("         report generation will fail until you add a free key from")
        log("         https://aistudio.google.com/apikey")


def ensure_web_env() -> None:
    """Point the UI at the local backend without touching the committed .env.
    Next.js loads .env.local at higher priority than .env."""
    content = (
        f'NEXT_PUBLIC_APP_URL="http://localhost:{FRONTEND_PORT}"\n'
        f'NEXT_PUBLIC_API_BASE_URL="http://localhost:{BACKEND_PORT}"\n'
    )
    env_local = WEB / ".env.local"
    # Not rewritten when identical: a fresh mtime on every start would make the
    # production build look stale (see web_build_reason).
    if not env_local.exists() or env_local.read_text() != content:
        env_local.write_text(content)


def _web_deps_ok() -> bool:
    """True only if node_modules looks usable *on this OS*. A node_modules that
    was installed elsewhere (e.g. with yarn on macOS and shipped in the zip)
    lacks the Windows .cmd shims, so the `next` binary fails to launch."""
    next_bin = WEB / "node_modules" / ".bin" / ("next.cmd" if IS_WIN else "next")
    return next_bin.exists()


def ensure_web_deps() -> None:
    if _web_deps_ok():
        return
    npm = shutil.which("npm") or ("npm.cmd" if IS_WIN else "npm")
    if not shutil.which("npm"):
        die("npm not found on PATH. Install Node.js (which includes npm) first.")
    nm = WEB / "node_modules"
    if nm.exists():
        log("web node_modules is incomplete/foreign — reinstalling cleanly ...")
        shutil.rmtree(nm, ignore_errors=True)
    log("installing web dependencies (npm install — first run, a few minutes) ...")
    run([npm, "install"], cwd=WEB)


# ---------------------------------------------------------------------------
# Production web build (web/.next)
# ---------------------------------------------------------------------------
def _web_env_hash(env: dict) -> str:
    """NEXT_PUBLIC_* is inlined at build time, so a build is only valid for the
    env it was made with: hash those vars plus the .env files Next loads."""
    h = hashlib.sha256()
    for key in sorted(k for k in env if k.startswith("NEXT_PUBLIC_")):
        h.update(f"{key}={env[key]}\0".encode())
    for name in WEB_ENV_FILES:
        f = WEB / name
        if f.is_file():
            h.update(name.encode() + b"\0" + f.read_bytes() + b"\0")
    return h.hexdigest()


def _web_sources():
    for d in WEB_SRC_DIRS:
        for f in (WEB / d).rglob("*"):
            if f.is_file() and ".test." not in f.name and ".spec." not in f.name \
                    and f.suffix != ".md":
                yield f
    for pattern in (*WEB_SRC_FILES, *WEB_ENV_FILES):
        yield from (f for f in WEB.glob(pattern) if f.is_file())


def _web_paths_hash(files) -> str:
    """Hash of the sorted source path list. An edit bumps an mtime, but a delete
    or a rename keeps every remaining mtime, so only this notices them."""
    rels = sorted({f.relative_to(WEB).as_posix() for f in files})
    return hashlib.sha256("\0".join(rels).encode()).hexdigest()


def _stamp_text(env: dict, started: float) -> str:
    return f"{_web_env_hash(env)}\n{_web_paths_hash(_web_sources())}\n{started}\n"


def _read_stamp(stamp: Path) -> tuple[str, str, float] | None:
    """(env hash, paths hash, build start time), or None when the stamp is
    missing or unreadable — empty/truncated by a crash mid-write, or an older
    format — which counts as 'no build', never an error."""
    try:
        env_hash, paths_hash, started = stamp.read_text().split()
        return env_hash, paths_hash, float(started)
    except (OSError, ValueError):
        return None


def web_build_reason(env: dict) -> str | None:
    """Why the production web build must be (re)made, or None if web/.next is
    current: no completed build, a different NEXT_PUBLIC_*/.env, source files
    added/removed/renamed, or one modified since the last build *started* (not
    finished, so an edit made while it was running is still caught)."""
    next_dir = WEB / ".next"
    stamp = _read_stamp(next_dir / WEB_BUILD_STAMP)
    if stamp is None or not (next_dir / "BUILD_ID").exists():
        return "no production build yet"
    env_hash, paths_hash, started = stamp
    if env_hash != _web_env_hash(env):
        return "NEXT_PUBLIC_* / .env values changed since the last build"
    files = list(_web_sources())
    if paths_hash != _web_paths_hash(files):
        return "web source files were added, removed or renamed since the last build"
    newer = next((f for f in files if f.stat().st_mtime > started), None)
    return f"{newer.relative_to(WEB)} changed since the last build" if newer else None


def build_web(next_bin: Path, env: dict, reason: str) -> None:
    """`next build`, streamed live. Fails loudly — never falls back to dev."""
    log(f"building the production web app ({reason}) — a few minutes ...", "web")
    stamp = WEB / ".next" / WEB_BUILD_STAMP
    stamp.unlink(missing_ok=True)  # a failed/cancelled build must not look current
    started = time.time()
    snapshot = _stamp_text(env, started)  # taken before the build: later edits/renames read as stale
    p = spawn("web", [str(next_bin), "build"], WEB, env=env, pump=False)
    try:
        _pump(p, "web")  # returns at EOF, i.e. when the build has ended
        rc = p.wait()
    except KeyboardInterrupt:
        shutdown()
        log("build cancelled.", "web")
        sys.exit(130)
    except Exception:  # noqa: BLE001 — don't leave `next build` running behind a crash
        shutdown()
        raise
    if rc != 0:
        die(f"the web build failed (exit code {rc}) — see the [web] output above. "
            f"Fix the error and re-run, or use --dev to skip the build.")
    stamp.write_text(snapshot)
    log(f"build finished in {time.time() - started:.0f}s.", "web")


# ---------------------------------------------------------------------------
# MongoDB (portable, bundled into .mongo/)
# ---------------------------------------------------------------------------
def _mongod_binary() -> Path | None:
    name = "mongod.exe" if IS_WIN else "mongod"
    hits = list(MONGO_DIR.rglob(name))
    return hits[0] if hits else None


def _mongo_download_url() -> str:
    v = MONGO_VERSION
    sysname = platform.system()
    arch = platform.machine().lower()
    if sysname == "Windows":
        return f"https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-{v}.zip"
    if sysname == "Darwin":
        a = "arm64" if arch in ("arm64", "aarch64") else "x86_64"
        return f"https://fastdl.mongodb.org/osx/mongodb-macos-{a}-{v}.tgz"
    # Linux — best-effort (Ubuntu 22.04 build)
    return f"https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu2204-{v}.tgz"


def _download(url: str, dest: Path) -> None:
    log(f"downloading MongoDB {MONGO_VERSION} (~250 MB, one time) ...")
    log(url)

    def hook(blocks, bs, total):
        if total > 0:
            pct = min(100, blocks * bs * 100 // total)
            sys.stdout.write(f"\r[mongo] {pct:3d}%")
            sys.stdout.flush()

    urllib.request.urlretrieve(url, dest, reporthook=hook)
    sys.stdout.write("\n")


def ensure_mongo() -> Path | None:
    """Return the mongod binary to launch, or None if an external MongoDB is
    already listening on the port (in which case we reuse it)."""
    if port_open(MONGO_PORT):
        log(f"a MongoDB is already running on :{MONGO_PORT} — reusing it", "mongo")
        return None
    MONGO_DIR.mkdir(exist_ok=True)
    binary = _mongod_binary()
    if not binary:
        url = _mongo_download_url()
        suffix = ".zip" if url.endswith(".zip") else ".tgz"
        archive = MONGO_DIR / f"mongo{suffix}"
        try:
            _download(url, archive)
        except Exception as e:  # noqa: BLE001
            die(f"failed to download MongoDB: {e}\n"
                f"      Set MONGO_URL in backend/.env to a MongoDB Atlas connection "
                f"string to skip the local download, then re-run.")
        log("extracting ...", "mongo")
        if suffix == ".zip":
            with zipfile.ZipFile(archive) as z:
                z.extractall(MONGO_DIR)
        else:
            with tarfile.open(archive) as t:
                t.extractall(MONGO_DIR)
        archive.unlink(missing_ok=True)
        binary = _mongod_binary()
    if not binary:
        die("could not locate the mongod binary after extraction")
    if not IS_WIN:
        os.chmod(binary, 0o755)
    MONGO_DATA.mkdir(parents=True, exist_ok=True)
    return binary


# ---------------------------------------------------------------------------
# Process orchestration
# ---------------------------------------------------------------------------
def spawn(tag: str, cmd: list, cwd: Path, env: dict | None = None,
          pump: bool = True) -> subprocess.Popen:
    """Start a child; with pump=False the caller drains its output with _pump()."""
    kw: dict = {}
    if IS_WIN:
        kw["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kw["start_new_session"] = True
    log("$ " + " ".join(str(c) for c in cmd), tag)
    p = subprocess.Popen(
        cmd, cwd=str(cwd), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, **kw,
    )
    _PROCS.append((tag, p))
    if pump:
        threading.Thread(target=_pump, args=(p, tag), daemon=True).start()
    return p


def _pump(p: subprocess.Popen, tag: str) -> None:
    color = COLORS.get(tag, "")
    assert p.stdout is not None
    for line in p.stdout:
        sys.stdout.write(f"{color}[{tag}]{RESET} {line}")
        sys.stdout.flush()


def shutdown() -> None:
    for tag, p in _PROCS:
        if p.poll() is None:
            try:
                if IS_WIN:
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            except Exception:  # noqa: BLE001
                pass


def clean() -> None:
    for path in (VENV, MONGO_DIR, WEB / "node_modules", WEB / ".env.local", WEB / ".next"):
        if path.exists():
            log(f"removing {path.relative_to(ROOT)} ...")
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                path.unlink(missing_ok=True)
    log("clean complete.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    if IS_WIN:
        os.system("")  # enable ANSI escape processing on Windows terminals
    if hasattr(sys.stdout, "reconfigure"):  # Next's ✓ etc. must not crash a redirected cp1252 stdout
        sys.stdout.reconfigure(errors="replace")

    args = set(sys.argv[1:])
    dev = bool(args & {"--dev", "--web-dev"})
    if "--clean" in args:
        clean()
        return

    # --- setup (idempotent) ---
    ensure_venv()
    ensure_backend_deps()
    ensure_web_env()
    ensure_web_deps()
    check_gemini_key()
    mongod = ensure_mongo()

    if "--setup" in args:
        log("setup complete. Run `python scripts/run.py` to start.")
        return

    for port, what in ((BACKEND_PORT, "backend"), (FRONTEND_PORT, "frontend")):
        if port_open(port):
            log(f"port {port} ({what}) is in use by a stale process — freeing it ...")
            free_port(port)
            if port_open(port):
                die(f"port {port} ({what}) is still in use — stop that process and retry.")

    # --- web build (before anything is spawned, so a failed/cancelled build leaves nothing running) ---
    web_env = {**os.environ, "BROWSER": "none"}
    next_bin = WEB / "node_modules" / ".bin" / ("next.cmd" if IS_WIN else "next")
    if dev:
        if "--rebuild" in args:
            log("--rebuild ignored: --dev serves with `next dev` and builds nothing.", "web")
        # `next dev` rewrites web/.next, so a production build there is no longer valid.
        (WEB / ".next" / WEB_BUILD_STAMP).unlink(missing_ok=True)
    else:
        reason = "--rebuild" if "--rebuild" in args else web_build_reason(web_env)
        if reason:
            build_web(next_bin, web_env, reason)
        else:
            log("production web build is up to date — skipping the build "
                "(--rebuild forces one).", "web")

    # --- launch ---
    if mongod is not None:
        spawn("mongo", [str(mongod), "--dbpath", str(MONGO_DATA),
                        "--port", str(MONGO_PORT), "--bind_ip", "127.0.0.1"], MONGO_DIR)
        log("waiting for MongoDB ...", "mongo")
        if not wait_port(MONGO_PORT):
            die("MongoDB did not start in time")

    api_host, api_note = backend_bind_host()
    log(api_note, "api")
    # --timeout-keep-alive 75 (uvicorn's default is 5): a connection the server drops while
    # the user pauses costs the browser a fresh connect on the next click.
    spawn("api", [str(venv_python()), "-m", "uvicorn", "server:app",
                  "--host", api_host, "--port", str(BACKEND_PORT),
                  "--timeout-keep-alive", "75"],
          BACKEND, env={**os.environ})

    # loopback only: both `next dev` and `next start` bind 0.0.0.0 (the whole LAN) by default
    web_cmd = [str(next_bin), "dev" if dev else "start", "-p", str(FRONTEND_PORT),
               "-H", "127.0.0.1"]
    if not dev:  # `next start` drops idle connections after 6 s unless told otherwise
        web_cmd += ["--keepAliveTimeout", "75000"]
    spawn("web", web_cmd, WEB, env=web_env)

    log("")
    log("AlphaScribe is starting" + (" (web: `next dev`, routes compile on first visit):" if dev
                                     else " (web: production build):"))
    log(f"    UI       ->  http://localhost:{FRONTEND_PORT}")
    log(f"    API      ->  http://localhost:{BACKEND_PORT}/api/health")
    log(f"    seed data->  POST http://localhost:{BACKEND_PORT}/api/ingest/samples")
    log("Press Ctrl+C to stop everything.")

    try:
        while True:
            time.sleep(1)
            for tag, p in _PROCS:
                if p.poll() is not None and tag in ("api", "mongo"):
                    die(f"the '{tag}' process exited unexpectedly (see logs above)")
    except KeyboardInterrupt:
        log("\nshutting down ...")
    finally:
        shutdown()


if __name__ == "__main__":
    main()
