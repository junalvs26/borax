import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from academic_flow import AcademicFlowManager
from academic_writer_engine import AcademicWriterEngine
from smart_web_search import SmartWebSearch

def test_web_search_deduplication():
    print("\n--- [TESTE 1/2] Validação de Deduplicação Estrita da Busca Web (smart_web_search.py) ---", flush=True)
    searcher = SmartWebSearch(max_results=6)
    
    query = "Engenharia Genética ABNT artigos"
    raw_results = searcher.search(query, max_results=6)

    print(f" -> Resultados brutos obtidos: {len(raw_results)}", flush=True)
    assert len(raw_results) <= 3, f"Erro: A busca web deveria retornar no máximo 3 fontes distintas, retornou {len(raw_results)}"

    urls = [r["url"].lower().rstrip("/") for r in raw_results]
    titles = [r["title"].lower().strip() for r in raw_results]

    assert len(urls) == len(set(urls)), "Erro: Detectadas URLs duplicadas nos resultados da busca web"
    assert len(titles) == len(set(titles)), "Erro: Detectados Títulos duplicados nos resultados da busca web"

    formatted = searcher.format_web_context(raw_results)
    print(" -> Previa da Formatação Limpa (Dados Brutos):")
    print("   " + "\n   ".join(formatted.split("\n")[:4]) + "\n   ...")

    assert "Você pode pesquisar em" not in formatted, "Erro: Texto pré-pronto com frases repetitivas detectado"
    assert "[FONTE 1]:" in formatted or formatted == "", "Erro: Formato de dados brutos [FONTE N] ausente"
    print("[OK] Deduplicação e formatação limpa de dados brutos validadas!", flush=True)

def test_direct_tcc_generation_without_metalanguage():
    print("\n--- [TESTE 2/2] Validação de Redação Direta do TCC sem Metalinguagem Evasiva ---", flush=True)
    engine = AcademicWriterEngine()

    user_query = "gere esse tcc para mim sobre Engenharia Genética"
    
    is_academic = AcademicFlowManager.is_academic_request(user_query)
    is_compile = AcademicFlowManager.is_ready_to_compile(user_query)

    print(f" -> É solicitação acadêmica: {is_academic}", flush=True)
    print(f" -> É solicitação direta de escrita/compilação: {is_compile}", flush=True)

    assert is_academic is True, "Erro: Não reconheceu solicitação de TCC"
    assert is_compile is True, "Erro: 'gere esse tcc para mim' deveria acionar modo de escrita direta"

    turn_res = engine.process_academic_turn(user_query, messages=[], force_compile=True)
    print(f" -> Tipo de execução: {turn_res['type']}", flush=True)
    assert turn_res["type"] == "compilation", "Erro: Não executou compilação/escrita direta"

    output_text = turn_res["content"]
    print("\n -> Prévia do Texto do TCC Gerado:")
    print("   " + output_text[:500].strip() + "\n   ...")

    out_lower = output_text.lower()

    # Verify absence of evasive metalanguage / repetitive link lists
    assert "você pode pesquisar em" not in out_lower, "Erro: LLM respondeu com metalinguagem evasiva ('você pode pesquisar em...')"
    assert "aqui está um resumo do que encontrar" not in out_lower, "Erro: LLM respondeu com metalinguagem de resumo"
    assert "fontes de pesquisa online:" not in out_lower, "Erro: LLM entrou no loop 'Fontes de Pesquisa Online:'"

    # Verify structured academic sections
    has_resumo = "resumo" in out_lower
    has_intro = "introdução" in out_lower or "introducao" in out_lower
    has_desenvolvimento = "desenvolvimento" in out_lower or "fundamentação" in out_lower or "fundamentacao" in out_lower
    has_consideracoes = "considerações" in out_lower or "consideracoes" in out_lower or "conclusão" in out_lower or "conclusao" in out_lower

    print(f" - Contém Resumo: {has_resumo}", flush=True)
    print(f" - Contém Introdução: {has_intro}", flush=True)
    print(f" - Contém Desenvolvimento: {has_desenvolvimento}", flush=True)
    print(f" - Contém Considerações Finais: {has_consideracoes}", flush=True)

    assert has_intro and has_desenvolvimento, "Erro: O texto do TCC gerado não contém as seções estruturais obrigatórias"
    assert os.path.exists(turn_res["docx_path"]), "Erro: Arquivo .docx não foi compilado"

    print("[OK] Redação direta do TCC ABNT sem metalinguagem e compilação Word validadas!", flush=True)

def main():
    print("==================================================================", flush=True)
    print(" SUÍTE DE TESTES: BUSCA WEB LIMPA & GERADOR DE TCC DIRETO (BORAX) ", flush=True)
    print("==================================================================", flush=True)

    test_web_search_deduplication()
    test_direct_tcc_generation_without_metalanguage()

    print("\n==================================================================", flush=True)
    print(" TODOS OS TESTES PASSARAM COM SUCESSO!", flush=True)
    print("==================================================================", flush=True)

if __name__ == "__main__":
    main()
