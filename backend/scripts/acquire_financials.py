"""M8 Step 6 — the operational/manual acquisition trigger (Document 36
§4.3): "a manually-invoked command/script that calls acquire() directly...
useful operationally, but it requires a human to act, so it does not by
itself solve organic user liveness." Always available, independent of
whether the Financials acquisition-request endpoint (Step 7, not built in
this repository yet) exists.

Reuses exactly the same repository/use-case construction
app/container.py::build_container already does for server.py — no parallel
composition logic, no new abstraction. Calls AcquireFinancialsUseCase
(Step 5) directly, one identity per (period_type, statement_type)
combination requested; defaults to all six.

Usage:
    python backend/scripts/acquire_financials.py AAPL
    python backend/scripts/acquire_financials.py AAPL --period-type annual --statement-type income
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.settings import load_settings  # noqa: E402
from application.financials import AcquireFinancialsUseCase, AcquisitionResultKind  # noqa: E402
from domain.financials import PeriodType, StatementType  # noqa: E402
from infrastructure.mongo.acquisition_state import MongoAcquisitionStateRepository  # noqa: E402
from infrastructure.mongo.client import create_mongo_client  # noqa: E402
from infrastructure.mongo.financial_statements import MongoFinancialStatementRepository  # noqa: E402

_FAILURE_KINDS = {
    AcquisitionResultKind.PERSISTENCE_FAILED,
    AcquisitionResultKind.STATE_TRANSITION_FAILED,
    AcquisitionResultKind.UNEXPECTED_ERROR,
}


async def _run(ticker: str, period_types: list[PeriodType], statement_types: list[StatementType]) -> int:
    settings = load_settings()
    client = create_mongo_client(settings.mongo_url)
    db = client[settings.db_name]
    use_case = AcquireFinancialsUseCase(
        MongoFinancialStatementRepository(db), MongoAcquisitionStateRepository(db)
    )

    exit_code = 0
    for period_type in period_types:
        for statement_type in statement_types:
            result = await use_case.acquire(ticker, period_type, statement_type)
            detail = f" ({result.detail})" if result.detail else ""
            print(f"{ticker} {period_type.value} {statement_type.value}: {result.kind.value} -> "
                  f"{result.state.value}{detail}")
            if result.kind in _FAILURE_KINDS:
                exit_code = 1
    client.close()
    return exit_code


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ticker")
    parser.add_argument(
        "--period-type", choices=[p.value for p in PeriodType], action="append", dest="period_types",
        help="repeatable; defaults to both annual and quarterly",
    )
    parser.add_argument(
        "--statement-type", choices=[s.value for s in StatementType], action="append", dest="statement_types",
        help="repeatable; defaults to all three statement types",
    )
    args = parser.parse_args()

    period_types = [PeriodType(p) for p in args.period_types] if args.period_types else list(PeriodType)
    statement_types = (
        [StatementType(s) for s in args.statement_types] if args.statement_types else list(StatementType)
    )

    exit_code = asyncio.run(_run(args.ticker.strip().upper(), period_types, statement_types))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
