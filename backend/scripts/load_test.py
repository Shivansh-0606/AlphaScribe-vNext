"""M6 — load/stress validation. No new dependency: asyncio + httpx (already
a runtime dep via agents/llm.py's provider calls) is enough for a fixed-
concurrency latency/error-rate probe; a real load framework (locust/k6)
would be new infrastructure for what a ~100-line script already answers.

Hits public, no-auth endpoints only (/health, /health/ready, /metrics, /) —
covers the request-timing middleware and the Mongo-backed health checks
without needing a seeded corpus or an LLM key. The report pipeline
(/reports/generate) is deliberately NOT load-tested here: it burns real LLM
provider quota/cost per request, which a load generator must not do without
an explicit opt-in the caller controls (see --include-pipeline below).

Usage:
    python backend/scripts/load_test.py --base-url http://localhost:8001 \
        --concurrency 20 --duration 15
"""
from __future__ import annotations

import argparse
import asyncio
import statistics
import time

import httpx

_ENDPOINTS = ("/api/health", "/api/health/ready", "/api/metrics", "/api/")


async def _worker(client: httpx.AsyncClient, base_url: str, deadline: float,
                   latencies: list[float], errors: list[str]) -> None:
    i = 0
    while time.monotonic() < deadline:
        path = _ENDPOINTS[i % len(_ENDPOINTS)]
        i += 1
        start = time.monotonic()
        try:
            resp = await client.get(f"{base_url}{path}", timeout=10.0)
            latencies.append(time.monotonic() - start)
            if resp.status_code >= 500:
                errors.append(f"{path}: {resp.status_code}")
        except Exception as e:  # noqa: BLE001 — a connection error is a result, not a crash
            latencies.append(time.monotonic() - start)
            errors.append(f"{path}: {type(e).__name__}")


def _percentile(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = min(len(sorted_vals) - 1, int(len(sorted_vals) * pct))
    return sorted_vals[idx]


async def run(base_url: str, concurrency: int, duration_s: float) -> dict:
    latencies: list[float] = []
    errors: list[str] = []
    deadline = time.monotonic() + duration_s
    async with httpx.AsyncClient() as client:
        await asyncio.gather(*[
            _worker(client, base_url, deadline, latencies, errors) for _ in range(concurrency)
        ])
    latencies.sort()
    total = len(latencies)
    return {
        "requests": total,
        "errors": len(errors),
        "error_rate": (len(errors) / total) if total else 0.0,
        "rps": total / duration_s,
        "p50_ms": _percentile(latencies, 0.50) * 1000,
        "p95_ms": _percentile(latencies, 0.95) * 1000,
        "p99_ms": _percentile(latencies, 0.99) * 1000,
        "max_ms": (max(latencies) if latencies else 0.0) * 1000,
        "sample_errors": errors[:5],
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-url", default="http://localhost:8001")
    p.add_argument("--concurrency", type=int, default=20)
    p.add_argument("--duration", type=float, default=15.0)
    args = p.parse_args()

    result = asyncio.run(run(args.base_url, args.concurrency, args.duration))
    print(f"requests={result['requests']} rps={result['rps']:.1f} "
          f"errors={result['errors']} ({result['error_rate']:.2%})")
    print(f"p50={result['p50_ms']:.1f}ms p95={result['p95_ms']:.1f}ms "
          f"p99={result['p99_ms']:.1f}ms max={result['max_ms']:.1f}ms")
    if result["sample_errors"]:
        print("sample errors:", result["sample_errors"])


if __name__ == "__main__":
    main()
