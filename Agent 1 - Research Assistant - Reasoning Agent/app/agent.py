from __future__ import annotations

import time
from typing import Any

from app.clients import EmbeddingClient, LLMClient, RerankClient
from app.config import settings
from app.models import Paper, QueryResponse, RetrievedContext
from app.paper_sources import PaperSourceClient
from app.vector_store import PaperVectorStore


class ResearchAgent:
    def __init__(self) -> None:
        self.paper_client = PaperSourceClient()
        self.vector_store = PaperVectorStore()
        self.embedding_client = EmbeddingClient(
            settings.embedding_base_url,
            settings.embedding_api_key,
        )
        self.rerank_client = RerankClient(
            settings.rerank_base_url,
            settings.rerank_api_key,
        )
        self.llm_client = LLMClient(
            settings.llm_base_url,
            settings.llm_api_key,
        )

    def ingest_topic(self, topic: str, max_papers: int = 25) -> list[Paper]:
        papers = self.paper_client.search_recent(topic, max_results=max_papers)
        if not papers:
            return []

        texts = [self._paper_text(p) for p in papers]
        vectors = self.embedding_client.embed_passages(texts)
        self.vector_store.upsert_papers(papers, vectors)
        return papers

    def answer(self, topic: str, question: str, max_papers: int, refresh: bool = True) -> QueryResponse:
        started = time.perf_counter()
        fresh_papers: list[Paper] = []

        if refresh:
            fresh_papers = self.ingest_topic(topic, max_papers=max(12, max_papers))

        query_vector = self.embedding_client.embed_query(question)
        candidates = self.vector_store.search(query_vector, limit=max(12, max_papers))
        reranked = self._rerank(question, candidates, top_n=max_papers)

        answer, llm_telemetry = self.llm_client.generate(
            question,
            [ctx.model_dump() for ctx in reranked],
        )

        total_ms = (time.perf_counter() - started) * 1000.0

        papers_by_id = {paper.id: paper for paper in fresh_papers}
        resolved_papers = [papers_by_id[ctx.paper_id] for ctx in reranked if ctx.paper_id in papers_by_id]

        telemetry: dict[str, Any] = {
            "fresh_papers_found": len(fresh_papers),
            "retrieved_candidates": len(candidates),
            "reranked_contexts": len(reranked),
            "total_latency_ms": total_ms,
            **llm_telemetry,
        }

        return QueryResponse(
            topic=topic,
            answer=answer,
            papers=resolved_papers,
            context=reranked,
            telemetry=telemetry,
        )

    def _rerank(self, question: str, contexts: list[RetrievedContext], top_n: int) -> list[RetrievedContext]:
        if not contexts:
            return []

        docs = [self._rerank_text(ctx) for ctx in contexts]
        scores = self.rerank_client.rerank(question, docs, top_n=top_n)

        if not scores:
            return contexts[:top_n]

        results: list[RetrievedContext] = []
        used_indexes: set[int] = set()

        for row in scores[:top_n]:
            index = int(row["index"])
            if 0 <= index < len(contexts) and index not in used_indexes:
                used_indexes.add(index)
                ctx = contexts[index]
                results.append(
                    ctx.model_copy(
                        update={"score": float(row.get("relevance_score", ctx.score))}
                    )
                )

        return results or contexts[:top_n]

    @staticmethod
    # def _paper_text(paper: Paper) -> str:
    #     author_blob = ", ".join(paper.authors[:8])
    #     text = (
    #         f"Title: {paper.title}\n"
    #         f"Authors: {author_blob}\n"
    #         f"Published: {paper.published}\n"
    #         f"Abstract: {paper.abstract}"
    #     )
    #     return text[:2000]

    def _paper_text(paper: Paper) -> str:
        author_blob = ", ".join(paper.authors[:5])
        text = (
            f"{paper.title}. "
            f"{paper.abstract}"
        )
        return text[:1000]  # still keep smaller


    @staticmethod
    def _rerank_text(ctx: RetrievedContext) -> str:
        text = f"{ctx.title}\n{ctx.snippet}"
        return text[:2000]