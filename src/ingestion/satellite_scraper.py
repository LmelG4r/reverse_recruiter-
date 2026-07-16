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
    """
    Scraper basado en requests/BS4 para OCC Mundial.
    Extrae datos estáticos inyectando pausas heurísticas.
    """
    # Ruta parametrizada estática de prueba
    url = "https://www.occ.com.mx/empleos/de-analista-de-datos/en-ciudad-de-mexico/"
    
    # Pausa inteligente (Evasión de rate limits)
    time.sleep(random.uniform(2.0, 4.5))
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        jobs_data = []
        # Localiza las tarjetas de trabajo (selectores genéricos para resiliencia)
        cards = soup.find_all('div', id=lambda x: x and 'jobcard' in x.lower())[:5]
        
        for card in cards:
            title = card.find('h2')
            company = card.find('a', attrs={"data-testid": "jobcard-company"})
            url_path = card.find('a', href=True)
            
            if title:
                jobs_data.append({
                    'title': title.get_text(strip=True),
                    'company': company.get_text(strip=True) if company else "Confidencial",
                    'location': "CDMX / EdoMex",
                    'description': "Descripción extendida en la URL nativa.",
                    'url': f"https://www.occ.com.mx{url_path['href']}" if url_path else url,
                    'source': "occ_mundial"
                })
                
        return pd.DataFrame(jobs_data)
    except Exception as e:
        print(f"Error en Scraper Satélite: {e}")
        return pd.DataFrame()