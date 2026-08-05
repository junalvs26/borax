import os
import sys
from typing import Dict, Any, List, Optional

from embedded_engine import BoraxLLM
from artifact_engine import ArtifactEngine
from web_search_agent import WebSearchAgent
from academic_flow import AcademicFlowManager

PHD_ACADEMIC_WRITER_SYSTEM_PROMPT = (
    "Você é o REDATOR FINAL de Trabalhos Acadêmicos e TCCs da Plataforma BORAX.\n"
    "NUNCA use metalinguagem e NUNCA sugira sites ou diga 'você pode pesquisar em X site' ou 'aqui está um resumo do que encontrar'.\n"
    "Se o usuário pedir 'gere esse tcc para mim' ou solicitar a escrita do trabalho, VOCÊ DEVE ESCREVER O TEXTO COMPLETO DO TRABALHO DIRETA E IMEDIATAMENTE.\n\n"
    "ESTRUTURA OBRIGATÓRIA DA REDAÇÃO:\n"
    "1. RESUMO EXECUTIVO\n"
    "2. INTRODUÇÃO E PROBLEMATIZAÇÃO\n"
    "3. FUNDAMENTAÇÃO TEÓRICA E DESENVOLVIMENTO\n"
    "4. CONSIDERAÇÕES FINAIS\n"
    "5. REFERÊNCIAS BIBLIOGRÁFICAS\n\n"
    "REGRAS DE RIGOR:\n"
    "- Redija seções densas, altamente articuladas, linguagem acadêmica de nível de doutorado e citações no formato (SOBRENOME, Ano).\n"
    "- PROIBIDO: Frases clichês, conselhos evasivos, sugestões de sites ou repetição de links."
)

class AcademicWriterEngine:
    """
    Motor de Redação Acadêmica de Alto Padrão (Nível Doutorado ABNT 2026).
    """
    def __init__(self):
        self.llm = BoraxLLM()
        self.artifact_engine = ArtifactEngine()
        self.web_agent = WebSearchAgent()

    def process_academic_turn(
        self,
        query: str,
        messages: Optional[List[Dict[str, Any]]] = None,
        rag_context: str = "",
        force_compile: bool = False
    ) -> Dict[str, Any]:
        """
        Processa um turno de conversa acadêmica:
        - Se for sondagem/alinhamento: responde consultivamente e faz perguntas dinâmicas.
        - Se for solicitação de compilação/texto completo: redige o documento ABNT denso e compila o arquivo .docx.
        """
        is_ready = force_compile or AcademicFlowManager.is_ready_to_compile(query, messages)
        
        # 1. Pesquisa Web Autônoma de fontes e referências reais
        need_web = self.web_agent.should_search(query, history=messages, has_local_answer=bool(rag_context))
        web_context = ""
        if need_web:
            search_res = self.web_agent.search_references(query)
            web_context = search_res.get("formatted_context", "")

        # 2. Concatenação limpa do contexto para a LLM (sem vazar tags no chat)
        combined_context = f"{rag_context}\n\n{web_context}".strip()

        if is_ready:
            print(f"[AcademicWriterEngine] Compilando documento ABNT denso para: '{query}'")
            compilation_prompt = f"{query}\n\nPor favor, redija o TRABALHO ACADÊMICO COMPLETO em normas ABNT 2026 com todos os capítulos desenvolvidos em profundidade."
            full_markdown = self.llm.generate_text(
                prompt=compilation_prompt,
                system_prompt=PHD_ACADEMIC_WRITER_SYSTEM_PROMPT,
                max_tokens=1024
            )
            
            docx_path = self.artifact_engine.compile_docx(full_markdown, title=query[:30])
            size_bytes = os.path.getsize(docx_path) if os.path.exists(docx_path) else 0

            return {
                "type": "compilation",
                "content": full_markdown,
                "docx_path": docx_path,
                "file_metadata": {
                    "filename": os.path.basename(docx_path),
                    "file_format": "docx",
                    "size_bytes": size_bytes
                }
            }
        else:
            # Resposta consultiva dinâmica
            dynamic_instruction = AcademicFlowManager.get_dynamic_consultative_instruction(query)
            custom_system_prompt = f"{PHD_ACADEMIC_WRITER_SYSTEM_PROMPT}\n\n{dynamic_instruction}"

            response_text = self.llm.generate_text(
                prompt=query,
                system_prompt=custom_system_prompt,
                messages=messages,
                max_tokens=1024
            )

            return {
                "type": "consultation",
                "content": response_text,
                "searched_web": need_web
            }
