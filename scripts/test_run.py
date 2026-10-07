"""Hermetic check of run.py's production-build staleness logic.

    python scripts/test_run.py        # stdlib only: no server, no network, temp dir

Covers: when web/.next counts as current vs. when the launcher must rebuild.
"""
import importlib.util
import os
import socket
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

_spec = importlib.util.spec_from_file_location("alphascribe_run", Path(__file__).with_name("run.py"))
run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run)


class WebBuildReason(unittest.TestCase):
    def setUp(self):
        self._orig_web = run.WEB
        self._tmp = tempfile.TemporaryDirectory()
        self.web = run.WEB = Path(self._tmp.name)
        self.env = {"NEXT_PUBLIC_API_BASE_URL": "http://localhost:8001"}
        self.page = self._write("app/page.tsx", "x")
        self.test_file = self._write("features/a/Thing.test.tsx", "t")
        self.notes = self._write("lib/NOTES.md", "n")
        self._write(".env.local", 'NEXT_PUBLIC_API_BASE_URL="http://localhost:8001"\n')
        self.started = time.time()
        for f in (self.page, self.test_file, self.notes, self.web / ".env.local"):
            os.utime(f, (self.started - 100, self.started - 100))  # all older than the build

    def tearDown(self):
        run.WEB = self._orig_web
        self._tmp.cleanup()

    def _write(self, rel, text):
        f = self.web / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
        return f

    def _finish_build(self):
        self._write(".next/BUILD_ID", "id")
        self._write(f".next/{run.WEB_BUILD_STAMP}", run._stamp_text(self.env, self.started))

    def _newer(self, f):
        os.utime(f, (self.started + 100, self.started + 100))

    def test_no_build_means_build(self):
        self.assertIn("no production build", run.web_build_reason(self.env))

    def test_current_build_is_skipped(self):
        self._finish_build()
        self.assertIsNone(run.web_build_reason(self.env))

    def test_build_without_stamp_is_not_trusted(self):  # failed/cancelled build, or `--dev` ran since
        self._finish_build()
        (self.web / ".next" / run.WEB_BUILD_STAMP).unlink()
        self.assertIn("no production build", run.web_build_reason(self.env))

    def test_edited_source_forces_rebuild(self):
        self._finish_build()
        self._newer(self.page)
        self.assertIn("page.tsx", run.web_build_reason(self.env))

    def test_renamed_source_forces_rebuild(self):  # a rename keeps its mtime, so mtimes alone miss it
        self._finish_build()
        renamed = self.page.rename(self.page.with_name("home.tsx"))
        self.assertLess(renamed.stat().st_mtime, self.started)  # guard: really invisible to the mtime scan
        self.assertIn("added, removed or renamed", run.web_build_reason(self.env))

    def test_deleted_source_forces_rebuild(self):
        self._finish_build()
        self.page.unlink()
        self.assertIn("added, removed or renamed", run.web_build_reason(self.env))

    def test_malformed_stamp_counts_as_no_build(self):  # crash mid-write, or an older stamp format
        stamp = self.web / ".next" / run.WEB_BUILD_STAMP
        for bad in ("", "\n", "garbage", "abc def", "abc def not-a-number\n", "abc\n1.0\n",
                    "x\ny\nz\nw\n"):  # empty, junk, too few fields (the old 2-field format), bad float, too many
            with self.subTest(stamp=bad):
                self._finish_build()
                stamp.write_text(bad)
                self.assertIn("no production build", run.web_build_reason(self.env))

    def test_edited_test_or_markdown_does_not(self):
        self._finish_build()
        self._newer(self.test_file)
        self._newer(self.notes)
        self.assertIsNone(run.web_build_reason(self.env))

    def test_changed_next_public_env_forces_rebuild(self):
        self._finish_build()
        self.assertIn("NEXT_PUBLIC", run.web_build_reason({"NEXT_PUBLIC_API_BASE_URL": "http://x"}))

    def test_changed_env_file_forces_rebuild(self):
        self._finish_build()
        self._write(".env.local", 'NEXT_PUBLIC_API_BASE_URL="http://localhost:9999"\n')
        self.assertIn("NEXT_PUBLIC", run.web_build_reason(self.env))

    def test_ensure_web_env_leaves_identical_file_alone(self):  # else every start would look stale
        run.ensure_web_env()
        f = self.web / ".env.local"
        os.utime(f, (self.started - 5, self.started - 5))
        run.ensure_web_env()
        self.assertEqual(f.stat().st_mtime, self.started - 5)


class BackendBindHost(unittest.TestCase):
    """The `--host localhost` guard: dual loopback only when EVERY resolved address is loopback."""

    @staticmethod
    def _resolve(*addrs):
        infos = [(socket.AF_INET6 if ":" in a else socket.AF_INET, socket.SOCK_STREAM, 6, "",
                  (a, 8001, 0, 0) if ":" in a else (a, 8001)) for a in addrs]
        return mock.patch.object(run.socket, "getaddrinfo", return_value=infos)

    def _host(self, *addrs):
        with self._resolve(*addrs):
            return run.backend_bind_host()

    def test_dual_stack_loopback_uses_localhost(self):
        host, note = self._host("::1", "127.0.0.1")
        self.assertEqual(host, "localhost")
        self.assertIn("::1", note)

    def test_ipv6_less_host_still_works(self):  # getaddrinfo returns only IPv4 loopback
        self.assertEqual(self._host("127.0.0.1")[0], "localhost")

    def test_whole_127_8_block_counts_as_loopback(self):
        self.assertEqual(self._host("127.0.0.1", "127.0.0.2")[0], "localhost")

    def test_any_non_loopback_address_falls_back_and_says_why(self):
        for extra in ("192.168.1.5", "10.10.39.98", "2001:db8::1", "fe80::1%12"):
            with self.subTest(extra=extra):
                host, note = self._host("127.0.0.1", "::1", extra)
                self.assertEqual(host, "127.0.0.1")
                self.assertIn(extra.split("%")[0], note)

    def test_only_non_loopback_falls_back(self):
        self.assertEqual(self._host("10.0.0.5")[0], "127.0.0.1")

    def test_ipv6_only_loopback_falls_back(self):  # run.py's own port checks need 127.0.0.1
        self.assertEqual(self._host("::1")[0], "127.0.0.1")

    def test_no_addresses_falls_back(self):
        self.assertEqual(self._host()[0], "127.0.0.1")

    def test_resolution_failure_falls_back_and_says_why(self):
        with mock.patch.object(run.socket, "getaddrinfo", side_effect=socket.gaierror("boom")):
            host, note = run.backend_bind_host()
        self.assertEqual(host, "127.0.0.1")
        self.assertIn("could not resolve", note)


if __name__ == "__main__":
    unittest.main()
