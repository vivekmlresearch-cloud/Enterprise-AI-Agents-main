from __future__ import annotations

from typing import Iterable

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.config import settings
from app.models import Paper, RetrievedContext


class PaperVectorStore:
    def __init__(self) -> None:
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection = settings.qdrant_collection
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = {c.name for c in self.client.get_collections().collections}
        if self.collection not in collections:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=rest.VectorParams(size=settings.vector_size, distance=rest.Distance.COSINE),
            )

    def upsert_papers(self, papers: Iterable[Paper], vectors: list[list[float]]) -> None:
        points = []
        for paper, vector in zip(papers, vectors, strict=False):
            points.append(
                rest.PointStruct(
                    id=paper.id,
                    vector=vector,
                    payload=paper.model_dump(),
                )
            )
        if points:
            self.client.upsert(collection_name=self.collection, wait=True, points=points)

    def search(self, query_vector: list[float], limit: int) -> list[RetrievedContext]:
        matches = self.client.search(collection_name=self.collection, query_vector=query_vector, limit=limit)
        results: list[RetrievedContext] = []
        for row in matches:
            payload = row.payload or {}
            snippet = (payload.get('abstract') or '')[:1200]
            results.append(
                RetrievedContext(
                    paper_id=str(payload.get('id')),
                    title=str(payload.get('title')),
                    snippet=snippet,
                    score=float(row.score),
                    url=str(payload.get('url') or ''),
                    published=payload.get('published'),
                )
            )
        return results
