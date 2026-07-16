import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.config_loader import PIPELINE_CONFIG

# Cargar variables ocultas desde .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Error Crítico: GEMINI_API_KEY no encontrada en el archivo .env")

# Instanciar el cliente con la nueva SDK
client = genai.Client(api_key=api_key)

def evaluate_job_semantics(job_description: str) -> dict:
    """
    Inyecta la descripción de la vacante y el perfil del usuario al LLM.
    Retorna un diccionario estructurado mapeado desde un JSON estricto.
    """
    if not job_description or job_description == "N/A":
        return get_empty_evaluation()

    # Extraemos el contexto de tu configuración
    user_skills = json.dumps(PIPELINE_CONFIG["skills"], ensure_ascii=False)
    red_flags = json.dumps(PIPELINE_CONFIG["roles"]["red_flags"], ensure_ascii=False)

    prompt = f"""
    Eres un evaluador de reclutamiento técnico. Analiza la siguiente descripción de vacante frente al perfil del candidato.
    
    PERFIL DEL CANDIDATO:
    - Habilidades Técnicas: {user_skills}
    - Banderas Rojas (Rechazo inmediato): {red_flags}
    
    DESCRIPCIÓN DE LA VACANTE:
    {job_description}
    
    INSTRUCCIONES DE SALIDA:
    Devuelve ÚNICAMENTE un objeto JSON válido con la siguiente estructura exacta:
    {{
        "match_score": <int entre 0 y 100 evaluando la viabilidad>,
        "matched_skills": [<lista de strings con habilidades encontradas>],
        "missing_skills": [<lista de strings con habilidades requeridas que no están en el perfil>],
        "red_flags_detected": <string describiendo la bandera roja o null si no hay>,
        "justification": <string breve justificando el score>
    }}
    """

    try:
        # Llamada a la API forzando JSON mediante la clase GenerateContentConfig

        
        # Código corregido:
        response = client.models.generate_content(
        model='gemini-3.5-flash', # Actualizado según curl
        contents=prompt,
        config=types.GenerateContentConfig(
        response_mime_type="application/json",
            )
        )


        evaluation_dict = json.loads(response.text)
        return evaluation_dict

    except Exception as e:
        print(f"Error en evaluación LLM: {e}")
        return get_empty_evaluation()

def get_empty_evaluation() -> dict:
    """Retorna un esquema nulo en caso de fallo para no quebrar el pipeline."""
    return {
        "match_score": 0,
        "matched_skills": [],
        "missing_skills": [],
        "red_flags_detected": "Error de procesamiento",
        "justification": "No se pudo procesar la evaluación."
    }

if __name__ == "__main__":
    # Prueba lógica funcional
    vacante_prueba = "Buscamos Analista de Datos junior. Requisitos: manejo de PostgreSQL, Python avanzado y Power BI. 100% esquema mixto de comisiones por ventas cruzadas."
    
    print("Iniciando evaluación de prueba...")
    resultado = evaluate_job_semantics(vacante_prueba)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))