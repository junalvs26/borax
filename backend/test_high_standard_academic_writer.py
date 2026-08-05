import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from academic_flow import AcademicFlowManager
from academic_writer_engine import AcademicWriterEngine
from web_search_agent import WebSearchAgent

def test_dynamic_consultative_flow():
    print("\n--- [TESTE 1/3] Validação de Sondagem Consultiva Dinâmica (Não Engessada) ---", flush=True)
    engine = AcademicWriterEngine()
    
    query = "Quero fazer um TCC de Inteligência Artificial no diagnóstico de imagens médicas"
    res = engine.process_academic_turn(query, messages=[], force_compile=False)

    print(" -> Resposta da LLM para o tema de IA médica:")
    print("   " + res["content"][:400].strip() + "\n   ...")

    content_lower = res["content"].lower()
    has_medical_context = "médic" in content_lower or "imagem" in content_lower or "diagnóstico" in content_lower or "saúde" in content_lower or "medicina" in content_lower
    has_probing_questions = "?" in res["content"] or "problema" in content_lower or "abordagem" in content_lower

    print(f" - Contextualizou sobre a área específica (Saúde/Medicina): {has_medical_context}", flush=True)
    print(f" - Formulou perguntas/orientação dinâmica: {has_probing_questions}", flush=True)

    assert has_probing_questions, "Erro: Assistente não formulou perguntas consultivas dinâmicas"
    print("[OK] Sondagem consultiva dinâmica e não engessada validada!", flush=True)

def test_web_search_references_injection():
    print("\n--- [TESTE 2/3] Validação de Pesquisa Web de Referências Científicas Reais ---", flush=True)
    agent = WebSearchAgent()
    
    query = "pesquisar artigos científicos ABNT sobre IA em diagnósticos radiológicos"
    search_res = agent.search_references(query, max_results=3)

    print(f" -> Encontrou referências web ativas: {search_res['has_results']}", flush=True)
    assert search_res["has_results"] is True, "Erro: Agente não retornou referências da web"
    
    formatted = search_res["formatted_context"]
    print(" -> Previa das Referências Reais Encontradas:")
    print("   " + "\n   ".join(formatted.split("\n")[:5]) + "\n   ...")

    assert "📌 **Fontes e Referências Consultadas:**" in formatted
    print("[OK] Busca de referências reais e injeção acadêmica validadas!", flush=True)

def test_high_standard_abnt_compilation():
    print("\n--- [TESTE 3/3] Validação de Redação PhD & Compilação Final ABNT ---", flush=True)
    engine = AcademicWriterEngine()
    
    query = "Compilar TCC sobre Inteligência Artificial no Diagnóstico de Imagens Médicas em formato ABNT"
    res = engine.process_academic_turn(query, messages=[], force_compile=True)

    print(f" -> Tipo de retorno: {res['type']}", flush=True)
    assert res["type"] == "compilation", "Erro: O motor não executou a compilação final"

    markdown_text = res["content"]
    docx_path = res["docx_path"]

    print("\n--- PRÉVIA DO TEXTO ACADÊMICO PhD GERADO ---", flush=True)
    print(markdown_text[:600] + "\n...", flush=True)

    print(f"\n -> Arquivo Word (.docx) gerado em: {docx_path}", flush=True)
    assert os.path.exists(docx_path), "Erro: Arquivo .docx não foi criado"
    assert os.path.getsize(docx_path) > 3000, "Erro: Arquivo .docx gerado está muito pequeno ou corrompido"

    # Verify absence of RAG tags leakage or generic templates
    assert "[CONTEXTO" not in markdown_text, "Erro: Tag interna RAG vazou no texto final"
    assert "Instituto Brasileiro de Pesquisa Econômica" not in markdown_text, "Erro: Texto mock hardcoded detectado"

    print("[OK] Redação científica sênior e compilação ABNT validadas com sucesso!", flush=True)

def main():
    print("==================================================================", flush=True)
    print("   SUÍTE DE TESTES: REDAÇÃO ACADÊMICA DE ALTO PADRÃO ABNT (BORAX)", flush=True)
    print("==================================================================", flush=True)
    
    test_dynamic_consultative_flow()
    test_web_search_references_injection()
    test_high_standard_abnt_compilation()

    print("\n==================================================================", flush=True)
    print(" TODOS OS 3 TESTES DE REDAÇÃO CIENTÍFICA PASSARAM COM SUCESSO!", flush=True)
    print("==================================================================", flush=True)

if __name__ == "__main__":
    main()
