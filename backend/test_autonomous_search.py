import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from search_trigger import should_search_web
from smart_web_search import SmartWebSearch

def test_search_trigger_rules():
    print("\n--- [TESTE 1/3] Validação das Regras do Detector de Intenção (search_trigger.py) ---", flush=True)

    # 1. Perguntas que NÃO devem acionar a busca na web
    no_search_cases = [
        "Corrija o texto a seguir: O projeto visa desenvolver novas abordagens.",
        "Reescreva este parágrafo em tom formal.",
        "Melhore a pontuação e gramática da frase.",
        "Qual é a fórmula de soma no Excel?"
    ]

    for msg in no_search_cases:
        res = should_search_web(msg, history=[], active_cds_has_answer=True)
        print(f" -> '{msg[:45]}...' -> Aciona Busca: {res}", flush=True)
        assert res is False, f"Erro: Mensagem '{msg}' não deveria acionar a busca web"

    # 2. Perguntas que DEVEM acionar a busca na web
    must_search_cases = [
        "Quais os avanços mais recentes na legislação de biossegurança no Brasil?",
        "Pesquise sobre as normas atualizadas da ABNT para projetos PIBIC.",
        "Quais são os dados e estatísticas mais recentes do IBGE?",
        "Busque na internet sobre a portaria mais recente do CNPq."
    ]

    for msg in must_search_cases:
        res = should_search_web(msg, history=[], active_cds_has_answer=False)
        print(f" -> '{msg[:45]}...' -> Aciona Busca: {res}", flush=True)
        assert res is True, f"Erro: Mensagem '{msg}' DEVERIA acionar a busca web"

    print("[OK] Regras de acionamento do detector de busca validadas com sucesso!", flush=True)

def test_smart_web_search_execution():
    print("\n--- [TESTE 2/3] Validação do Motor de Pesquisa Web (smart_web_search.py) ---", flush=True)
    searcher = SmartWebSearch(max_results=3)
    
    query = "legislação de biossegurança Brasil"
    print(f" -> Executando busca real no DuckDuckGo para: '{query}'...", flush=True)
    
    results = searcher.search(query, max_results=3)
    print(f" -> Total de resultados retornados: {len(results)}", flush=True)
    assert len(results) > 0, "Nenhum resultado retornado na busca web"

    first_item = results[0]
    print(f" -> Primeiro Resultado:")
    print(f"    - Título: {first_item.get('title')}")
    print(f"    - URL: {first_item.get('url')}")
    print(f"    - Trecho: {first_item.get('snippet')[:100]}...")

    assert "url" in first_item and first_item["url"].startswith("http"), "Resultado com URL inválida"
    print("[OK] Execução e extração da busca web validadas!", flush=True)

def test_formatted_context_and_citations():
    print("\n--- [TESTE 3/3] Validação de Formatação de Contexto e Seção de Fontes ---", flush=True)
    searcher = SmartWebSearch()
    mock_results = [
        {"title": "Lei de Biossegurança Nº 11.105", "url": "https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2005/lei/l11105.htm", "snippet": "Regulamenta os incisos II, IV e V do art. 225 da Constituição Federal..."},
        {"title": "CNBio - Comissão Nacional de Biossegurança", "url": "https://www.gov.br/mcti/pt-br/ctnbio", "snippet": "Normas e pareceres técnicos sobre OGM e biotecnologia."}
    ]

    formatted_context = searcher.format_web_context(mock_results)
    print(" -> Previa do Contexto Web Injetado:")
    print("   " + "\n   ".join(formatted_context.split("\n")[:6]) + "\n   ...")

    assert "[CONTEXTO DA PESQUISA WEB AUTÔNOMA" in formatted_context
    assert "📌 **Fontes e Referências Consultadas:**" in formatted_context
    assert "https://www.planalto.gov.br" in formatted_context
    print("[OK] Formatação de contexto web e instruções de citação validadas!", flush=True)

def main():
    print("==================================================================", flush=True)
    print("   SUÍTE DE TESTES: PESQUISA WEB AUTÔNOMA POR INTENÇÃO (BORAX)", flush=True)
    print("==================================================================", flush=True)
    
    test_search_trigger_rules()
    test_smart_web_search_execution()
    test_formatted_context_and_citations()

    print("\n==================================================================", flush=True)
    print(" TODOS OS 3 TESTES DE PESQUISA WEB AUTÔNOMA PASSARAM COM SUCESSO!", flush=True)
    print("==================================================================", flush=True)

if __name__ == "__main__":
    main()
