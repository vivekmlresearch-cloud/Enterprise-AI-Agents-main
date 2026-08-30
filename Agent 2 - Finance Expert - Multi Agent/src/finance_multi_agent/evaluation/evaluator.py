from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from ..db.session import SessionLocal, init_db, save_evaluation


VERDICTS = ["BUY", "WATCH", "AVOID"]


def evaluate(predictions_path: str, labels_path: str) -> dict:
    preds = {row["ticker"]: row for row in _read_jsonl(predictions_path)}
    labels = {row["ticker"]: row for row in _read_jsonl(labels_path)}

    total = 0
    correct = 0
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)

    for ticker, label in labels.items():
        pred = preds.get(ticker)
        if not pred:
            continue
        total += 1
        y_true = label["verdict"]
        y_pred = pred["verdict"]
        if y_true == y_pred:
            correct += 1
            tp[y_true] += 1
        else:
            fp[y_pred] += 1
            fn[y_true] += 1

    precision = {}
    for verdict in VERDICTS:
        denom = tp[verdict] + fp[verdict]
        precision[verdict] = round(tp[verdict] / denom, 4) if denom else 0.0

    accuracy = round(correct / total, 4) if total else 0.0
    metrics = {
        "accuracy": accuracy,
        "buy_precision": precision["BUY"],
        "watch_precision": precision["WATCH"],
        "avoid_precision": precision["AVOID"],
        "support": total,
    }
    return metrics


def _read_jsonl(path: str):
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            yield json.loads(line)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate prediction quality.")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--labels", required=True)
    parser.add_argument("--run-name", default="offline_eval")
    args = parser.parse_args()

    metrics = evaluate(args.predictions, args.labels)
    init_db()
    with SessionLocal() as session:
        save_evaluation(
            session,
            run_name=args.run_name,
            accuracy=metrics["accuracy"],
            buy_precision=metrics["buy_precision"],
            watch_precision=metrics["watch_precision"],
            avoid_precision=metrics["avoid_precision"],
            metrics=metrics,
        )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
