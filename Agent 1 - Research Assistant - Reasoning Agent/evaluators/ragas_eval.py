from __future__ import annotations

import asyncio
from typing import Any
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, context_precision, context_recall, faithfulness
from app.agent import ResearchAgent
from evaluators.dataset import load_jsonl

def _build_rows(dataset_path: str) -> list[dict[str, Any]]:
    agent = ResearchAgent()
    rows = []
    for row in load_jsonl(dataset_path):
        result = agent.answer(row['topic'], row['question'], max_papers=row.get('max_papers', 6), refresh=False)
        rows.append(
            {
                'question': row['question'],
                'answer': result.answer,
                'contexts': [ctx.snippet for ctx in result.context],
                'ground_truth': row['ground_truth'],
            }
        )
    return rows


def run_ragas_benchmark(dataset_path: str) -> dict:
    rows = _build_rows(dataset_path)
    dataset = Dataset.from_list(rows)
    result = evaluate(dataset=dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
    return dict(result)
