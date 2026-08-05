import re
from typing import List, Dict, Any, Optional

EXPLICIT_SEARCH_PATTERNS = [
    r'\b(pesquis|busqu|procur|busc|consult|find|search)\w*\b',
    r'\b(internet|web|online|google|duckduckgo|site|fonte|fontes|referência|referencias|citação|citacao|citações|citacoes)\b',
    r'\b(dados\s+recentes|últimas\s+notícias|ultimas\s+noticias|avanços\s+recentes|avancos\s+recentes|estudos\s+recentes)\b',
    r'\b(legislação|legislacao|lei|leis|decreto|norma|normas|portaria|stf|stj|jurisprudência)\b',
    r'\b(artigo|artigos|paper|papers|publicação|publicacao|publicações|publicacoes|revista\s+científica)\b'
]

NO_SEARCH_PATTERNS = [
    r'^\s*(corrij|correg|reescrev|melhor|traduz|format|organiz|ajust|simplific)\w*',
    r'\b(gramática|gramatica|ortografia|pontuação|pontuacao|erro\s+de\s+digitação)\b',
    r'^\s*(código|codigo|python|javascript|typescript|html|css|sql|função|funcao|script)\s*:'
]

ACADEMIC_HISTORICAL_PATTERNS = [
    r'\b(pibic|cnpq|capes|fapesp|abnt|dissertação|dissertacao|tese|monografia|tcc)\b',
    r'\b(história|historia|século|seculo|ano\s+de\s+\d{4}|evolução|evolucao|origem|conceito|teoria|fundamentação)\b',
    r'\b(estatística|estatistica|indicador|indicadores|percentual|taxa|ibge|ipea|opas|who|oms)\b'
]

def should_search_web(
    user_message: str,
    history: Optional[List[Dict[str, Any]]] = None,
    active_cds_has_answer: bool = False
) -> bool:
    """
    Determina de forma autônoma se uma mensagem exige pesquisa web ativa.
    
    Regras:
    1. Se houver padrões explícitos de busca/fontes/legislação -> TRUE.
    2. Se for pedido de correção gramatical/reescrita/código puro -> FALSE.
    3. Se houver padrões acadêmicos/históricos/estatísticos -> TRUE.
    4. Se a busca RAG nos CDs locais ativos NÃO encontrou contexto suficiente (active_cds_has_answer=False) -> TRUE.
    5. Se os CDs locais ativos já possuem resposta suficiente e não há pedido explícito de web -> FALSE.
    """
    if not user_message or not user_message.strip():
        return False

    msg_clean = user_message.lower().strip()

    # 1. Checagem de Negação Direta (Correção / Reescrita / Código puro)
    for pattern in NO_SEARCH_PATTERNS:
        if re.search(pattern, msg_clean):
            # Se for apenas "Corrija este texto" sem pedir fontes externas
            if not any(re.search(exp, msg_clean) for exp in EXPLICIT_SEARCH_PATTERNS):
                return False

    # 2. Gatilhos de Busca Explícita
    for pattern in EXPLICIT_SEARCH_PATTERNS:
        if re.search(pattern, msg_clean):
            return True

    # 3. Gatilhos Acadêmicos, Históricos ou Normativos
    for pattern in ACADEMIC_HISTORICAL_PATTERNS:
        if re.search(pattern, msg_clean):
            return True

    # 4. Se a consulta aos CDs ativos localmente NÃO trouxe informações relevantes
    if not active_cds_has_answer and len(msg_clean.split()) >= 4:
        return True

    return False
