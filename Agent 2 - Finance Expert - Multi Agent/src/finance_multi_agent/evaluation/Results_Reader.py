import os
import json
import sqlite3
import html
import re
from typing import Any, List, Tuple

import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_rows", 200)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "finance_agent.db")


def strip_html_tags(text: str) -> str:
    if not isinstance(text, str):
        return str(text)
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_anchor_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    m = re.search(r'>(.*?)</a>', text, flags=re.IGNORECASE | re.DOTALL)
    return strip_html_tags(m.group(1)) if m else ""


def extract_source_from_html(text: str) -> str:
    if not isinstance(text, str):
        return ""
    cleaned = strip_html_tags(text)
    parts = [p.strip() for p in cleaned.split("  ") if p.strip()]
    if len(parts) >= 2:
        return parts[-1]
    return ""


def normalize_news_rows(rows: list) -> pd.DataFrame:
    cleaned_rows = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        new_row = dict(row)

        for key in list(new_row.keys()):
            val = new_row[key]

            if isinstance(val, str):
                new_row[key] = strip_html_tags(val)

        description_raw = row.get("description") or row.get("summary") or row.get("content") or ""
        title_from_html = extract_anchor_text(description_raw)
        source_from_html = extract_source_from_html(description_raw)

        if "title" not in new_row or not new_row.get("title"):
            if title_from_html:
                new_row["title"] = title_from_html

        if "source" not in new_row or not new_row.get("source"):
            if source_from_html:
                new_row["source"] = source_from_html

        cleaned_rows.append(new_row)

    df = pd.DataFrame(cleaned_rows)

    preferred_order = [
        "title",
        "source",
        "published",
        "published_at",
        "pubDate",
        "link",
        "ticker",
        "summary",
        "description",
    ]

    ordered = [c for c in preferred_order if c in df.columns]
    remaining = [c for c in df.columns if c not in ordered]
    return df[ordered + remaining]


def is_ohlcv_record(item: Any) -> bool:
    if not isinstance(item, dict):
        return False
    keys = set(item.keys())
    expected = {"Date", "Open", "High", "Low", "Close"}
    return len(keys.intersection(expected)) >= 4


def is_news_record(item: Any) -> bool:
    if not isinstance(item, dict):
        return False
    keys = set(item.keys())
    news_keys = {"title", "link", "published", "pubDate", "description", "summary", "source"}
    return len(keys.intersection(news_keys)) >= 2


def find_tabular_lists(obj: Any, path: str = "root") -> List[Tuple[str, list]]:
    found = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            found.extend(find_tabular_lists(value, f"{path}.{key}"))

    elif isinstance(obj, list):
        if obj and all(isinstance(x, dict) for x in obj):
            found.append((path, obj))

        for i, item in enumerate(obj[:10]):
            found.extend(find_tabular_lists(item, f"{path}[{i}]"))

    return found


def normalize_ohlcv_table(rows: list) -> pd.DataFrame:
    df = pd.DataFrame(rows)

    preferred_order = [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Volume",
        "Dividends",
        "Stock Splits",
    ]
    ordered = [c for c in preferred_order if c in df.columns]
    remaining = [c for c in df.columns if c not in ordered]
    df = df[ordered + remaining]

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.sort_values("Date", ascending=False)

    return df


def print_dataframe(df: pd.DataFrame, title: str, max_rows: int = 15) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    if df.empty:
        print("No rows found.")
    else:
        print(df.head(max_rows).to_string(index=False))


def inspect_analysis_runs(conn: sqlite3.Connection) -> None:
    print("\n" + "=" * 120)
    print("ANALYSIS_RUNS (Latest 15 rows)")
    print("=" * 120)

    try:
        df = pd.read_sql("SELECT * FROM analysis_runs ORDER BY ROWID DESC LIMIT 15", conn)
        print_dataframe(df, "analysis_runs", 15)

        preferred_cols = [
            "ticker",
            "technical_score",
            "macro_score",
            "final_score",
            "recommendation",
            "verdict",
            "confidence",
            "today_price_summary",
            "created_at",
        ]
        available = [c for c in preferred_cols if c in df.columns]
        if available:
            print_dataframe(df[available], "analysis_runs (selected columns)", 15)

    except Exception as e:
        print(f"Error reading analysis_runs: {e}")


def inspect_other_tables(conn: sqlite3.Connection, tables: List[str]) -> None:
    for table in tables:
        if table in {"analysis_runs", "state_snapshots"}:
            continue

        print("\n" + "=" * 120)
        print(f"{table.upper()} (Latest 15 rows)")
        print("=" * 120)

        try:
            df = pd.read_sql(f"SELECT * FROM {table} ORDER BY ROWID DESC LIMIT 15", conn)
            print_dataframe(df, table, 15)
        except Exception as e:
            print(f"Error reading {table}: {e}")


def inspect_state_snapshots(conn: sqlite3.Connection) -> None:
    print("\n" + "=" * 120)
    print("STATE_SNAPSHOTS (Latest 5 rows, parsed)")
    print("=" * 120)

    try:
        snapshots = pd.read_sql(
            "SELECT * FROM state_snapshots ORDER BY ROWID DESC LIMIT 5",
            conn,
        )
    except Exception as e:
        print(f"Error reading state_snapshots: {e}")
        return

    if snapshots.empty:
        print("No state snapshots found.")
        return

    for _, row in snapshots.iterrows():
        snapshot_id = row.get("id")
        run_id = row.get("run_id")
        node_name = row.get("node_name")
        created_at = row.get("created_at")
        state_json = row.get("state_json")

        print("\n" + "#" * 120)
        print(f"SNAPSHOT id={snapshot_id} | run_id={run_id} | node={node_name} | created_at={created_at}")
        print("#" * 120)

        try:
            parsed = json.loads(state_json)
        except Exception as e:
            print(f"Failed to parse state_json: {e}")
            continue

        if isinstance(parsed, dict):
            print("\nTop-level keys:")
            print(list(parsed.keys()))

        tabular_sections = find_tabular_lists(parsed)

        if not tabular_sections:
            print("\nNo tabular list found in this snapshot.")
            print(json.dumps(parsed, indent=2)[:4000])
            continue

        found_any = False

        for path, rows in tabular_sections:
            if not rows:
                continue
            first = rows[0]

            try:
                if is_ohlcv_record(first):
                    df = normalize_ohlcv_table(rows)
                    print_dataframe(df, f"Detected OHLCV table at: {path}", 15)
                    found_any = True

                elif is_news_record(first):
                    df = normalize_news_rows(rows)
                    print_dataframe(df, f"Detected NEWS table at: {path}", 15)
                    found_any = True

            except Exception as e:
                print(f"Could not print section at {path}: {e}")

        if not found_any:
            print("\nNo OHLCV/news table found. JSON preview:")
            print(json.dumps(parsed, indent=2)[:4000])


def main() -> None:
    print("Using DB:", DB_PATH)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)

    try:
        tables_df = pd.read_sql(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name",
            conn,
        )
        tables = tables_df["name"].tolist()

        print("\nTables Found:")
        if tables:
            print(tables_df.to_string(index=False))
        else:
            print("No tables found.")
            return

        inspect_analysis_runs(conn)
        inspect_state_snapshots(conn)
        inspect_other_tables(conn, tables)

    finally:
        conn.close()
        print("\nDatabase connection closed.")


if __name__ == "__main__":
    main()