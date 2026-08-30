from __future__ import annotations

import html
import logging
import re
import time
import xml.etree.ElementTree as ET
from typing import Iterable
from urllib.parse import urlencode

import httpx

from app.config import settings
from app.models import Paper
from app.utils import stable_id


logger = logging.getLogger(__name__)


class PaperSourceClient:
    def __init__(self) -> None:
        self.headers = {
            "User-Agent": settings.user_agent,
            "Accept": "application/atom+xml, application/json, text/xml;q=0.9, */*;q=0.8",
        }
        self.timeout = 45.0
        self.max_retries = 3

    def search_recent(self, topic: str, max_results: int = 10) -> list[Paper]:
        papers: list[Paper] = []

        arxiv_papers = self.search_arxiv(topic, max_results=max_results)
        papers.extend(arxiv_papers)

        if settings.semantic_scholar_api_key:
            try:
                semantic_papers = self.search_semantic_scholar(topic, max_results=max_results)
                papers.extend(semantic_papers)
            except Exception as exc:
                logger.warning("Semantic Scholar search failed; continuing with arXiv only: %s", exc)
        else:
            logger.info("Semantic Scholar API key not configured; using arXiv only.")

        deduped = self._dedupe(papers)
        deduped.sort(
            key=lambda p: (
                p.published or "",
                p.citation_count or 0,
            ),
            reverse=True,
        )
        return deduped[:max_results]

    def search_arxiv(self, topic: str, max_results: int = 10) -> list[Paper]:
        params = {
            "search_query": f"all:{topic}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        url = f"{settings.arxiv_api_url}?{urlencode(params)}"

        response_text = self._get_with_backoff(
            url=url,
            headers=self.headers,
            source_name="arXiv",
        )

        try:
            root = ET.fromstring(response_text)
        except ET.ParseError as exc:
            raise RuntimeError(f"Failed to parse arXiv XML response: {exc}") from exc

        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        results: list[Paper] = []

        for entry in root.findall("atom:entry", namespace):
            title = self._clean_text(entry.findtext("atom:title", default="", namespaces=namespace))
            abstract = self._clean_text(entry.findtext("atom:summary", default="", namespaces=namespace))
            published = entry.findtext("atom:published", default=None, namespaces=namespace)
            updated = entry.findtext("atom:updated", default=None, namespaces=namespace)
            paper_url = entry.findtext("atom:id", default="", namespaces=namespace)

            authors = [
                self._clean_text(a.findtext("atom:name", default="", namespaces=namespace))
                for a in entry.findall("atom:author", namespace)
            ]

            paper_id = stable_id(["arxiv", title, paper_url])

            results.append(
                Paper(
                    id=paper_id,
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    published=published,
                    updated=updated,
                    source="arXiv",
                    url=paper_url,
                    raw={"provider": "arxiv"},
                )
            )

        return results

    def search_semantic_scholar(self, topic: str, max_results: int = 10) -> list[Paper]:
        params = {
            "query": topic,
            "limit": max_results,
            "fields": "title,abstract,authors,year,url,venue,citationCount,publicationDate,externalIds",
            "sort": "publicationDate:desc",
        }

        headers = dict(self.headers)
        if settings.semantic_scholar_api_key:
            headers["x-api-key"] = settings.semantic_scholar_api_key

        url = f"{settings.semantic_scholar_api_url}/paper/search"

        response_json = self._get_json_with_backoff(
            url=url,
            headers=headers,
            params=params,
            source_name="Semantic Scholar",
        )

        results: list[Paper] = []

        for row in response_json.get("data", []):
            title = self._clean_text(row.get("title", ""))
            abstract = self._clean_text(row.get("abstract", ""))
            paper_url = row.get("url") or ""
            doi = (row.get("externalIds") or {}).get("DOI")
            authors = [self._clean_text(a.get("name", "")) for a in row.get("authors", [])]
            published = row.get("publicationDate") or (f"{row['year']}-01-01" if row.get("year") else None)

            paper_id = stable_id(["semantic_scholar", title, paper_url or str(doi)])

            results.append(
                Paper(
                    id=paper_id,
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    published=published,
                    source="Semantic Scholar",
                    url=paper_url or (f"https://doi.org/{doi}" if doi else ""),
                    doi=doi,
                    venue=row.get("venue"),
                    citation_count=row.get("citationCount"),
                    raw={"provider": "semantic_scholar"},
                )
            )

        return results

    def _get_with_backoff(self, url: str, headers: dict[str, str], source_name: str) -> str:
        last_error: Exception | None = None

        with httpx.Client(headers=headers, timeout=self.timeout, follow_redirects=True) as client:
            for attempt in range(self.max_retries):
                try:
                    response = client.get(url)

                    if response.status_code == 429:
                        wait_seconds = 2 ** attempt
                        logger.warning("%s rate limited (429). Retrying in %s seconds.", source_name, wait_seconds)
                        time.sleep(wait_seconds)
                        continue

                    response.raise_for_status()
                    return response.text

                except httpx.HTTPStatusError as exc:
                    last_error = exc
                    if exc.response.status_code in {429, 500, 502, 503, 504} and attempt < self.max_retries - 1:
                        wait_seconds = 2 ** attempt
                        logger.warning(
                            "%s HTTP error %s. Retrying in %s seconds.",
                            source_name,
                            exc.response.status_code,
                            wait_seconds,
                        )
                        time.sleep(wait_seconds)
                        continue
                    raise

                except httpx.HTTPError as exc:
                    last_error = exc
                    if attempt < self.max_retries - 1:
                        wait_seconds = 2 ** attempt
                        logger.warning("%s network error. Retrying in %s seconds: %s", source_name, wait_seconds, exc)
                        time.sleep(wait_seconds)
                        continue
                    raise

        raise RuntimeError(f"{source_name} request failed after retries: {last_error}")

    def _get_json_with_backoff(
        self,
        url: str,
        headers: dict[str, str],
        params: dict[str, object],
        source_name: str,
    ) -> dict:
        last_error: Exception | None = None

        with httpx.Client(headers=headers, timeout=self.timeout, follow_redirects=True) as client:
            for attempt in range(self.max_retries):
                try:
                    response = client.get(url, params=params)

                    if response.status_code == 429:
                        wait_seconds = 2 ** attempt
                        logger.warning("%s rate limited (429). Retrying in %s seconds.", source_name, wait_seconds)
                        time.sleep(wait_seconds)
                        continue

                    response.raise_for_status()
                    return response.json()

                except httpx.HTTPStatusError as exc:
                    last_error = exc
                    if exc.response.status_code in {429, 500, 502, 503, 504} and attempt < self.max_retries - 1:
                        wait_seconds = 2 ** attempt
                        logger.warning(
                            "%s HTTP error %s. Retrying in %s seconds.",
                            source_name,
                            exc.response.status_code,
                            wait_seconds,
                        )
                        time.sleep(wait_seconds)
                        continue
                    raise

                except httpx.HTTPError as exc:
                    last_error = exc
                    if attempt < self.max_retries - 1:
                        wait_seconds = 2 ** attempt
                        logger.warning("%s network error. Retrying in %s seconds: %s", source_name, wait_seconds, exc)
                        time.sleep(wait_seconds)
                        continue
                    raise

        raise RuntimeError(f"{source_name} request failed after retries: {last_error}")

    def _dedupe(self, papers: Iterable[Paper]) -> list[Paper]:
        seen: dict[str, Paper] = {}

        for paper in papers:
            key = (paper.doi or "").lower().strip() or re.sub(r"\W+", "", paper.title.lower())
            current = seen.get(key)

            if current is None:
                seen[key] = paper
            elif (paper.citation_count or 0) > (current.citation_count or 0):
                seen[key] = paper
            elif not current.abstract and paper.abstract:
                seen[key] = paper

        return list(seen.values())

    @staticmethod
    def _clean_text(value: str) -> str:
        value = html.unescape(value or "")
        return re.sub(r"\s+", " ", value).strip()