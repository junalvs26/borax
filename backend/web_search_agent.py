import os
import sys
from typing import List, Dict, Any, Optional

from search_trigger import should_search_web
from smart_web_search import SmartWebSearch

class WebSearchAgent:
    """
    Agente de Pesquisa Web Ativa para Trabalhos Acadêmicos, TCCs e Pesquisas.
    Unifica o detector de intenções com o motor de busca DuckDuckGo / DDGS.
    """
    def __init__(self, max_results: int = 4):
        self.searcher = SmartWebSearch(max_results=max_results)

    def should_search(
        self,
        query: str,
        history: Optional[List[Dict[str, Any]]] = None,
        has_local_answer: bool = False
    ) -> bool:
        """Determina se a consulta necessita de pesquisa ativa na web."""
        return should_search_web(
            user_message=query,
            history=history,
            active_cds_has_answer=has_local_answer
        )

    def search_references(self, query: str, max_results: int = 4) -> Dict[str, Any]:
        """
        Executa busca ativa por referências, legislações e artigos acadêmicos atuais.
        """
        results = self.searcher.search(query, max_results=max_results)
        if not results:
            return {
                "has_results": False,
                "formatted_context": "",
                "raw_results": []
            }

        formatted = self.searcher.format_web_context(results)
        return {
            "has_results": True,
            "formatted_context": formatted,
            "raw_results": results
        }
