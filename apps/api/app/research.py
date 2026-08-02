import asyncio

import httpx

from .config import Settings
from .models import Source
from .safety import validate_public_url

MOCK_SOURCES = [
    Source(
        title="NIST AI Risk Management Framework",
        url="https://www.nist.gov/itl/ai-risk-management-framework",
        excerpt="The AI RMF helps organizations govern, map, measure, and manage AI risks.",
    ),
    Source(
        title="OECD AI Principles",
        url="https://oecd.ai/en/ai-principles",
        excerpt="Accountability, transparency, robustness, security, and human-centered values guide trustworthy AI.",
    ),
    Source(
        title="EU AI Act overview",
        url="https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai",
        excerpt="The risk-based framework establishes obligations based on the potential harm of AI systems.",
    ),
]


async def _retry(coro_factory, attempts: int = 3):
    error = None
    for i in range(attempts):
        try:
            return await coro_factory()
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            error = exc
            if i + 1 < attempts:
                await asyncio.sleep(0.1 * (2**i))
    raise RuntimeError("Research provider unavailable after bounded retries") from error


async def search(query: str, settings: Settings) -> list[Source]:
    if settings.agent_mode != "live":
        return MOCK_SOURCES
    if not settings.tavily_api_key:
        raise ValueError("TAVILY_API_KEY is required in live mode")

    async def call():
        async with httpx.AsyncClient(timeout=12) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.tavily_api_key,
                    "query": query,
                    "max_results": 5,
                    "search_depth": "advanced",
                },
            )
            response.raise_for_status()
            data = response.json()
            return [
                Source(
                    title=r.get("title", "Untitled"),
                    url=validate_public_url(r["url"]),
                    excerpt=r.get("content", "")[:600],
                )
                for r in data.get("results", [])
            ]

    return await _retry(call)


def summarize(sources: list[Source]) -> str:
    if not sources:
        return "No reliable public sources were available, so the agent stopped without proposing an action."
    return "The research identifies governance, accountability, transparency, security, and risk-based oversight as recurring requirements. Organizations should inventory AI systems, assign accountable owners, test material risks, document decisions, and maintain human review for consequential use cases."
