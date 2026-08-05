import re
from typing import List, Dict, Any, Optional

ACADEMIC_DOC_PATTERNS = [
    r'\b(tcc|monografia|dissertação|dissertacao|tese|artigo\s+científico|artigo\s+cientifico|trabalho\s+acadêmico|trabalho\s+academico|projeto\s+pibic|pibic|relatório\s+acadêmico|relatorio\s+academico)\b',
    r'\b(abnt|normas\s+abnt|pesquisa\s+científica|pesquisa\s+cientifica|fundamentação\s+teórica|fundamentacao\s+teorica)\b',
    r'^\s*(quero|gostaria|preciso|crie|gere|monte|faça|faca)\s+(um|uma|meu|minha)?\s*(tcc|artigo|monografia|projeto|trabalho|relatório|relatorio)'
]

COMPILE_PATTERNS = [
    r'\b(compil|gerar\s+arquivo|gerar\s+o\s+docx|baixar|exportar|gerar\s+o\s+texto\s+completo|gerar\s+o\s+documento|aprovado|pode\s+gerar|pode\s+compilar|faça\s+o\s+docx|gere\s+esse\s+tcc|faça\s+esse\s+tcc|escreva\s+o\s+tcc|gerar\s+tcc|crie\s+o\s+tcc)\b'
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
    def extract_academic_topic(user_message: str) -> Optional[str]:
        """Extrai o tema da pesquisa se presente (ex: 'sobre engenharia genética')."""
        if not user_message:
            return None
        match = re.search(r'\b(sobre|em|de|com\s+foco\s+em|focado\s+em)\s+([\w\s]{3,50})', user_message, re.IGNORECASE)
        if match:
            topic = match.group(2).strip()
            topic = re.sub(r'[^\w\s]', '', topic)
            if len(topic) >= 3 and topic.lower() not in ["meu tcc", "meu trabalho", "minha tese", "um artigo", "meu artigo"]:
                return topic
        return None

    @classmethod
    def get_academic_system_prompt(cls, user_message: str) -> str:
        """Retorna o System Prompt dinâmico de Orientador de Doutorado ajustado ao tema do usuário."""
        topic = cls.extract_academic_topic(user_message)
        if topic:
            return (
                f"Você é um Pesquisador e Orientador Acadêmico de Doutorado da Plataforma BORAX.\n"
                f"O usuário quer desenvolver um TCC/trabalho acadêmico sobre o tema: {topic.upper()}.\n\n"
                f"ESTRUTURA DA SUA RESPOSTA (SIGA RIGOROSAMENTE):\n"
                f"1. Acolhimento e Relevância: Apresente-se como Orientador Acadêmico de Doutorado e comente sucintamente o impacto científico de {topic}.\n"
                f"2. Abordagens Temáticas: Sugira 3 recortes de pesquisa instigantes sobre {topic}.\n"
                f"3. Sumário Preliminar: Proponha uma estrutura inicial em capítulos formais ABNT.\n"
                f"4. Pergunta de Condução: Faça 2 perguntas diretas para o usuário definir o rumo da investigação."
            )
        else:
            return (
                "Você é um Pesquisador e Orientador Acadêmico de Doutorado da Plataforma BORAX.\n"
                "O usuário solicitou apoio para elaborar um TCC/trabalho acadêmico, mas ainda não informou o tema exato.\n\n"
                "ESTRUTURA DA SUA RESPOSTA (SIGA RIGOROSAMENTE):\n"
                "1. Acolhimento: 'Excelente! Como seu Orientador Acadêmico de Doutorado, estou aqui para te conduzir do zero até a aprovação do seu TCC.'\n"
                "2. Diagnóstico: Pergunte a área ou curso de estudo dele (ex: Saúde, Direito, Tecnologia, Engenharia, Humanas).\n"
                "3. Sugestões de Temas: Apresente 3 ideias de temas científicos em alta para ele escolher.\n"
                "4. Metodologia: Pergunte se prefere revisão bibliográfica, estudo de caso ou aplicação prática."
            )
