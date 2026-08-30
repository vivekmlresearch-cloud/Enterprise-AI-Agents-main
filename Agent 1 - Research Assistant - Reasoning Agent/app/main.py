from __future__ import annotations

from fastapi import FastAPI

from app.agent import ResearchAgent
from app.models import BenchmarkRequest, IngestRequest, QueryRequest
from evaluators.run_all import run_all_benchmarks

app = FastAPI(title='Research Assistant Agent', version='0.1.0')
agent = ResearchAgent()


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/research/ingest')
def ingest(request: IngestRequest):
    papers = agent.ingest_topic(request.topic, request.max_papers)
    return {'count': len(papers), 'papers': [p.model_dump() for p in papers]}


@app.post('/research/query')
def query(request: QueryRequest):
    result = agent.answer(request.topic, request.question, request.max_papers, request.refresh)
    return result.model_dump()


@app.post('/research/benchmark')
def benchmark(request: BenchmarkRequest):
    return run_all_benchmarks(dataset_path=request.dataset_path, concurrency=request.concurrency, requests=request.requests)
