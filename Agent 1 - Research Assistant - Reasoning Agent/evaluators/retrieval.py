from __future__ import annotations

import math
from collections import defaultdict

from app.agent import ResearchAgent
from evaluators.dataset import load_jsonl


def run_retrieval_benchmark(dataset_path: str, k: int = 5) -> dict:
    agent = ResearchAgent()
    rows = load_jsonl(dataset_path)
    hits = 0
    reciprocal_ranks = []
    ndcgs = []

    for row in rows:
        response = agent.answer(row['topic'], row['question'], max_papers=k, refresh=False)
        retrieved_titles = [ctx.title.lower() for ctx in response.context[:k]]
        gold_titles = [x.lower() for x in row.get('gold_titles', [])]
        first_rank = None
        dcg = 0.0
        idcg = 0.0
        for rank, title in enumerate(retrieved_titles, start=1):
            rel = 1 if any(gold in title for gold in gold_titles) else 0
            if rel and first_rank is None:
                first_rank = rank
            dcg += rel / math.log2(rank + 1)
        for rank in range(1, min(len(gold_titles), k) + 1):
            idcg += 1 / math.log2(rank + 1)
        if first_rank is not None:
            hits += 1
            reciprocal_ranks.append(1 / first_rank)
        else:
            reciprocal_ranks.append(0.0)
        ndcgs.append((dcg / idcg) if idcg else 0.0)

    total = max(len(rows), 1)
    return {
        'queries': len(rows),
        'recall_at_k': hits / total,
        'mrr_at_k': sum(reciprocal_ranks) / total,
        'ndcg_at_k': sum(ndcgs) / total,
    }
