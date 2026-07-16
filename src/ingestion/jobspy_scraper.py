import pandas as pd
from jobspy import scrape_jobs
from src.config_loader import PIPELINE_CONFIG

def fetch_jobspy_jobs() -> pd.DataFrame:
    """
    Extrae vacantes de LinkedIn e Indeed utilizando jobspy.
    Mapea el output a las columnas estandarizadas.
    """
    # Extraemos solo el primer rol y la geografía general para esta prueba
    search_term = PIPELINE_CONFIG["roles"]["target"][0]
    location = "Ciudad de México"
    
    try:
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin"],
            search_term=search_term,
            location=location,
            results_wanted=15, # Volumen bajo para pruebas de desarrollo
            hours_old=24,      # Solo vacantes recientes
            country_sameline_search=False
        )
        
        if jobs.empty:
            return pd.DataFrame()
            
        # Normalización de columnas
        df = jobs[['title', 'company', 'location', 'description', 'job_url', 'site']].copy()
        df.rename(columns={'job_url': 'url', 'site': 'source'}, inplace=True)
        
        return df
    except Exception as e:
        print(f"Error en conector JobSpy: {e}")
        return pd.DataFrame()