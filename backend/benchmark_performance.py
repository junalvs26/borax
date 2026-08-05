import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from embedded_engine import BoraxLLM, list_local_models

def run_benchmark(n_threads: int, n_ctx: int, n_gpu_layers: int = 0):
    models = list_local_models()
    if not models:
        print("Nenhum modelo encontrado para benchmark.")
        return

    model_path = models[0]["path"]
    model_name = models[0]["name"]

    print(f"\n--- BENCHMARK: {model_name} (n_threads={n_threads}, n_ctx={n_ctx}, n_gpu_layers={n_gpu_layers}) ---")
    
    t0 = time.time()
    llm = BoraxLLM(model_name_or_path=model_path, n_ctx=n_ctx, n_threads=n_threads, n_gpu_layers=n_gpu_layers)
    t_load = time.time() - t0
    print(f"[1] Tempo de Inicialização/Carga na Memória: {t_load:.2f}s")

    prompt = "Responda de forma sucinta: O que é Inteligência Artificial?"
    
    t_start = time.time()
    first_token_time = None
    token_count = 0

    stream = llm.generate_stream(prompt=prompt, system_prompt="Você é um assistente conciso.")
    
    full_text = ""
    for token in stream:
        if first_token_time is None:
            first_token_time = time.time() - t_start
        token_count += 1
        full_text += token

    t_total = time.time() - t_start
    tps = token_count / t_total if t_total > 0 else 0

    print(f"[2] Time-to-First-Token (TTFT - Latência Inicial): {first_token_time:.2f}s")
    print(f"[3] Duração Total de Geração: {t_total:.2f}s ({token_count} tokens)")
    print(f"[4] Velocidade de Geração: {tps:.2f} tokens/segundo")
    print(f"[5] Amostra da Resposta: {full_text[:80]}...\n")

    return {
        "n_threads": n_threads,
        "n_ctx": n_ctx,
        "n_gpu_layers": n_gpu_layers,
        "load_time": t_load,
        "ttft": first_token_time,
        "total_time": t_total,
        "tps": tps,
        "tokens": token_count
    }

def main():
    print("====================================================")
    print("   [BATERIA DE BENCHMARKS DE PERFORMANCE BORAX]    ")
    print("====================================================")

    results = []
    
    # Test 1: Baseline (4 threads, 2048 ctx, CPU)
    r1 = run_benchmark(n_threads=4, n_ctx=2048, n_gpu_layers=0)
    results.append(r1)

    # Test 2: High Threading (8 threads, 2048 ctx, CPU)
    r2 = run_benchmark(n_threads=8, n_ctx=2048, n_gpu_layers=0)
    results.append(r2)

    # Test 3: Compact Context (4 threads, 1024 ctx, CPU)
    r3 = run_benchmark(n_threads=4, n_ctx=1024, n_gpu_layers=0)
    results.append(r3)

    # Test 4: GPU Offload (4 threads, 2048 ctx, n_gpu_layers=-1 if GPU available)
    r4 = run_benchmark(n_threads=4, n_ctx=2048, n_gpu_layers=-1)
    results.append(r4)

    print("====================================================")
    print("           RESUMO COMPARATIVO DE RESULTADOS         ")
    print("====================================================")
    print(f"{'Configuração':<35} | {'TTFT (s)':<10} | {'TPS (tok/s)':<12} | {'Tempo Total':<12}")
    print("-" * 75)
    for r in results:
        if not r: continue
        config_str = f"Threads:{r['n_threads']} Ctx:{r['n_ctx']} GPU:{r['n_gpu_layers']}"
        print(f"{config_str:<35} | {r['ttft']:<10.2f} | {r['tps']:<12.2f} | {r['total_time']:<12.2f}s")

if __name__ == "__main__":
    main()
