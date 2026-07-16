import json
import os
from pathlib import Path

def load_config() -> dict:
    """
    Carga y retorna los parámetros estructurados desde config.json.
    Retorna un diccionario vacío y lanza un error por consola si el archivo no existe.
    """
    # Resuelve la ruta absoluta basándose en la ubicación de este script
    base_dir = Path(__file__).resolve().parent.parent
    config_path = os.path.join(base_dir, 'config', 'config.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return config_data
    except FileNotFoundError:
        print(f"Error crítico: No se encontró el archivo de configuración en {config_path}")
        return {}
    except json.JSONDecodeError:
        print("Error crítico: config.json tiene un formato inválido.")
        return {}

# Variable global para importar directamente la configuración instanciada
PIPELINE_CONFIG = load_config()

if __name__ == "__main__":
    # Prueba lógica funcional: Ejecutar este script directamente debe imprimir la configuración
    print(json.dumps(PIPELINE_CONFIG, indent=2, ensure_ascii=False))