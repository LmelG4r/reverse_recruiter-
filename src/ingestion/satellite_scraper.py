import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-MX,es;q=0.9",
    "Referer": "https://www.google.com/"
}

def fetch_local_jobs() -> pd.DataFrame:
    url = "https://www.occ.com.mx/empleos/de-analista-de-datos/en-ciudad-de-mexico/"
    time.sleep(random.uniform(2.0, 4.0))
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        jobs_data = []
        cards = soup.find_all('div', id=lambda x: x and 'jobcard' in x.lower())[:5]
        
        for card in cards:
            title = card.find('h2')
            company = card.find('a', attrs={"data-testid": "jobcard-company"})
            url_path = card.find('a', href=True)
            
            if title and url_path:
                raw_href = url_path['href']
                
                # 1. Corrección de URL
                if raw_href.startswith('http'):
                    job_url = raw_href
                else:
                    # Limpiamos barras duplicadas
                    clean_path = raw_href if raw_href.startswith('/') else f"/{raw_href}"
                    job_url = f"https://www.occ.com.mx{clean_path}"
                    # Prevenir el error "https://www.occ.com.mxhttps//..."
                    job_url = job_url.replace("https://www.occ.com.mxhttps//", "https://")

                # 2. Extracción profunda (Inner Fetch) para alimentar al LLM
                time.sleep(random.uniform(1.0, 2.5)) # Pausa para evitar baneos de OCC
                try:
                    inner_resp = requests.get(job_url, headers=HEADERS, timeout=10)
                    inner_soup = BeautifulSoup(inner_resp.text, 'html.parser')
                    # Extraemos el texto de toda la página y lo limpiamos
                    description = inner_soup.get_text(separator=' ', strip=True)
                    # Acotamos a 3000 caracteres para no saturar los tokens del LLM
                    description = description[:3000] if len(description) > 50 else "Descripción no accesible."
                except Exception as inner_e:
                    description = f"Error al extraer descripción: {inner_e}"

                jobs_data.append({
                    'title': title.get_text(strip=True),
                    'company': company.get_text(strip=True) if company else "Confidencial",
                    'location': "CDMX / EdoMex",
                    'description': description,
                    'url': job_url,
                    'source': "occ_mundial"
                })
                
        return pd.DataFrame(jobs_data)
    except Exception as e:
        print(f"Error en Scraper Satélite: {e}")
        return pd.DataFrame()