import re
from typing import List, Dict, Any, Optional

class SmartWebSearch:
    """
    Agente de Pesquisa Web Autônoma para o BORAX.
    Utiliza duckduckgo_search com suporte a formatação de contextos e citações.
    """
    def __init__(self, max_results: int = 4):
        self.max_results = max_results

    def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """Perform active web search using DuckDuckGo text engine."""
        num_results = max_results or self.max_results
        cleaned_query = re.sub(r'[^\w\s-]', '', query).strip()
        if not cleaned_query:
            cleaned_query = query

        results = []
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                ddg_gen = ddgs.text(cleaned_query, region="pt-br", max_results=num_results)
                for item in ddg_gen:
                    title = item.get("title") or "Fonte Web"
                    snippet = item.get("body") or item.get("snippet") or ""
                    url = item.get("href") or item.get("link") or ""
                    if url and snippet:
                        results.append({
                            "title": title.strip(),
                            "snippet": snippet.strip(),
                            "url": url.strip()
                        })
        except Exception as e:
            print(f"[SmartWebSearch Error] Falha na busca DuckDuckGo: {e}")

        if not results:
            print(f"[SmartWebSearch] Nenhuma fonte externa encontrada para: '{query}'")
            return []

        # Deduplicação estrita por URL e Título
        seen_urls = set()
        seen_titles = set()
        deduped = []
        for r in results:
            url_norm = r["url"].lower().rstrip("/")
            title_norm = r["title"].lower().strip()
            if url_norm not in seen_urls and title_norm not in seen_titles:
                seen_urls.add(url_norm)
                seen_titles.add(title_norm)
                deduped.append(r)

        return deduped[:min(3, num_results)]

    @staticmethod
    def format_web_context(results: List[Dict[str, str]]) -> str:
        """Format web search results into a clean raw data context block without repetitive pre-made text."""
        if not results:
            return ""

        lines = ["--- DADOS BRUTOS DA PESQUISA WEB (FONTES REAIS) ---"]
        for idx, res in enumerate(results[:3], 1):
            snippet_clean = res['snippet'].replace("\n", " ").strip()
            lines.append(f"[FONTE {idx}]: {res['title']} | {snippet_clean} | URL: {res['url']}")

        lines.append("\nInstrução: Utilize estas informações brutas apenas como fundamentação científica e citação. Não repita listas de links no corpo do texto.")
        return "\n".join(lines)
