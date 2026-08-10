"""T-6 (M7, Doc 28 B-5) — restart-recovery. server.py's `@app.on_event
("startup")` handler (`_warmup`) sweeps any `jobs`/`explanation_jobs` row
still `queued`/`running` when the process boots — orphaned by a previous
process dying mid-run — and marks it `failed` (server.py ~1673-1687).

This calls the real `server._warmup()` coroutine directly (the literal
function FastAPI registers as the startup handler, not a reimplementation of
its update_many logic) against the same Mongo the live dev server uses
(`server.py` loads the same `.env` at import). Needs a live Mongo, so this is
`live`-marked like every other test in this repo that touches a real DB.

    python -m pytest backend/tests/test_restart_recovery.py -v
"""
import asyncio
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

# 06 §5.1 Ph0 / 05 T-1: needs live Mongo. Excluded from the hermetic CI job
# via `-m "not live"`.
pytestmark = pytest.mark.live

import server  # noqa: E402


def test_startup_sweep_marks_orphaned_jobs_failed_and_leaves_terminal_jobs_alone():
    async def run():
        orphan_ids = {}
        for coll_name in ("jobs", "explanation_jobs"):
            jid = f"m7-t6-orphan-{coll_name}-{uuid.uuid4().hex[:8]}"
            await server.db[coll_name].insert_one({
                "id": jid, "status": "running", "user_id": "m7-t6-user",
            })
            orphan_ids[coll_name] = jid

        # A terminal job present at boot must NOT be touched by the sweep —
        # only {"queued", "running"} are in scope (server.py's own $in filter).
        done_id = f"m7-t6-completed-{uuid.uuid4().hex[:8]}"
        await server.db.jobs.insert_one({
            "id": done_id, "status": "completed", "user_id": "m7-t6-user",
        })

        try:
            await server._warmup()  # the actual registered startup handler

            for coll_name, jid in orphan_ids.items():
                doc = await server.db[coll_name].find_one({"id": jid})
                assert doc is not None, f"{coll_name} orphan row disappeared"
                assert doc["status"] == "failed", f"{coll_name} orphan not swept: {doc}"
                assert doc.get("error") == "Server restarted mid-run."

            done_doc = await server.db.jobs.find_one({"id": done_id})
            assert done_doc["status"] == "completed"  # untouched by the sweep
        finally:
            for coll_name, jid in orphan_ids.items():
                await server.db[coll_name].delete_one({"id": jid})
            await server.db.jobs.delete_one({"id": done_id})

    asyncio.run(run())


if __name__ == "__main__":
    test_startup_sweep_marks_orphaned_jobs_failed_and_leaves_terminal_jobs_alone()
    print("ok: restart-recovery sweep marks orphaned jobs/explanation_jobs failed "
          "via the real server._warmup() startup handler; terminal jobs untouched")
