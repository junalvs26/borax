import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from academic_flow import AcademicFlowManager
from embedded_engine import BoraxLLM

def test_tcc_with_specific_topic():
    print("\n--- [TESTE 1/2] Validação de TCC com tema específico ('engenharia genética') ---", flush=True)
    user_query = "eu queria fazer meu tcc sobre engenharia genética"
    
    is_academic = AcademicFlowManager.is_academic_request(user_query)
    print(f" -> É solicitação acadêmica: {is_academic}", flush=True)
    assert is_academic is True, "Erro: Não reconheceu solicitação de TCC"

    topic = AcademicFlowManager.extract_academic_topic(user_query)
    print(f" -> Tema extraído com sucesso: '{topic}'", flush=True)
    assert topic and "engenharia gen" in topic.lower(), f"Erro: Falha ao extrair tema 'engenharia genética', obteve: {topic}"

    sys_prompt = AcademicFlowManager.get_academic_system_prompt(user_query)
    print(" -> System Prompt gerado especificamente para o tema:")
    print("   " + "\n   ".join(sys_prompt.split("\n")[:4]) + "\n   ...")

    llm = BoraxLLM()
    response = llm.generate_text(prompt=user_query, system_prompt=sys_prompt, max_tokens=512)

    print("\n -> Resposta da LLM para TCC de Engenharia Genética:")
    print("   " + response[:400].strip() + "\n   ...")

    resp_lower = response.lower()
    is_generic = "como posso te auxiliar hoje" in resp_lower or "como posso te ajudar hoje" in resp_lower
    print(f" -> Retornou resposta genérica robótica ('como posso te ajudar hoje'): {is_generic}", flush=True)
    assert not is_generic, "Erro: LLM respondeu com frase genérica robótica!"

    has_topic_mention = "genétic" in resp_lower or "crispr" in resp_lower or "dna" in resp_lower or "biotecnologia" in resp_lower or "engenharia" in resp_lower
    print(f" -> Mencionou o contexto do tema (Engenharia Genética / CRISPR / Biotecnologia): {has_topic_mention}", flush=True)
    assert has_topic_mention, "Erro: Resposta não abordou o tema específico de Engenharia Genética"

    print("[OK] Teste de TCC com tema específico passou com 100% de sucesso!", flush=True)

def test_tcc_without_topic():
    print("\n--- [TESTE 2/2] Validação de TCC sem tema definido ('quero fazer meu tcc') ---", flush=True)
    user_query = "quero fazer meu tcc"

    is_academic = AcademicFlowManager.is_academic_request(user_query)
    assert is_academic is True, "Erro: Não reconheceu 'quero fazer meu tcc'"

    sys_prompt = AcademicFlowManager.get_academic_system_prompt(user_query)
    llm = BoraxLLM()
    response = llm.generate_text(prompt=user_query, system_prompt=sys_prompt, max_tokens=512)

    print("\n -> Resposta da LLM para 'quero fazer meu tcc':")
    print("   " + response[:400].strip() + "\n   ...")

    resp_lower = response.lower()
    is_generic = "como posso te auxiliar hoje" in resp_lower or "como posso te ajudar hoje" in resp_lower
    assert not is_generic, "Erro: LLM respondeu com frase genérica robótica!"

    has_probing = "?" in response or "curso" in resp_lower or "área" in resp_lower or "ideias" in resp_lower or "tema" in resp_lower
    print(f" -> Orientou o usuário propondo áreas/ideias/perguntas: {has_probing}", flush=True)
    assert has_probing, "Erro: LLM não fez perguntas/sugestões de temas"

    print("[OK] Teste de TCC sem tema definido passou com 100% de sucesso!", flush=True)

def main():
    print("==================================================================", flush=True)
    print(" SUÍTE DE TESTES: CORREÇÃO DE RESPOSTAS GENÉRICAS EM TCC (BORAX) ", flush=True)
    print("==================================================================", flush=True)

    test_tcc_with_specific_topic()
    test_tcc_without_topic()

    print("\n==================================================================", flush=True)
    print(" TODOS OS TESTES DE CORREÇÃO DE RESPOSTA PASSARAM COM SUCESSO!", flush=True)
    print("==================================================================", flush=True)

if __name__ == "__main__":
    main()
