import logging
from duckduckgo_search import DDGS
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def web_search(query: str) -> str:
    """Search the web for up-to-date information, facts, or technical documentation.

    Input: A search query string (e.g. 'FastAPI lifespan events', 'HNSW algorithm Qdrant').
    Output: A concise summary of top search results with snippets and URLs.
    """
    clean_query = query.strip()
    if not clean_query:
        return "Error: Search query cannot be empty."

    try:
        results = []
        with DDGS() as ddgs:
            for item in ddgs.text(clean_query, max_results=3):
                title = item.get("title", "")
                snippet = item.get("body", "")
                url = item.get("href", "")
                results.append(f"- **{title}**: {snippet} (Source: {url})")

        if not results:
            return f"No search results found for query: '{clean_query}'."

        return "\n".join(results)
    except Exception as exc:
        logger.error("Web search failed for '%s': %s", clean_query, exc)
        return f"Error executing web search for '{clean_query}': {exc}"
