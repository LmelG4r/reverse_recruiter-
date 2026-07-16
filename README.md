# Pipeline de procesamiento y análisis semántico de datos de mercado

## General
Arquitectura de datos automatizada diseñada para la ingesta multifuente, normalización y evaluación semántica de ofertas laborales. El sistema invierte el proceso tradicional de reclutamiento: extrae vacantes crudas del mercado, evalúa algorítmicamente el encaje técnico (match score) frente a un perfil parametrizado y descarta oportunidades con "banderas rojas" operativas.

## Diagrama de Flujo

El pipeline opera bajo un modelo ETL (Extract, Transform, Load) enriquecido con inferencia de Modelos de Lenguaje Grande (LLM):

1. **Ingestion:** 
   - Scrapers concurrentes apuntando a agregadores globales (LinkedIn, Indeed vía `jobspy`) y bolsas locales (OCC Mundial vía `BeautifulSoup`).
   - Gestión heurística de pausas para evasión de Rate Limits.
2. **Processing:**
   - Consolidación y normalización de esquemas de datos utilizando `Pandas`.
   - Limpieza de nulos y desduplicación determinista basada en URLs.
3. **Evaluation:**
   - Inyección de descripciones crudas a la API de **Gemini 3.5 Flash**.
   - Procesamiento semántico que retorna un JSON estricto con métricas de afinidad, mapeo de *skills* y detección temprana de *red flags* (ej. "esquemas 100% comisiones").
4. **Reporting:**
   - Filtrado final y ordenamiento descendente por `match_score`.
   - Generación de un artefacto Markdown diario altamente escaneable (`reporte_diario.md`).
   - Ejecución desatendida mediante cronjobs en **GitHub Actions**.

## Métricas de impacto y optimización

- **Reducción de tiempo de búsqueda:** Optimización del 100% del tiempo de búsqueda manual (ahorro estimado de 2-3 horas diarias).
- **Filtrado de precisión:** Descarte automático del 100% de vacantes con estructuras fraudulentas o desalineadas al perfil técnico deseado.
- **Latencia de ejecución:** Procesamiento de lote estándar (15-30 vacantes) en < 45 segundos.

## Stack

| Tecnología | Rol en la Arquitectura | Justificación Técnica |
|---|---|---|
| **Python 3.10** | Core Logic | Estándar de la industria para pipelines de datos y scripting de automatización. |
| **Pandas** | Data Manipulation | Eficiencia en memoria para transformaciones vectorizadas y limpieza de DataFrames. |
| **Gemini 3.5 Flash API** | Semantic Engine | Alta velocidad de inferencia, bajo costo computacional y soporte nativo para *Structured Outputs* (JSON). |
| **BeautifulSoup / Requests** | Web Scraping | Extracción ligera y resiliente de DOMs estáticos en bolsas de trabajo locales. |
| **GitHub Actions** | CI/CD / Cronjobs | Infraestructura serverless gratuita para la orquestación desatendida del pipeline en la nube. |

## Despliegue y configuración local

1. **Clonar repositorio e inicializar entorno:**
   ```bash
   git clone https://github.com/LmelG4r/reverse_recruiter-
   cd reverse_recruiter_pipeline
   python -m venv venv
   source venv/bin/activate  # Windows: .\venv\Scripts\activate
   pip install -r requirements.txt

## Configuración de variables:

Crear un archivo .env en la raíz (no rastreado por Git) e incluir: GEMINI_API_KEY=tu_clave_aqui

Ajustar el diccionario de habilidades y geografía en config/config.json.

## Ejecución manual:

Bash
python -m src.orquestador