import os
import json
import sqlite3
import textwrap
from typing import Any, Dict, List

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "finance_agent.db")
OUTPUT_IMAGE = os.path.join(BASE_DIR, "latest_run_decision_flow.png")


def pick_first_non_null(*values):
    for value in values:
        if value is not None:
            return value
    return None


def wrap_text(value: Any, width: int = 52) -> str:
    if value is None:
        return "None"
    text = str(value).strip()
    if not text:
        return "None"
    return "\n".join(textwrap.wrap(text, width=width))


def fmt_num(value: Any) -> str:
    if value is None:
        return "None"
    try:
        return f"{float(value):.2f}"
    except Exception:
        return str(value)


def extract_tickers(state: Dict[str, Any]) -> List[str]:
    tickers = state.get("tickers")
    if isinstance(tickers, list) and tickers:
        return tickers

    discovered = set()
    for key in ["raw_market_data", "technical_results", "macro_results", "judge_results"]:
        section = state.get(key, {})
        if isinstance(section, dict):
            discovered.update(section.keys())

    return sorted(discovered)


def load_latest_run_snapshots(db_path: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql(
            """
            SELECT id, run_id, node_name, state_json, created_at
            FROM state_snapshots
            ORDER BY created_at ASC
            """,
            conn,
        )
    finally:
        conn.close()

    if df.empty:
        return df

    latest_run_id = df["run_id"].iloc[-1]
    return df[df["run_id"] == latest_run_id].copy()


def build_stock_tree(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {}

    run_id = df["run_id"].iloc[0]
    tree: Dict[str, Any] = {"run_id": run_id, "stocks": {}}

    node_order = {
        "input_agent": 1,
        "data_agent": 2,
        "technical_agent": 3,
        "macro_agent": 4,
        "judge_agent": 5,
    }
    df["node_rank"] = df["node_name"].map(node_order).fillna(999)
    df = df.sort_values(["created_at", "node_rank"])

    for _, row in df.iterrows():
        node_name = row["node_name"]
        created_at = row["created_at"]

        try:
            state = json.loads(row["state_json"])
        except Exception:
            continue

        raw_market_data = state.get("raw_market_data", {}) or {}
        technical_results = state.get("technical_results", {}) or {}
        macro_results = state.get("macro_results", {}) or {}
        judge_results = state.get("judge_results", {}) or {}

        tickers = extract_tickers(state)

        for ticker in tickers:
            if ticker not in tree["stocks"]:
                tree["stocks"][ticker] = {
                    "input_agent": {},
                    "data_agent": {},
                    "technical_agent": {},
                    "macro_agent": {},
                    "judge_agent": {},
                }

            market = raw_market_data.get(ticker, {}) if isinstance(raw_market_data, dict) else {}
            tech = technical_results.get(ticker, {}) if isinstance(technical_results, dict) else {}
            macro = macro_results.get(ticker, {}) if isinstance(macro_results, dict) else {}
            judge = judge_results.get(ticker, {}) if isinstance(judge_results, dict) else {}

            if node_name == "input_agent":
                tree["stocks"][ticker]["input_agent"] = {
                    "status": "received",
                    "created_at": created_at,
                }

            elif node_name == "data_agent":
                tree["stocks"][ticker]["data_agent"] = {
                    "latest_price": pick_first_non_null(
                        market.get("latest_price"), market.get("close"), market.get("Close")
                    ),
                    "previous_close": pick_first_non_null(
                        market.get("previous_close"), market.get("prev_close")
                    ),
                    "created_at": created_at,
                }

            elif node_name == "technical_agent":
                tree["stocks"][ticker]["technical_agent"] = {
                    "technical_score": pick_first_non_null(tech.get("score"), tech.get("technical_score")),
                    "technical_signal": tech.get("signal"),
                    "technical_reason": pick_first_non_null(
                        tech.get("reason"), tech.get("summary"), tech.get("rationale"), tech.get("explanation")
                    ),
                    "created_at": created_at,
                }

            elif node_name == "macro_agent":
                tree["stocks"][ticker]["macro_agent"] = {
                    "macro_score": pick_first_non_null(macro.get("score"), macro.get("macro_score")),
                    "macro_signal": macro.get("signal"),
                    "macro_reason": pick_first_non_null(
                        macro.get("reason"), macro.get("summary"), macro.get("rationale"), macro.get("explanation")
                    ),
                    "created_at": created_at,
                }

            elif node_name == "judge_agent":
                tree["stocks"][ticker]["judge_agent"] = {
                    "final_score": pick_first_non_null(judge.get("score"), judge.get("final_score")),
                    "verdict": pick_first_non_null(judge.get("verdict"), judge.get("recommendation")),
                    "confidence": judge.get("confidence"),
                    "judge_reason": pick_first_non_null(
                        judge.get("reason"), judge.get("summary"), judge.get("rationale"), judge.get("explanation")
                    ),
                    "created_at": created_at,
                }

    return tree


def make_stock_panel_text(ticker: str, info: Dict[str, Any]) -> str:
    input_agent = info.get("input_agent", {})
    data_agent = info.get("data_agent", {})
    technical_agent = info.get("technical_agent", {})
    macro_agent = info.get("macro_agent", {})
    judge_agent = info.get("judge_agent", {})

    latest_price = data_agent.get("latest_price")
    previous_close = data_agent.get("previous_close")

    day_change = None
    if latest_price is not None and previous_close not in (None, 0):
        try:
            day_change = ((float(latest_price) - float(previous_close)) / float(previous_close)) * 100.0
        except Exception:
            day_change = None

    parts = [
        f"STOCK: {ticker}",
        "",
        "1) INPUT AGENT",
        f"   - Status: {input_agent.get('status', 'None')}",
        f"   - Timestamp: {input_agent.get('created_at', 'None')}",
        "",
        "2) DATA AGENT",
        f"   - Latest Price: {fmt_num(latest_price)}",
        f"   - Previous Close: {fmt_num(previous_close)}",
        f"   - Day Change %: {fmt_num(day_change)}" if day_change is not None else "   - Day Change %: None",
        f"   - Timestamp: {data_agent.get('created_at', 'None')}",
        "",
        "3) TECHNICAL AGENT",
        f"   - Technical Score: {fmt_num(technical_agent.get('technical_score'))}",
        f"   - Technical Signal: {technical_agent.get('technical_signal', 'None')}",
        "   - Technical Reason:",
        f"     {wrap_text(technical_agent.get('technical_reason'), 58)}",
        f"   - Timestamp: {technical_agent.get('created_at', 'None')}",
        "",
        "4) MACRO AGENT",
        f"   - Macro Score: {fmt_num(macro_agent.get('macro_score'))}",
        f"   - Macro Signal: {macro_agent.get('macro_signal', 'None')}",
        "   - Macro Reason:",
        f"     {wrap_text(macro_agent.get('macro_reason'), 58)}",
        f"   - Timestamp: {macro_agent.get('created_at', 'None')}",
        "",
        "5) JUDGE AGENT",
        f"   - Final Score: {fmt_num(judge_agent.get('final_score'))}",
        f"   - Verdict: {judge_agent.get('verdict', 'None')}",
        f"   - Confidence: {fmt_num(judge_agent.get('confidence'))}",
        "   - Judge Reason:",
        f"     {wrap_text(judge_agent.get('judge_reason'), 58)}",
        f"   - Timestamp: {judge_agent.get('created_at', 'None')}",
    ]

    return "\n".join(parts)


def draw_single_detailed_image(tree: Dict[str, Any], output_path: str) -> None:
    stocks = tree.get("stocks", {})
    run_id = tree.get("run_id", "unknown")

    if not stocks:
        raise ValueError("No stock data found to visualize.")

    stock_items = list(stocks.items())
    n = len(stock_items)

    fig_height = max(5 * n, 8)
    fig = plt.figure(figsize=(18, fig_height))
    ax = plt.gca()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    title = f"Finance Multi-Agent Decision Flow - Latest Run\nrun_id: {run_id}"
    ax.text(0.5, 0.975, title, ha="center", va="top", fontsize=18, fontweight="bold")

    top = 0.92
    bottom_margin = 0.04
    available_height = top - bottom_margin
    panel_h = available_height / n
    panel_x = 0.03
    panel_w = 0.94

    for idx, (ticker, info) in enumerate(stock_items):
        y_top = top - idx * panel_h
        y = y_top - panel_h + 0.01
        h = panel_h - 0.02

        box = FancyBboxPatch(
            (panel_x, y),
            panel_w,
            h,
            boxstyle="round,pad=0.008,rounding_size=0.01",
            linewidth=1.2,
            edgecolor="black",
            facecolor="#f7f7f7",
        )
        ax.add_patch(box)

        text = make_stock_panel_text(ticker, info)
        ax.text(
            panel_x + 0.015,
            y + h - 0.015,
            text,
            ha="left",
            va="top",
            fontsize=10,
            family="monospace",
            color="black",
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def print_console_summary(tree: Dict[str, Any]) -> None:
    print(f"run_id: {tree.get('run_id')}")
    print("stocks:")
    for ticker, info in tree.get("stocks", {}).items():
        judge = info.get("judge_agent", {})
        print(
            f"  - {ticker}: verdict={judge.get('verdict')}, "
            f"final_score={judge.get('final_score')}, confidence={judge.get('confidence')}"
        )


def main() -> None:
    print("Using DB:", DB_PATH)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    snapshots_df = load_latest_run_snapshots(DB_PATH)
    if snapshots_df.empty:
        print("No snapshots found in state_snapshots.")
        return

    tree = build_stock_tree(snapshots_df)
    print_console_summary(tree)

    draw_single_detailed_image(tree, OUTPUT_IMAGE)
    print(f"\nSaved detailed decision image to:\n{OUTPUT_IMAGE}")


if __name__ == "__main__":
    main()