from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from app.agent import ResearchAgent

mcp = FastMCP('research-assistant-mcp')
agent = ResearchAgent()


@mcp.tool()
def search_recent_papers(topic: str, max_papers: int = 8) -> list[dict]:
    papers = agent.ingest_topic(topic, max_papers=max_papers)
    return [paper.model_dump() for paper in papers]


@mcp.tool()
def get_paper_details(topic: str, question: str, max_papers: int = 5) -> dict:
    result = agent.answer(topic, question, max_papers=max_papers, refresh=True)
    return result.model_dump()


@mcp.tool()
def run_topic_digest(topic: str, max_papers: int = 10) -> dict:
    question = f'Provide a concise digest of the latest research on {topic}, grouped by themes.'
    result = agent.answer(topic, question, max_papers=max_papers, refresh=True)
    return {
        'topic': topic,
        'answer': result.answer,
        'papers': [paper.model_dump() for paper in result.papers],
        'telemetry': result.telemetry,
    }


if __name__ == '__main__':
    mcp.run(transport='streamable-http')
