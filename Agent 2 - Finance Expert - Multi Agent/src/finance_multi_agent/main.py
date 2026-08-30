from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from .agents.email_agent import EmailAgent
from .db.session import SessionLocal, init_db
from .graph import FinanceAgentGraph
from .logging_config import setup_logging

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the multi-agent stock analysis system.")
    parser.add_argument("--stocks-file", required=True, help="Path to comma-separated ticker text file.")
    parser.add_argument("--output", default="analysis_results.json", help="Path for JSON output.")
    args = parser.parse_args()

    setup_logging()
    init_db()

    graph = FinanceAgentGraph()
    state = graph.invoke(args.stocks_file)

    results = list(state.get("judge_results", {}).values())
    Path(args.output).write_text(json.dumps(results, indent=2), encoding="utf-8")
    logger.info("Saved results to %s", args.output)

    email_agent = EmailAgent()
    with SessionLocal() as session:
        sent = []
        for result in results:
            if email_agent.send(session, state["run_id"], result):
                sent.append(result["ticker"])
        logger.info("Email alerts sent for: %s", sent)

    print(json.dumps({"run_id": state["run_id"], "results": results}, indent=2))


if __name__ == "__main__":
    main()
