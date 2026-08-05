import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from artifact_engine import ArtifactEngine
from chat_power_executor import BORAX_EXPORTS_DIR, ensure_exports_dir

def test_generate_abnt_docx(engine: ArtifactEngine):
    print("\n--- [TEST 1/3] Geração de Documento DOCX ABNT (3+ páginas) ---")
    ensure_exports_dir()
    filepath = os.path.join(BORAX_EXPORTS_DIR, "teste_abnt_completo.docx")

    long_academic_markdown = """# ARQUITETURA DE INTELIGÊNCIA ARTIFICIAL LOCAL E COMPUTAÇÃO DE ALTA PERFORMANCE

## 1. INTRODUÇÃO E CONTEXTUALIZAÇÃO
A evolução das arquiteturas de Inteligência Artificial voltadas para execução local impõe novos paradigmas no processamento de linguagem natural e na segurança da informação empresarial. O avanço de modelos quantizados em formato GGUF e inferência direta em C++ permite reduzir drasticamente a latência de execução sem comprometer a confidencialidade dos dados sensíveis.

O objetivo deste trabalho é analisar detalhadamente o desempenho de modelos embutidos, técnicas de RAG (Retrieval-Augmented Generation) com LanceDB e a compilação estruturada de artefatos acadêmicos e corporativos.

## 2. FUNDAMENTAÇÃO TEÓRICA E REQUISITOS DE SISTEMA
Para assegurar a eficiência operacional em ecossistemas de hardware restrito, faz-se imperativa a adoção de técnicas modernas de otimização e alocação dinâmica de memória. A utilização de estruturas vetoriais nativas e tabelas de busca em disco proporciona tempo de resposta sub-segundo mesmo durante consultas a grandes acervos de documentos.

A tabela a seguir apresenta os requisitos operacionais recomendados para os diferentes modos de operação da plataforma:

| Componente | Requisito Mínimo | Requisito Recomendado | Impacto no Desempenho |
| Processador (CPU) | 4 Cores / 8 Threads | 8 Cores / 16 Threads | Alto (Inferência C++) |
| Memória RAM | 8 GB DDR4 | 16 GB DDR5 / ECC | Crítico (Contexto & LLM) |
| Armazenamento | SSD NVMe (500 MB/s) | SSD NVMe PCIe 4.0 (5000 MB/s) | Alto (Leitura LanceDB) |
| Aceleração GPU | Opcional (CPU Direct) | GPU Dedicada 8GB VRAM | Médio (Layer Offloading) |

### 2.1 DA ESTRUTURAÇÃO DE DADOS E TABELAS NATIVAS
Conforme demonstrado nos testes de bancada, a integração direta entre o motor de vetorização e os utilitários de geração de documentos garante a preservação da integridade estrutural e a aplicação rigorosa das normas ABNT.

## 3. ANÁLISE EXPERIMENTAL E RESULTADOS
Durante os experimentos com documentos extensos, verificou-se que a padronização das margens (superior/esquerda de 3cm e inferior/direita de 2cm) atrelada à fonte Arial 12pt com espaçamento 1.5 proporciona leitura fluida e conformidade com os requisitos formais de publicação acadêmica.

- **Conformidade ABNT**: Margens, espaçamentos e recuos de primeira linha de 1.25cm rigorosamente aplicados.
- **Rendimento de Tokens**: Capacidade de expansão de contexto para 8192 tokens com loop automático de continuação.
- **Tabelas Estilizadas**: Conversão limpa de tabelas Markdown em tabelas nativas do Word com cabeçalho escuro.

## 4. CONSIDERAÇÕES FINAIS E CONCLUSÃO
Conclui-se que a plataforma BORAX atinge os objetivos de geração documental extensa com elevadíssima fidelidade e robustez técnica. A descentralização da inteligência garante privacidade total e autonomia operacional para ambientes críticos.

## 5. REFERÊNCIAS BIBLIOGRÁFICAS
- ALMEIDA, R. *Engenharia de Software e Modelos Locais de Linguagem*. São Paulo: Editora Acadêmica, 2025.
- BORAX PLATAFORMA DE IA. *Especificação Técnica do Motor de Artefatos v1.6*. Rio de Janeiro, 2026.
"""

    out_path = engine.compile_docx(long_academic_markdown, filepath, title="Inteligência Artificial Local")
    size = os.path.getsize(out_path)
    line_count = len(long_academic_markdown.split("\n"))
    print(f"[OK] DOCX ABNT gerado com sucesso!")
    print(f"   Caminho: {out_path}")
    print(f"   Tamanho: {size} bytes ({size / 1024:.1f} KB)")
    print(f"   Linhas: {line_count}")
    assert os.path.exists(out_path) and size > 5000, "Falha na geração do DOCX"

