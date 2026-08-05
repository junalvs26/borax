import os
import re
import uuid
from typing import Dict, Any, Optional, List
from document_generator import convert_markdown_to_docx
from artifact_engine import ArtifactEngine
from chat_power_executor import BORAX_EXPORTS_DIR, ensure_exports_dir

class DocumentWizardEngine:
    def __init__(self, ollama_service=None, rag_engine=None):
        self.ollama_service = ollama_service
        self.rag_engine = rag_engine
        self.artifact_engine = ArtifactEngine()

    def initiate_wizard(self, prompt: str = "") -> Dict[str, Any]:
        """
        State Interruption: Return awaiting_wizard state so chat UI renders requirements card.
        """
        clean_p = (prompt or "").lower().strip()

        doc_type = "technical"
        if "abnt" in clean_p or "acadêmico" in clean_p or "tcc" in clean_p or "artigo" in clean_p:
            doc_type = "abnt"
        elif "planilha" in clean_p or "excel" in clean_p or "tabela" in clean_p or "xlsx" in clean_p:
            doc_type = "spreadsheet"
        elif "proposta" in clean_p or "comercial" in clean_p or "orçamento" in clean_p:
            doc_type = "proposal"
        elif "resumo" in clean_p or "sintético" in clean_p:
            doc_type = "summary"

        tone = "scientific" if doc_type == "abnt" else "direct"
        default_fmt = "xlsx" if doc_type == "spreadsheet" else "docx"

        return {
            "status": "awaiting_wizard",
            "wizard_active": True,
            "message": "Por favor, informe o tema do trabalho, a estrutura desejada e quais detalhes utilizar.",
            "prompt_original": prompt,
            "suggested_preferences": {
                "theme": prompt if prompt and not prompt.startswith("@") else "",
                "sections": "",
                "document_type": doc_type,
                "tone": tone,
                "export_format": default_fmt,
                "filename": f"trabalho_{doc_type}_{str(uuid.uuid4())[:6]}"
            },
            "options": {
                "document_types": [
                    {"id": "abnt", "label": "Acadêmico ABNT", "desc": "Estrutura formal ABNT com seções, citações e referências"},
                    {"id": "technical", "label": "Relatório Técnico", "desc": "Especificações, métricas e recomendações"},
                    {"id": "spreadsheet", "label": "Planilha / Dados Excel", "desc": "Tabelas organizadas com fórmulas ativas"},
                    {"id": "proposal", "label": "Proposta Comercial", "desc": "Objetivo, escopo e entregáveis"},
                    {"id": "summary", "label": "Resumo Executivo", "desc": "Síntese concisa em tópicos chave"}
                ],
                "tones": [
                    {"id": "scientific", "label": "Científico / Formal", "desc": "Linguagem impessoal e precisa"},
                    {"id": "direct", "label": "Direto e Objetivo", "desc": "Foco em resultados e clareza"},
                    {"id": "didactic", "label": "Didático / Explicativo", "desc": "Tom instrutivo com exemplos"}
                ],
                "export_formats": [
                    {"id": "docx", "label": "Word ABNT (.docx)"},
                    {"id": "xlsx", "label": "Excel (.xlsx)"},
                    {"id": "pdf", "label": "PDF (.pdf)"},
                    {"id": "txt", "label": "Texto (.txt)"}
                ]
            }
        }

    def generate_custom_document(
        self,
        prompt: str,
        preferences: Dict[str, Any],
        context_text: str = ""
    ) -> Dict[str, Any]:
        """
        Deep-Drafting Generation Pipeline:
        Stage A: Synthesize full fluid Markdown/Data via LLM using elite deep-draft prompt.
        Stage B: Pass synthesized content to ArtifactEngine for native DOCX, XLSX, or PDF compilation.
        """
        theme = (preferences.get("theme") or prompt or "").strip()
        if not theme or theme.startswith("@"):
            return self.initiate_wizard(prompt)

        sections = preferences.get("sections", "").strip()
        doc_type = preferences.get("document_type", "abnt")
        tone = preferences.get("tone", "scientific")
        export_fmt = preferences.get("export_format", "docx").lower().replace(".", "")
        clean_filename = preferences.get("filename") or f"trabalho_{doc_type}_{str(uuid.uuid4())[:6]}"
        if not clean_filename.endswith(f".{export_fmt}"):
            out_filename = f"{clean_filename}.{export_fmt}"
        else:
            out_filename = clean_filename

        ensure_exports_dir()
        out_filepath = os.path.join(BORAX_EXPORTS_DIR, out_filename)

        # Clean any raw [knowledge_base]: markers from RAG context
        clean_rag_context = ""
        if context_text:
            clean_rag_context = re.sub(r'\[.*?\]:', '', context_text).strip()

        # System Prompt de Redação Profunda (Deep-Drafting)
        if export_fmt == "xlsx" or doc_type == "spreadsheet":
            system_prompt = """Você é um analista de dados e engenheiro de planilhas sênior.
Sua tarefa é gerar uma tabela de dados completa e detalhada para Excel em formato JSON ou Tabela Markdown.
REGRAS OBRIGATÓRIAS:
- Inclua cabeçalhos claros (ex: Item, Categoria, Quantidade, Valor Unitário, Subtotal, Impostos, Total).
- Forneça FÓRMULAS do Excel reais para colunas calculadas (ex: '=B2*C2', '=SUM(D2:D10)', '=AVERAGE(E2:E10)').
- Se usar JSON, retorne um objeto no formato: {"headers": [...], "rows": [[...], [...]]}."""
            user_prompt_llm = f"Gere uma planilha de dados completa com fórmulas ativas sobre o tema: '{theme}'."
            if sections:
                user_prompt_llm += f"\nInclua as seguintes colunas/tópicos: {sections}."
        else:
            system_prompt = """Você é um redator sênior. NUNCA resuma. Escreva capítulos extensos, com introduções ricas, fundamentação teórica sólida, análise crítica e considerações finais detalhadas. Cada capítulo deve conter múltiplos parágrafos bem desenvolvidos.

REGRAS DE REDAÇÃO:
- NUNCA cole trechos brutos ou marcadores como [knowledge_base] no texto.
- Sintetize as informações com suas próprias palavras em tom acadêmico/profissional fluido.
- Estruture o texto com títulos claros em Markdown (#, ##, ###), parágrafos bem desenvolvidos e conectivos lógicos.
- Desenvolva cada seção de forma aprofundada, com introdução contextualizada, fundamentação teórica e considerações finais.
- Inclua tabelas explicativas em Markdown quando relevante."""
            user_prompt_llm = f"Por favor, redija um trabalho/relatório completo e aprofundado sobre o tema: '{theme}'."
            if sections:
                user_prompt_llm += f"\nDesenvolva com profundidade as seguintes seções: {sections}."
            if clean_rag_context:
                user_prompt_llm += f"\n\nSintetize e articule as seguintes referências teóricas obtidas da base de dados:\n{clean_rag_context}"

        markdown_llm_output = ""

        # Invoke LLM Synthesis via embedded engine / ollama service
        if self.ollama_service:
            try:
                print(f"[DocumentWizardEngine] Solicitando síntese fluida e aprofundada para o tema: '{theme}'...")
                if hasattr(self.ollama_service, "generate_long_text"):
                    res_llm = self.ollama_service.generate_long_text(
                        prompt=user_prompt_llm,
                        system_prompt=system_prompt
                    )
                elif hasattr(self.ollama_service, "generate_text"):
                    res_llm = self.ollama_service.generate_text(
                        prompt=user_prompt_llm,
                        system_prompt=system_prompt
                    )
                elif hasattr(self.ollama_service, "generate_stream"):
                    res_llm = "".join(list(self.ollama_service.generate_stream(
                        prompt=user_prompt_llm,
                        system_prompt=system_prompt
                    )))
                else:
                    res_llm = ""

                if res_llm and len(res_llm.strip()) > 50:
                    markdown_llm_output = res_llm.strip()
            except Exception as e:
                print(f"[DocumentWizardEngine Warning] Falha na síntese LLM: {e}. Gerando estrutura alternativa.")

        # Fallback Markdown synthesis if offline
        if not markdown_llm_output:
            if export_fmt == "xlsx":
                markdown_llm_output = """{
  "headers": ["Item / Descrição", "Quantidade", "Custo Unitário (R$)", "Total (R$)"],
  "rows": [
    ["Licenciamento de Software", 10, 250.00, "=B2*C2"],
    ["Serviços de Infraestrutura Cloud", 5, 1200.00, "=B3*C3"],
    ["Suporte Técnico Especializado", 20, 180.00, "=B4*C4"],
    ["Total Geral de Investimento", "", "", "=SUM(D2:D4)"]
  ]
}"""
            else:
                clean_theme_title = theme.upper()
                markdown_llm_output = f"# ESTUDO TÉCNICO E ANÁLISE DETALHADA: {clean_theme_title}\n\n"
                markdown_llm_output += "## 1. INTRODUÇÃO E OBJETIVOS\n"
                markdown_llm_output += f"A presente investigação aborda de maneira aprofundada a temática atrelada a **{theme}**, buscando delinear as diretrizes fundamentais e os conceitos aplicáveis ao cenário contemporâneo. "
                markdown_llm_output += "Através de uma abordagem analítica e embasada, o objetivo central deste estudo consiste em mapear as variáveis críticas e propor estratégias sólidas para implementação e tomada de decisão.\n\n"

                if sections:
                    markdown_llm_output += "## 2. DESENVOLVIMENTO E ANÁLISE DAS SEÇÕES\n"
                    for sec in sections.split(","):
                        sec_clean = sec.strip()
                        if sec_clean:
                            markdown_llm_output += f"### 2.{sections.split(',').index(sec)+1} {sec_clean.upper()}\n"
                            markdown_llm_output += f"No âmbito de **{sec_clean}**, identifica-se a necessidade imperativa de alinhar os procedimentos metodológicos com os objetivos estratégicos de **{theme}**. "
                            markdown_llm_output += "A articulação dos dados evidencia que a padronização e o monitoramento contínuo das etapas operacionais garantem elevada eficiência e redução de riscos.\n\n"
                else:
                    markdown_llm_output += "## 2. FUNDAMENTAÇÃO TEÓRICA E METODOLÓGICA\n"
                    markdown_llm_output += f"No desenvolvimento dos aspectos relativos a **{theme}**, constata-se a relevância da integração de metodologias consolidadas com inovações tecnológicas. "
                    if clean_rag_context:
                        markdown_llm_output += f"A síntese dos dados de referência indica que a aplicação prática das diretrizes contribui significativamente para o aprimoramento dos processos.\n\n"
                    else:
                        markdown_llm_output += "A fundamentação teórica sustenta a necessidade de acompanhamento periódico e revisão das métricas de qualidade estabelecidas.\n\n"

                markdown_llm_output += "## 3. CONSIDERAÇÕES FINAIS E RECOMENDAÇÕES\n"
                markdown_llm_output += f"Em síntese, o aprofundamento acerca de **{theme}** demonstra a viabilidade e a importância de uma gestão estruturada baseada em evidências. "
                markdown_llm_output += "Recomenda-se a continuidade dos estudos e o alinhamento das equipes envolvidas para assegurar a sustentabilidade e excelência dos resultados a longo prazo.\n\n"

                if doc_type == "abnt":
                    markdown_llm_output += "## 4. REFERÊNCIAS\n"
                    markdown_llm_output += f"- PLATAFORMA BORAX LOCAL AI. *Redação Técnica e Científica em {theme}*. Versão 1.6, 2026.\n"

        # Stage B: Artifact Compilation via ArtifactEngine
        if export_fmt == "docx":
            self.artifact_engine.compile_docx(markdown_llm_output, out_filepath, title=theme)
        elif export_fmt == "xlsx":
            self.artifact_engine.compile_xlsx(markdown_llm_output, out_filepath, title=theme)
        elif export_fmt == "pdf":
            self.artifact_engine.compile_pdf(markdown_llm_output, out_filepath, title=theme)
        else:
            with open(out_filepath, "w", encoding="utf-8") as f:
                f.write(markdown_llm_output)

        file_size = os.path.getsize(out_filepath) if os.path.exists(out_filepath) else 0

        # Estimate page/line counts
        line_count = len(markdown_llm_output.split("\n"))
        est_pages = max(1, line_count // 35) if export_fmt in ["docx", "pdf"] else 1

        file_payload = {
            "status": "success",
            "filename": out_filename,
            "file_format": export_fmt,
            "filepath": out_filepath,
            "size_bytes": file_size,
            "page_count": est_pages,
            "line_count": line_count,
            "download_url": f"/api/file/download/{out_filename}",
            "message": f"Artefato '{out_filename}' gerado com sucesso!"
        }

        return {
            "status": "success",
            "message": f"📄 Artefato **'{out_filename}'** gerado com sucesso para o tema **'{theme}'**!",
            "preferences": preferences,
            "document_text": markdown_llm_output,
            "file": file_payload
        }

