import pandas as pd
from datetime import datetime
from src.ingestion.consolidator import ingest_all_sources
from src.evaluation.llm_evaluator import evaluate_job_semantics

def generate_markdown_report(df_top: pd.DataFrame, file_path: str = "reporte_diario.md"):
    """
    Toma el DataFrame filtrado y genera un reporte Markdown altamente escaneable.
    """
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_content = f"# 🚀 Reporte de Reclutamiento Inverso\n"
    md_content += f"**Última actualización:** {fecha_actual}\n\n"
    
    if df_top.empty:
        md_content += "### ⚠️ Cero hallazgos\n"
        md_content += "No se encontraron vacantes viables libres de banderas rojas en esta ejecución.\n"
    else:
        md_content += "---\n\n"
        for index, row in df_top.iterrows():
            # Extraer variables manejando posibles nulos estructurales
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
            md_content += f"- **🔗 Enlace:** [Aplicar a la vacante]({url})\n\n"
            md_content += "---\n"
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Reporte generado exitosamente en: {file_path}")

def run_pipeline():
    """
    Ejecución principal: Ingesta -> Evaluación -> Filtrado -> Reporte.
    """
    print("=== INICIANDO PIPELINE DE RECLUTAMIENTO INVERSO ===")
    
    # 1. Ingesta
    df_jobs = ingest_all_sources()
    if df_jobs.empty:
        print("Finalizando: No hay datos para procesar.")
        generate_markdown_report(pd.DataFrame())
        return

    print(f"Iniciando evaluación semántica para {len(df_jobs)} vacantes...")
    
    # 2. Evaluación
    resultados = []
    for index, row in df_jobs.iterrows():
        print(f"Evaluando [{index + 1}/{len(df_jobs)}]: {row['title']}...")
        evaluacion = evaluate_job_semantics(row['description'])
        
        # Fusionar datos originales con la evaluación del LLM
        row_data = row.to_dict()
        row_data.update(evaluacion)
        resultados.append(row_data)
        
    df_evaluado = pd.DataFrame(resultados)
    
    # 3. Filtrado y Ordenamiento
    # Descartar filas donde el LLM detectó una bandera roja (red_flags_detected no es None)
    df_limpio = df_evaluado[df_evaluado['red_flags_detected'].isnull()]
    
    print(f"Filtro aplicado: {len(df_evaluado) - len(df_limpio)} vacantes descartadas por banderas rojas.")
    
    # Ordenar por score descendente y tomar el Top 10
    df_limpio = df_limpio.sort_values(by='match_score', ascending=False)
    df_top10 = df_limpio.head(10)
    
    # 4. Generación de Reporte
    generate_markdown_report(df_top10)
    print("=== PIPELINE COMPLETADO ===")

if __name__ == "__main__":
    run_pipeline()