from __future__ import annotations

import json
from pathlib import Path

from evaluators.inference import run_inference_benchmark
from evaluators.ragas_eval import run_ragas_benchmark
from evaluators.retrieval import run_retrieval_benchmark


ARTIFACT_DIR = Path('artifacts')
ARTIFACT_DIR.mkdir(exist_ok=True)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def build_summary(ragas_results: dict, retrieval_results: dict, inference_results: dict) -> str:
    return f"""# Benchmark Summary

## RAGAS
- Faithfulness: {ragas_results.get('faithfulness')}
- Answer Relevancy: {ragas_results.get('answer_relevancy')}
- Context Precision: {ragas_results.get('context_precision')}
- Context Recall: {ragas_results.get('context_recall')}

## Retrieval
- Recall@K: {retrieval_results.get('recall_at_k')}
- MRR@K: {retrieval_results.get('mrr_at_k')}
- nDCG@K: {retrieval_results.get('ndcg_at_k')}

## Inference
- Requests: {inference_results.get('requests')}
- Throughput (req/s): {inference_results.get('throughput_rps')}
- p50 latency (ms): {inference_results.get('latency_ms_p50')}
- p95 latency (ms): {inference_results.get('latency_ms_p95')}
- Avg tool calls: {inference_results.get('avg_tool_calls')}
- Avg context size: {inference_results.get('avg_context_size')}
"""


def run_all_benchmarks(dataset_path: str, concurrency: int = 4, requests: int = 20) -> dict:
    ragas_results = run_ragas_benchmark(dataset_path)
    retrieval_results = run_retrieval_benchmark(dataset_path)
    inference_results = run_inference_benchmark(dataset_path, concurrency=concurrency, requests=requests)

    write_json(ARTIFACT_DIR / 'ragas_results.json', ragas_results)
    write_json(ARTIFACT_DIR / 'retrieval_results.json', retrieval_results)
    write_json(ARTIFACT_DIR / 'inference_results.json', inference_results)

    summary = build_summary(ragas_results, retrieval_results, inference_results)
    (ARTIFACT_DIR / 'summary.md').write_text(summary, encoding='utf-8')

    return {
        'ragas': ragas_results,
        'retrieval': retrieval_results,
        'inference': inference_results,
        'summary_path': str(ARTIFACT_DIR / 'summary.md'),
    }


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--concurrency', type=int, default=4)
    parser.add_argument('--requests', type=int, default=20)
    args = parser.parse_args()

    print(run_all_benchmarks(args.dataset, args.concurrency, args.requests))
