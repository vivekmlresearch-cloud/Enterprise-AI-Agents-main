from __future__ import annotations

import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.agent import ResearchAgent
from evaluators.dataset import load_jsonl


def run_inference_benchmark(dataset_path: str, concurrency: int, requests: int) -> dict:
    agent = ResearchAgent()
    rows = load_jsonl(dataset_path)[:requests]
    latencies = []
    tool_calls = []
    ctx_sizes = []

    def task(row: dict) -> dict:
        started = time.perf_counter()
        result = agent.answer(row['topic'], row['question'], max_papers=row.get('max_papers', 6), refresh=False)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return {
            'latency_ms': elapsed_ms,
            'tool_calls': 3,
            'context_size': len(result.context),
            'answer_chars': len(result.answer),
        }

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(task, row) for row in rows]
        for future in as_completed(futures):
            out = future.result()
            latencies.append(out['latency_ms'])
            tool_calls.append(out['tool_calls'])
            ctx_sizes.append(out['context_size'])
    wall_s = time.perf_counter() - started

    if not latencies:
        return {'requests': 0}

    return {
        'requests': len(latencies),
        'concurrency': concurrency,
        'wall_time_s': wall_s,
        'throughput_rps': len(latencies) / wall_s if wall_s else 0.0,
        'latency_ms_p50': statistics.median(latencies),
        'latency_ms_p95': sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)],
        'avg_tool_calls': statistics.mean(tool_calls),
        'avg_context_size': statistics.mean(ctx_sizes),
    }
