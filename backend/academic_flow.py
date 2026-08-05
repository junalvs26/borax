import re
from typing import List, Dict, Any, Optional

ACADEMIC_DOC_PATTERNS = [
    r'\b(tcc|monografia|dissertação|dissertacao|tese|artigo\s+científico|artigo\s+cientifico|trabalho\s+acadêmico|trabalho\s+academico|projeto\s+pibic|pibic|relatório\s+acadêmico|relatorio\s+academico)\b',
    r'\b(abnt|normas\s+abnt|pesquisa\s+científica|pesquisa\s+cientifica|fundamentação\s+teórica|fundamentacao\s+teorica)\b',
    r'^\s*(quero|gostaria|preciso|crie|gere|monte|faça|faca)\s+(um|uma|meu|minha)?\s*(tcc|artigo|monografia|projeto|trabalho|relatório|relatorio)'
]

COMPILE_PATTERNS = [
    r'\b(compil|gerar\s+arquivo|gerar\s+o\s+docx|baixar|exportar|gerar\s+o\s+texto\s+completo|gerar\s+o\s+documento|aprovado|pode\s+gerar|pode\s+compilar|faça\s+o\s+docx)\b'
]

class AcademicFlowManager:
    """
    Gerenciador do Fluxo Consultivo Acadêmico Dinâmico (Não Engessado).
    Conduz o usuário de forma fluida como um Orientador Acadêmico de Doutorado.
    """
    @staticmethod
    def is_academic_request(user_message: str) -> bool:
        """Verifica se a solicitação é de um trabalho acadêmico ou científico."""
        if not user_message:
            return False
        msg_clean = user_message.lower().strip()
        return any(re.search(pattern, msg_clean) for pattern in ACADEMIC_DOC_PATTERNS)

    @staticmethod
    def is_ready_to_compile(user_message: str, history: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Verifica se o usuário solicitou explicitamente a compilação/download do arquivo final."""
        if not user_message:
            return False
        msg_clean = user_message.lower().strip()
        return any(re.search(pattern, msg_clean) for pattern in COMPILE_PATTERNS)

    @staticmethod
    def get_dynamic_consultative_instruction(user_message: str) -> str:
        """
        Gera instrução dinâmica para a LLM atuar como Orientador de Doutorado sem usar questionários rígidos.
        """
        return (
            "INSTRUÇÃO CONSULTIVA DINÂMICA:\n"
            "O usuário está desenvolvendo um trabalho acadêmico. Como Orientador de Doutorado:\n"
            "1. Acolha a ideia do usuário e faça uma análise acadêmica inicial do tema proposto.\n"
            "2. Faça de 1 a 3 perguntas inteligentes, fluídas e contextualizadas específicas para o tema dele (evite questionários engessados) para ajudar a delimitar o problema de pesquisa, a metodologia e o referencial teórico.\n"
            "3. Apresente uma proposta de sumário/estrutura inicial para ele avaliar."
        )
