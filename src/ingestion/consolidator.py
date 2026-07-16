import pandas as pd
from src.ingestion.jobspy_scraper import fetch_jobspy_jobs
from src.ingestion.satellite_scraper import fetch_local_jobs

def ingest_all_sources() -> pd.DataFrame:
    """
    Ejecuta todos los conectores de ingesta, concatena los resultados
    y normaliza el esquema del DataFrame final.
    """
    print("Iniciando ingesta: JobSpy (LinkedIn, Indeed)...")
    df_jobspy = fetch_jobspy_jobs()
    
    print("Iniciando ingesta: Extractor Satélite (Bolsas Locales)...")
    df_local = fetch_local_jobs()
    
    # Consolidación
    dfs_validos = [df for df in [df_jobspy, df_local] if not df.empty]
    
    if not dfs_validos:
        print("Fallo en ingesta: No se recuperaron vacantes.")
        # Retorna DataFrame vacío con la estructura correcta
        return pd.DataFrame(columns=['title', 'company', 'location', 'description', 'url', 'source'])
        
    df_final = pd.concat(dfs_validos, ignore_index=True)
    
    # Normalización estricta del esquema
    esquema_requerido = ['title', 'company', 'location', 'description', 'url', 'source']
    
    # Inyectar columnas faltantes si falla algún scraper
    for col in esquema_requerido:
        if col not in df_final.columns:
            df_final[col] = "N/A"
            
    # Filtrar solo las columnas objetivo y limpiar nulos
    df_final = df_final[esquema_requerido]
    df_final.fillna("N/A", inplace=True)
    
    # Eliminar duplicados exactos basados en la URL
    df_final.drop_duplicates(subset=['url'], keep='first', inplace=True)
    
    return df_final

if __name__ == "__main__":
    # Prueba lógica funcional
    df = ingest_all_sources()
    print(f"\nPipeline de Ingesta Completado. Total registros: {len(df)}")
    print(df.head())