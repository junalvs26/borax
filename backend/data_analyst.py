import os
import re
import duckdb
import polars as pl
from typing import Dict, Any, Optional
from services.ollama_service import OllamaService

class DataAnalyst:
    def __init__(self, ollama_service: Optional[OllamaService] = None):
        self.ollama_service = ollama_service or OllamaService()

    def inspect_schema(self, file_path: str) -> Dict[str, Any]:
        """Read column schema and sample rows using Polars or DuckDB."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo de dados não encontrado: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        con = duckdb.connect(database=':memory:')

        try:
            if ext == ".csv":
                df = con.execute(f"SELECT * FROM read_csv_auto('{file_path}') LIMIT 5").pl()
                table_sql_ref = f"read_csv_auto('{file_path}')"
            elif ext == ".parquet":
                df = con.execute(f"SELECT * FROM read_parquet('{file_path}') LIMIT 5").pl()
                table_sql_ref = f"read_parquet('{file_path}')"
            elif ext == ".json":
                df = con.execute(f"SELECT * FROM read_json_auto('{file_path}') LIMIT 5").pl()
                table_sql_ref = f"read_json_auto('{file_path}')"
            elif ext in [".xlsx", ".xls"]:
                # Load Excel via Polars
                df_pl = pl.read_excel(file_path)
                con.register("excel_data", df_pl.to_pandas())
                df = df_pl.head(5)
                table_sql_ref = "excel_data"
            else:
                raise ValueError(f"Formato de planilha não suportado: {ext}. Use .csv, .parquet, .xlsx ou .json.")

            columns_schema = {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}
            sample_rows = df.to_dicts()

            return {
                "file_path": file_path,
                "table_sql_ref": table_sql_ref,
                "columns": columns_schema,
                "sample_rows": sample_rows
            }
        finally:
            con.close()

    def generate_sql_query(self, schema_info: Dict[str, Any], user_query: str, model: str = "llama3.2") -> str:
        """Prompt Ollama to generate DuckDB SQL for user question."""
        prompt = (
            f"Você é um especialista em SQL DuckDB. "
            f"Dada a tabela '{schema_info['table_sql_ref']}' com as seguintes colunas e tipos:\n"
            f"{schema_info['columns']}\n\n"
            f"Exemplo de dados das 5 primeiras linhas:\n"
            f"{schema_info['sample_rows']}\n\n"
            f"Gere APENAS a consulta SQL em DuckDB válida para responder à pergunta: '{user_query}'.\n"
            f"IMPORTANTE: Retorne SOMENTE o código SQL dentro de um bloco ```sql ... ``` sem comentários adicionais."
        )

        messages = [{"role": "user", "content": prompt}]
        
        # Collect tokens from Ollama streaming
        sql_response = ""
        try:
            # Synchronous wrapper for ollama stream
            import asyncio
            async def get_response():
                res = []
                async for token in self.ollama_service.chat_stream(model, messages):
                    res.append(token)
                return "".join(res)
            
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In active loop, create new loop in thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    sql_response = pool.submit(lambda: asyncio.run(get_response())).result()
            else:
                sql_response = loop.run_until_complete(get_response())
        except Exception:
            # Fallback simple query if Ollama is offline or unpromoted
            sql_response = f"SELECT * FROM {schema_info['table_sql_ref']} LIMIT 10"

        # Extract SQL from markdown block if present
        match = re.search(r'```sql\s*(.*?)\s*```', sql_response, re.DOTALL | re.IGNORECASE)
        if match:
            sql_clean = match.group(1).strip()
        else:
            match_generic = re.search(r'```\s*(.*?)\s*```', sql_response, re.DOTALL)
            sql_clean = match_generic.group(1).strip() if match_generic else sql_response.strip()

        return sql_clean

    def query_data(self, file_path: str, user_query: str, model: str = "llama3.2") -> Dict[str, Any]:
        """Execute natural language query against tabular data using DuckDB + Polars."""
        schema_info = self.inspect_schema(file_path)
        sql_query = self.generate_sql_query(schema_info, user_query, model=model)

        con = duckdb.connect(database=':memory:')
        try:
            # Execute generated DuckDB query
            result_df = con.execute(sql_query).pl()
            result_rows = result_df.head(100).to_dicts()

            summary_msg = f"Consulta SQL executada com sucesso! Retornou {len(result_df)} linhas."

            return {
                "status": "success",
                "file_path": file_path,
                "user_query": user_query,
                "sql_executed": sql_query,
                "total_rows": len(result_df),
                "columns": result_df.columns,
                "results": result_rows,
                "summary": summary_msg
            }
        except Exception as e:
            # Fallback direct select on SQL error
            fallback_sql = f"SELECT * FROM {schema_info['table_sql_ref']} LIMIT 10"
            result_df = con.execute(fallback_sql).pl()
            return {
                "status": "partial_success",
                "error_details": str(e),
                "user_query": user_query,
                "sql_executed": fallback_sql,
                "total_rows": len(result_df),
                "columns": result_df.columns,
                "results": result_df.to_dicts(),
                "summary": f"Erro na SQL gerada. Exibindo primeiras 10 linhas da tabela."
            }
        finally:
            con.close()
