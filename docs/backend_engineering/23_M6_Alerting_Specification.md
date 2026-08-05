# M6 — Alerting Specification

**Milestone:** Backend Engineering M6 · **Date:** 2026-08-05
**Status:** Rule specification only — same reasoning as [`22`](22_M6_Dashboard_Specification.md):
no Alertmanager (or equivalent paging system) exists in this repo's
deployment target yet. Rules below are ready-to-import Prometheus alerting
rule YAML the day one does.

---

## Rule set

```yaml
groups:
  - name: alphascribe-service
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(alphascribe_http_requests_total{status=~"5.."}[5m]))
          / sum(rate(alphascribe_http_requests_total[5m])) > 0.05
        for: 5m
        labels: {severity: page}
        annotations:
          summary: "5xx rate above 5% for 5 minutes"

      - alert: HighLatencyP95
        expr: |
          histogram_quantile(0.95,
            sum(rate(alphascribe_http_request_duration_seconds_bucket[5m])) by (le)) > 2
        for: 10m
        labels: {severity: warn}
        annotations:
          summary: "p95 request latency above 2s for 10 minutes"

  - name: alphascribe-pipeline
    rules:
      - alert: PipelineFailureRateHigh
        expr: |
          sum(rate(alphascribe_pipeline_runs_total{status="failed"}[15m])) by (graph)
          / sum(rate(alphascribe_pipeline_runs_total[15m])) by (graph) > 0.2
        for: 15m
        labels: {severity: page}
        annotations:
          summary: "{{ $labels.graph }} pipeline failure rate above 20% for 15 minutes"

      - alert: JobsActiveNearCapacity
        # MAX_ACTIVE_JOBS default is 8 (07 §5) — this threshold must track
        # the deployed value; 90% of MAX_ACTIVE_JOBS is the trigger, not a
        # literal "7" hardcoded here.
        expr: sum(alphascribe_jobs_active) > 0.9 * <MAX_ACTIVE_JOBS>
        for: 5m
        labels: {severity: warn}
        annotations:
          summary: "Job admission near MAX_ACTIVE_JOBS — requests will start getting 429s"

      - alert: DeadlineExceedancesSpike
        expr: sum(rate(alphascribe_deadline_exceeded_total[30m])) > 0
        for: 0m
        labels: {severity: warn}
        annotations:
          summary: "A job hit its LG-11 deadline — investigate the labeled node for a stuck/slow provider"

  - name: alphascribe-security
    rules:
      - alert: LoginFailureSpike
        expr: |
          sum(rate(alphascribe_auth_failures_total{reason="bad_credentials"}[5m])) > 1
        for: 5m
        labels: {severity: warn}
        annotations:
          summary: "Elevated bad-credential login failures — possible brute-force (T-04)"

      - alert: CrossTenantProbeSpike
        expr: sum(rate(alphascribe_authz_denied_total{class="owner_scoped"}[10m])) > 0.5
        for: 10m
        labels: {severity: warn}
        annotations:
          summary: "Elevated cross-tenant authorization denials — possible UUID-enumeration probing (T-07/T-08)"

  - name: alphascribe-infra
    rules:
      - alert: RedisErrorsPresent
        expr: sum(rate(alphascribe_redis_errors_total[5m])) > 0
        for: 5m
        labels: {severity: page}
        annotations:
          summary: "Redis errors observed (only fires under JOB_BACKEND=redis) — check §8.1's fail-open posture (09)"

      - alert: ReadinessDown
        expr: probe_success{job="alphascribe-health-ready"} == 0
        for: 2m
        labels: {severity: page}
        annotations:
          summary: "GET /api/health/ready returning 503 — Mongo unreachable or retrieval degraded"
```

## Severity legend

| Severity | Meaning | Maps to |
|---|---|---|
| `page` | Wake someone up | `10` §12.2's severity model — SEV1/SEV2-shaped signals |
| `warn` | Investigate during business hours | Below paging threshold, worth a ticket |

## Deliberately not alerted on (this milestone)

| Signal | Why not |
|---|---|
| `alphascribe_ratelimit_degraded` | Not yet incremented anywhere (`19` §3, `20`) — an alert on a gauge with no call site would never fire and would be dead config. Add the rule in the same change that wires the gauge. |
| SSE session duration | Log-only, not metric-backed this milestone (`22` Dashboard 4) — no PromQL alert possible until it's promoted to a Histogram. |

## Cross-references

Threshold values (`0.05`, `0.2`, `<MAX_ACTIVE_JOBS>`, etc.) are starting
points, not measured production baselines — this environment has no
sustained production traffic to calibrate against yet. Revisit once real
traffic data exists (same "not yet observed at scale" caveat as `10`'s
own SD-5/SD-12 operational assumptions).
