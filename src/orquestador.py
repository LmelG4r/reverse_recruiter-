import os
import pandas as pd
from datetime import datetime
from src.ingestion.consolidator import ingest_all_sources
from src.evaluation.llm_evaluator import evaluate_job_semantics

# Ruta para el ledger de memoria de vacantes
HISTORY_FILE = "config/vistas.txt"

def load_seen_urls() -> set:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return set(f.read().splitlines())
    return set()

def save_seen_urls(urls: list):
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        for url in urls:
            f.write(f"{url}\n")

def generate_markdown_report(df_top: pd.DataFrame, file_path: str = "reporte_diario.md"):
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_content = f"# 🚀 Reporte de Reclutamiento Inverso\n"
    md_content += f"**Última actualización:** {fecha_actual}\n\n"
    
    if df_top.empty:
        md_content += "### ⚠️ Sin nuevas coincidencias\n"
        md_content += "No se encontraron vacantes nuevas viables o libres de banderas rojas en esta ejecución.\n"
    else:
        md_content += "---\n\n"
        for index, row in df_top.iterrows():
            score = row.get('match_score', 0)
            title = row.get('title', 'Sin título')
            company = row.get('company', 'Confidencial')
            location = row.get('location', 'N/A')
            source = row.get('source', 'N/A')
            url = row.get('url', '#')
            justification = row.get('justification', 'Sin justificación')
            matched = ", ".join(row.get('matched_skills', [])) or "Ninguna"
            missing = ", ".join(row.get('missing_skills', [])) or "Ninguna"

            md_content += f"## [{score}%] {title} @ {company}\n"
            md_content += f"- **📍 Ubicación:** {location} | **📡 Fuente:** {source}\n"
            md_content += f"- **🎯 Justificación:** {justification}\n"
            md_content += f"- **✅ Skills Match:** {matched}\n"
            md_content += f"- **❌ Skills Faltantes:** {missing}\n"
            md_content += f"- **🔗 Enlace:** [{url}]({url})\n\n"
            md_content += "---\n"
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Reporte generado exitosamente en: {file_path}")

def run_pipeline():
    print("=== INICIANDO PIPELINE DE RECLUTAMIENTO INVERSO ===")
    
    # 1. Ingesta
    df_jobs = ingest_all_sources()
    if df_jobs.empty:
        print("Finalizando: No hay datos para procesar.")
        generate_markdown_report(pd.DataFrame())
        return

    # 2. Filtrado de Estado (Memoria)
    seen_urls = load_seen_urls()
    df_nuevas = df_jobs[~df_jobs['url'].isin(seen_urls)].copy()
    
    print(f"Vacantes extraídas: {len(df_jobs)} | Ya vistas: {len(df_jobs) - len(df_nuevas)} | Nuevas a evaluar: {len(df_nuevas)}")
    
    if df_nuevas.empty:
        generate_markdown_report(pd.DataFrame())
        return

    # 3. Evaluación
    print(f"Iniciando evaluación semántica para {len(df_nuevas)} vacantes nuevas...")
    resultados = []
    
    for index, row in df_nuevas.iterrows():
        evaluacion = evaluate_job_semantics(row['description'])
        row_data = row.to_dict()
        row_data.update(evaluacion)
        resultados.append(row_data)
        
    df_evaluado = pd.DataFrame(resultados)
    
    # Registrar las nuevas URLs en el historial
    save_seen_urls(df_nuevas['url'].tolist())
    
    # 4. Filtrado y Ordenamiento
    df_limpio = df_evaluado[df_evaluado['red_flags_detected'].isnull()]
    print(f"Descartadas por banderas rojas: {len(df_evaluado) - len(df_limpio)}")
    
    df_limpio = df_limpio.sort_values(by='match_score', ascending=False)
    df_top10 = df_limpio.head(10)
    
    # 5. Reporte
    generate_markdown_report(df_top10)
    print("=== PIPELINE COMPLETADO ===")

if __name__ == "__main__":
    run_pipeline()