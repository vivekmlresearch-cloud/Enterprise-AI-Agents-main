from __future__ import annotations

import logging
from uuid import uuid4

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from .agents import data_agent, input_agent, judge_agent, macro_agent, technical_agent
from .db.session import SessionLocal, save_analysis_result, save_snapshot
from .state import GraphState

logger = logging.getLogger(__name__)


def _wrap(node_name: str, func):
    def inner(state: GraphState) -> GraphState:
        updates = func(state)
        merged = dict(state)
        merged.update(updates)
        with SessionLocal() as session:
            save_snapshot(session, state["run_id"], node_name, merged)
            if node_name == "judge_agent":
                for result in updates.get("judge_results", {}).values():
                    save_analysis_result(session, state["run_id"], result)
        return updates

    return inner


class FinanceAgentGraph:
    def __init__(self) -> None:
        builder = StateGraph(GraphState)
        builder.add_node("input_agent", _wrap("input_agent", input_agent.run))
        builder.add_node("data_agent", _wrap("data_agent", data_agent.run))
        builder.add_node("technical_agent", _wrap("technical_agent", technical_agent.run))
        builder.add_node("macro_agent", _wrap("macro_agent", macro_agent.run))
        builder.add_node("judge_agent", _wrap("judge_agent", judge_agent.run))

        builder.add_edge(START, "input_agent")
        builder.add_edge("input_agent", "data_agent")
        builder.add_edge("data_agent", "technical_agent")
        builder.add_edge("technical_agent", "macro_agent")
        builder.add_edge("macro_agent", "judge_agent")
        builder.add_edge("judge_agent", END)

        self.graph = builder.compile(checkpointer=InMemorySaver())

    def invoke(self, stocks_file: str) -> GraphState:
        run_id = str(uuid4())
        config = {"configurable": {"thread_id": run_id}}
        initial_state: GraphState = {
            "run_id": run_id,
            "thread_id": run_id,
            "stocks_file": stocks_file,
            "tickers": [],
            "invalid_tickers": [],
            "raw_market_data": {},
            "technical_results": {},
            "macro_results": {},
            "judge_results": {},
            "alerts_sent": [],
            "errors": [],
            "metadata": {},
        }
        logger.info("Starting graph run %s", run_id)
        return self.graph.invoke(initial_state, config)
