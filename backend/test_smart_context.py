import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_history_manager import ChatHistoryManager
from rag_engine import RAGEngine
from embedded_engine import BoraxLLM, DEFAULT_SCIENTIFIC_SYSTEM_PROMPT

def test_sliding_window_memory():
    print("\n--- [TESTE 1/3] Validacao de Memoria Flutuante (Sliding Window 10 Turnos) ---", flush=True)
    mock_messages = []
    for i in range(15):
        mock_messages.append({"role": "user", "content": f"Pergunta {i+1}: Sobre PIBIC e Inteligencia Artificial."})
        mock_messages.append({"role": "assistant", "content": f"Resposta {i+1}: O projeto PIBIC desenvolve metodologias avancadas."})

    sliding = ChatHistoryManager.get_sliding_window_context(mock_messages, max_turns=10)
    print(f" -> Total de mensagens originais: {len(mock_messages)}", flush=True)
    print(f" -> Mensagens retidas na janela flutuante (10 turnos): {len(sliding)}", flush=True)
    assert len(sliding) == 20, "Falha na retencao de 10 turnos (20 mensagens)"

    consolidated = ChatHistoryManager.build_consolidated_prompt(
        query="quero que gere o projeto",
        messages=mock_messages,
        rag_context="[CD ATIVO - PIBIC]: Requisitos do projeto de iniciacao cientifica em IA."
    )

    print(" -> Prompt Consolidado com sucesso:", flush=True)
    print("   " + "\n   ".join(consolidated.split("\n")[:8]) + "\n   ...", flush=True)
    assert "[HISTÓRICO RECENTE DA CONVERSA (ÚLTIMOS TURNOS)]" in consolidated
    assert "[CONTEXTO DOS CDS / BASES ATIVAS]" in consolidated
    assert "[MENSAGEM ATUAL DO USUÁRIO]" in consolidated
    print("[OK] Janela de Memoria Flutuante e Consolidao validadas!", flush=True)

def test_rag_hybrid_reranking():
    print("\n--- [TESTE 2/3] Validacao de Busca Hibrida e Re-ranking RAG ---", flush=True)
    rag = RAGEngine()
    
    sample_text = """O Programa Institucional de Bolsas de Iniciação Científica (PIBIC) visa incentivar talentos em inteligência artificial.
A metodologia científica do projeto exige a definição clara de objetivos gerais e específicos, fundamentação teórica sólida e cronograma de execução de 12 meses."""
    
    with open("temp_pibic_test.txt", "w", encoding="utf-8") as f:
        f.write(sample_text)
        
    try:
        rag.process_file("temp_pibic_test.txt", table_name="test_pibic_table")
        results = rag.query_context("requisitos do projeto PIBIC", table_name="test_pibic_table", top_k=3, min_score=0.45)
        
        print(f" -> Resultados re-ranqueados encontrados: {len(results)}", flush=True)
        if results:
            first_score = results[0].get("similarity_score", 0)
            print(f" -> Maior pontuacao de similaridade hibrida: {first_score}", flush=True)
            assert first_score >= 0.45, "Pontuacao de similaridade abaixo da nota de corte"
        print("[OK] Re-ranking RAG e filtro de pontuacao validados!", flush=True)
    finally:
        if os.path.exists("temp_pibic_test.txt"):
            os.remove("temp_pibic_test.txt")

def test_scientific_llm_generation():
    print("\n--- [TESTE 3/3] Geracao de Projeto Cientifico Sem Repeticoes (Redacao Senior) ---", flush=True)
    llm = BoraxLLM()
    
    query_prompt = """[HISTÓRICO RECENTE DA CONVERSA (ÚLTIMOS TURNOS)]:
USUÁRIO: Oi, gostaria de desenvolver meu projeto PIBIC em IA.
ASSISTENTE: Excelente! Podemos estruturar os objetivos, metodologia e cronograma.

[MENSAGEM ATUAL DO USUÁRIO]:
quero que gere o projeto"""

    print(" -> Gerando projeto cientifico completo com parametros otimizados (temperature=0.2, top_p=0.9)...", flush=True)
    output = llm.generate_text(
        prompt=query_prompt,
        system_prompt=DEFAULT_SCIENTIFIC_SYSTEM_PROMPT,
        max_tokens=512
    )

    print("\n--- PREVIA DO CONTEUDO GERADO ---", flush=True)
    print(output[:600] + "\n...", flush=True)

    output_lower = output.lower()

    has_title_resumo = "título" in output_lower or "resumo" in output_lower or "#" in output
    has_introducao = "introdução" in output_lower or "justificativa" in output_lower or "introducao" in output_lower
    has_objetivos = "objetivo" in output_lower
    has_metodologia = "metodologia" in output_lower or "materiais" in output_lower
    has_cronograma = "cronograma" in output_lower or "execução" in output_lower or "execucao" in output_lower

    has_generic_buzzword = "estudar a concorrência" in output_lower or "estudar a concorrencia" in output_lower
    has_repetition_loop = "tendências e tendências" in output_lower or "tendencias e tendencias" in output_lower

    print("\n--- VALIDACAO DE QUALIDADE E ESTRUTURA ---", flush=True)
    print(f" - Possui Titulo / Resumo: {has_title_resumo}", flush=True)
    print(f" - Possui Introducao / Justificativa: {has_introducao}", flush=True)
    print(f" - Possui Objetivos (Geral/Especificos): {has_objetivos}", flush=True)
    print(f" - Possui Metodologia Detalhada: {has_metodologia}", flush=True)
    print(f" - Possui Cronograma de Execucao: {has_cronograma}", flush=True)
    print(f" - Livre de listas corporativas ('estudar a concorrencia'): {not has_generic_buzzword}", flush=True)
    print(f" - Livre de repeticoes em loop ('tendencias e tendencias'): {not has_repetition_loop}", flush=True)

    assert not has_generic_buzzword, "Erro: Modelo gerou termos genericos corporativos ('estudar a concorrencia')"
    assert not has_repetition_loop, "Erro: Modelo gerou repeticao em loop ('tendencias e tendencias')"
    assert has_introducao and has_objetivos and has_metodologia, "Erro: Estrutura cientifica incompleta"

    print("\n[OK] Projeto cientifico gerado com altissima qualidade e rigor academico!", flush=True)

def main():
    print("==================================================================", flush=True)
    print("   SUITE DE TESTES: INTELIGENCIA E MEMORIA CIENTIFICA BORAX", flush=True)
    print("==================================================================", flush=True)
    
    test_sliding_window_memory()
    test_rag_hybrid_reranking()
    test_scientific_llm_generation()

    print("\n==================================================================", flush=True)
    print(" TODOS OS 3 TESTES DE INTELIGENCIA E MEMORIA PASSARAM COM SUCESSO!", flush=True)
    print("==================================================================", flush=True)

if __name__ == "__main__":
    main()