def test_generate_excel_xlsx(engine: ArtifactEngine):
    print("\n--- [TEST 2/3] Geração de Planilha XLSX com Fórmulas Reais ---")
    ensure_exports_dir()
    filepath = os.path.join(BORAX_EXPORTS_DIR, "teste_planilha_formulas.xlsx")

    json_spreadsheet_content = """{
  "headers": ["Projeto / Módulo", "Horas Estimadas", "Valor Hora (R$)", "Custo Bruto (R$)", "Impostos (15%)", "Custo Total (R$)"],
  "rows": [
    ["Desenvolvimento Backend (FastAPI + LanceDB)", 120, 150.00, "=B2*C2", "=D2*0.15", "=D2+E2"],
    ["Interface Frontend (React + Tauri + Tailwind)", 90, 140.00, "=B3*C3", "=D3*0.15", "=D3+E3"],
    ["Motor de Artefatos (DOCX, XLSX & PDF)", 60, 160.00, "=B4*C4", "=D4*0.15", "=D4+E4"],
    ["Testes de Carga e Automação Desktop", 40, 130.00, "=B5*C5", "=D5*0.15", "=D5+E5"],
    ["TOTAL GERAL DO PROJETO", "=SUM(B2:B5)", "", "=SUM(D2:D5)", "=SUM(E2:E5)", "=SUM(F2:F5)"]
  ]
}"""

    out_path = engine.compile_xlsx(json_spreadsheet_content, filepath, title="Orçamento e Custos")
    size = os.path.getsize(out_path)
    print(f"[OK] XLSX Planilha com fórmulas gerado com sucesso!")
    print(f"   Caminho: {out_path}")
    print(f"   Tamanho: {size} bytes ({size / 1024:.1f} KB)")
    assert os.path.exists(out_path) and size > 2000, "Falha na geração do XLSX"

def test_generate_pdf_report(engine: ArtifactEngine):
    print("\n--- [TEST 3/3] Geração de PDF Formatado (Capa + Numeração) ---")
    ensure_exports_dir()
    filepath = os.path.join(BORAX_EXPORTS_DIR, "teste_relatorio_pdf.pdf")

    pdf_markdown = """# RELATÓRIO EXECUTIVO DE DESEMPENHO E ARQUITETURA

## 1. RESUMO EXECUTIVO
Este relatório apresenta as métricas consolidadas de desempenho da Plataforma BORAX, demonstrando a capacidade de síntese documental e geração automatizada de relatórios executivos em formato PDF com numeração dinâmica e capa institucional.

## 2. MÉTRICAS DE PROCESSAMENTO E LATÊNCIA
A tabela a seguir consolida os tempos médios de resposta observados durante os testes de carga:

| Módulo de Execução | Tempo Médio (ms) | Taxa de Sucesso (%) | Status |
| Compilação DOCX ABNT | 120 ms | 100% | Operacional |
| Gerador de Planilhas XLSX | 85 ms | 100% | Operacional |
| Motor de PDF ReportLab | 150 ms | 100% | Operacional |
| Inferência LLM Local C++ | 450 ms | 99.8% | Operacional |

## 3. RECOMENDAÇÕES E PRÓXIMOS PASSOS
Recomenda-se a distribuição regular deste conjunto de testes em pipeline de integração contínua para assegurar estabilidade em versões futuras.
"""

    out_path = engine.compile_pdf(pdf_markdown, filepath, title="Relatório de Desempenho")
    size = os.path.getsize(out_path)
    print(f"[OK] PDF com Capa e Rodapé gerado com sucesso!")
    print(f"   Caminho: {out_path}")
    print(f"   Tamanho: {size} bytes ({size / 1024:.1f} KB)")
    assert os.path.exists(out_path) and size > 2000, "Falha na geração do PDF"

def main():
    print("==================================================================")
    print("   SUÍTE DE TESTES: GERADOR DE ARTEFATOS BORAX (DOCX, XLSX, PDF)")
    print("==================================================================")
    
    engine = ArtifactEngine()
    test_generate_abnt_docx(engine)
    test_generate_excel_xlsx(engine)
    test_generate_pdf_report(engine)

    print("\n==================================================================")
    print(" TODOS OS 3 TESTES DE ARTEFATOS FORAM EXECUTADOS COM SUCESSO!")
    print("==================================================================")

if __name__ == "__main__":
    main()
