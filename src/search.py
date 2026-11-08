"""Tavily search restricted to reputable health sources."""
from src.config import get_secret
from src.schemas import Source

NUTRITION_DOMAINS = ["who.int", "cdc.gov", "nhs.uk", "dietaryguidelines.gov", "myplate.gov", "eatright.org",
                     "health.harvard.edu", "hsph.harvard.edu", "mayoclinic.org", "heart.org", "nih.gov",
                     "medlineplus.gov", "nutrition.gov", "clevelandclinic.org"]
FITNESS_DOMAINS = ["who.int", "cdc.gov", "nhs.uk", "health.gov", "heart.org", "mayoclinic.org", "acsm.org",
                   "health.harvard.edu", "nih.gov", "medlineplus.gov", "hopkinsmedicine.org", "clevelandclinic.org"]


class SearchError(Exception):
    """Raised when sources cannot be retrieved."""


def _search(query: str, domains: list[str], max_results: int) -> list[dict]:
    key = get_secret("TAVILY_API_KEY")
    if not key:
        raise SearchError("TAVILY_API_KEY is not set (add it to the .env file).")
    try:
        from tavily import TavilyClient
        resp = TavilyClient(api_key=key).search(
            query=query, search_depth="basic", max_results=max_results, include_domains=domains)
    except Exception as e:  # noqa: BLE001 - network, auth, quota...
        raise SearchError(f"Could not search for sources: {e}") from e
    return resp.get("results", [])


def gather_sources(queries: list[str], domains: list[str], per_query: int = 3, cap: int = 7):
    """Run several searches, dedupe by URL, and return (Source list, id -> snippet text)."""
    seen, sources, snippets = set(), [], {}
    for q in queries:
        for r in _search(q, domains, per_query):
            url, content = r.get("url"), (r.get("content") or "").strip()
            if not url or url in seen or not content:
                continue
            seen.add(url)
            sid = len(sources) + 1
            sources.append(Source(id=sid, title=(r.get("title") or url)[:140], url=url))
            snippets[sid] = content[:600]
            if len(sources) >= cap:
                return sources, snippets
    if not sources:
        raise SearchError("No reliable sources were found for this request. Please try again shortly.")
    return sources, snippets


def format_sources(sources, snippets) -> str:
    return "\n\n".join(f"[{s.id}] {s.title} ({s.url})\n{snippets[s.id]}" for s in sources)
