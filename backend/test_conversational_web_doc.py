import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_search_agent import WebSearchAgent
from embedded_engine import BoraxLLM, DEFAULT_SCIENTIFIC_SYSTEM_PROMPT
from artifact_engine import ArtifactEngine

def test_conversational_probing():
    print("\n--- [TESTE 1/3] Validação da Sondagem Consultiva (Orientador Acadêmico) ---", flush=True)
    llm = BoraxLLM()
    
    user_query = "Quero fazer meu TCC de inteligência artificial na educação"
    output = llm.generate_text(
        prompt=user_query,
        system_prompt=DEFAULT_SCIENTIFIC_SYSTEM_PROMPT,
        max_tokens=256
    )

    print(" -> Resposta da LLM para solicitação de TCC:")
    print("   " + output[:300].strip() + "...")

    output_lower = output.lower()
    has_probing = "tema" in output_lower or "ideias" in output_lower or "problema" in output_lower or "pesquisa" in output_lower or "?" in output
    print(f" -> Realizou sondagem / pergunta consultiva ao usuário: {has_probing}", flush=True)
    assert has_probing, "Erro: Assistente não atuou como Orientador Acadêmico Consultivo"
    print("[OK] Sondagem e postura de Orientador Acadêmico validadas!", flush=True)

def test_web_search_agent_execution():
    print("\n--- [TESTE 2/3] Validação de Busca Ativa por Referências Acadêmicas (web_search_agent.py) ---", flush=True)
    agent = WebSearchAgent(max_results=3)

    query = "pesquisar artigos recentes sobre inteligência artificial na educação ABNT"
    should = agent.should_search(query, history=[], has_local_answer=False)
    print(f" -> Consulta: '{query}' -> Deve Buscar: {should}", flush=True)
    assert should is True, "Erro: Agente deveria acionar a busca web"

    search_res = agent.search_references(query, max_results=3)
    print(f" -> Resultados encontrados: {search_res['has_results']}", flush=True)
    assert search_res["has_results"] is True, "Erro: Agente não retornou resultados da web"

    formatted = search_res["formatted_context"]
    print(" -> Previa do Contexto Formatado:")
    print("   " + "\n   ".join(formatted.split("\n")[:4]) + "\n   ...")

    assert "[CONTEXTO DA PESQUISA WEB AUTÔNOMA" in formatted
    print("[OK] Agente de Busca Web Ativa e referências validados!", flush=True)

def test_abnt_docx_compilation():
    print("\n--- [TESTE 3/3] Validação de Compilação Final ABNT via ArtifactEngine ---", flush=True)
    engine = ArtifactEngine()
    
    mock_tcc_markdown = """# TCC: O Impacto da Inteligência Artificial na Educação Básica

## Resumo
Este Trabalho de Conclusão de Curso analisa a aplicação de ferramentas de IA no ensino fundamental.

## 1. Introdução e Justificativa
A tecnologia digital transformou os métodos de aprendizagem contemporâneos...

## 2. Objetivos
- **Objetivo Geral:** Avaliar o impacto das IAs generativas no desempenho escolar.
- **Objetivos Específicos:** Mapear ferramentas de IA; Analisar percepção de professores.

## 3. Metodologia
Pesquisa de campo quanti-qualitativa com aplicação de questionários estruturados.

## 📌 **Fontes e Referências Consultadas:**
- [Portal da Educação](https://www.gov.br/mec)
- [Revista Brasileira de Informática na Educação](https://sbie.org.br)
"""

    docx_path = engine.compile_docx(mock_tcc_markdown, title="TCC - IA na Educação ABNT")
    print(f" -> Documento .docx ABNT gerado com sucesso: {docx_path}", flush=True)
    assert os.path.exists(docx_path), "Erro: Arquivo .docx ABNT não foi criado"
    assert os.path.getsize(docx_path) > 3000, "Erro: Arquivo .docx gerado está muito pequeno ou corrompido"
    print("[OK] Compilação .docx ABNT rigorosa validada com sucesso!", flush=True)

def main():
    print("==================================================================", flush=True)
    print("   SUÍTE DE TESTES: FLUXO CONVERSACIONAL & BUSCA WEB DE DOCS (BORAX)", flush=True)
    print("==================================================================", flush=True)
    
    test_conversational_probing()
    test_web_search_agent_execution()
    test_abnt_docx_compilation()

    print("\n==================================================================", flush=True)
    print(" TODOS OS 3 TESTES DE CONVERSAÇÃO E BUSCA WEB PASSARAM COM SUCESSO!", flush=True)
    print("==================================================================", flush=True)

if __name__ == "__main__":
    main()
