from __future__ import annotations

from pathlib import Path
from re import findall

from app.config import get_settings


DEFAULT_DOCUMENTS = {
    "service_guidelines.md": """# Civic Service Response Guidelines
Prioritize wards with high complaint growth, repeated utility outages, emergency incident load, and delayed waste collection. Escalate cross-agency coordination when two or more service domains show high risk in the same ward.
""",
    "public_health_policy.md": """# Public Health and Air Quality Guidance
When AQI is high, city teams should inspect pollution sources, communicate health advisories, and prioritize vulnerable residents for outreach. Forecasts are estimates and should support, not replace, expert judgment.
""",
    "responsible_ai.md": """# Responsible AI Use
CivicIQ recommendations are decision support only. Do not make final emergency decisions automatically. Explain data used, include limitations, avoid demographic bias, and use vulnerable population signals only to improve service prioritization.
""",
}


def ensure_knowledge_base() -> None:
    knowledge_base_dir = get_settings().knowledge_base_dir
    knowledge_base_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in DEFAULT_DOCUMENTS.items():
        path = knowledge_base_dir / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def retrieve_context(question: str, limit: int = 4) -> list[dict[str, str]]:
    ensure_knowledge_base()
    query_terms = set(_tokenize(question))
    chunks = _load_chunks(get_settings().knowledge_base_dir)
    scored_chunks = []

    for chunk in chunks:
        chunk_terms = set(_tokenize(chunk["content"]))
        score = len(query_terms.intersection(chunk_terms))
        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored_chunks[:limit]]


def _load_chunks(knowledge_base_dir: Path) -> list[dict[str, str]]:
    chunks = []
    for path in sorted(knowledge_base_dir.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        paragraphs = [paragraph.strip() for paragraph in content.split("\n\n") if paragraph.strip()]
        for index, paragraph in enumerate(paragraphs, start=1):
            chunks.append(
                {
                    "source": path.name,
                    "chunk_id": f"{path.stem}-{index}",
                    "content": paragraph,
                }
            )
    return chunks


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in findall(r"[A-Za-z][A-Za-z0-9_]+", text)]
