from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class Paper(BaseModel):
    id: str
    title: str
    abstract: str = ''
    authors: List[str] = Field(default_factory=list)
    published: Optional[str] = None
    updated: Optional[str] = None
    source: str
    url: str
    doi: Optional[str] = None
    venue: Optional[str] = None
    citation_count: Optional[int] = None
    topics: List[str] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)


class QueryRequest(BaseModel):
    topic: str
    question: str
    max_papers: int = 8
    refresh: bool = True


class IngestRequest(BaseModel):
    topic: str
    max_papers: int = 25


class RetrievedContext(BaseModel):
    paper_id: str
    title: str
    snippet: str
    score: float
    url: str
    published: Optional[str] = None


class QueryResponse(BaseModel):
    topic: str
    answer: str
    papers: List[Paper]
    context: List[RetrievedContext]
    telemetry: dict[str, Any]


class BenchmarkRequest(BaseModel):
    dataset_path: str = 'data/eval_dataset.jsonl'
    concurrency: int = 4
    requests: int = 20
