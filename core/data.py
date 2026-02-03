import json
from pathlib import Path

FOLDER_PATH = Path(__file__).parent.parent / "config"
JSON_PATH = FOLDER_PATH / "templates.json"

def cargar_todo()->dict:
    """Carga el diccionario completo para no perder datos de otras secciones."""

    if not JSON_PATH.exists():
        return {"solicitudes": {}, "unidades": {}, "patios": [] , "linea_transporte":[]}
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_coord(destino:str , name:str)->list:
    """funcion para extaer las coordenadas de las plantillas dependiendo de 
    la plantilla seleccionada"""
    solicitudes = (patios for patios in cargar_todo()["solicitud"].items())

    for solicitud ,coodr  in solicitudes:
        is_requested = solicitud == destino
        if is_requested:
            for cord in coodr["fields"]:
                if cord["name"] == name:
                    
                    return [cord["x"] , cord["y"]]
    return [None,None]

def update_file(new_data )->bool:
    
    try:
        with open(JSON_PATH , "w" , encoding="utf-8") as f:
            json.dump(new_data,f,indent=4,ensure_ascii=False)
        print(f"Datos ingresados con exito")
        return True
    except Exception as e:
        raise f"Error al actualizar el archivo: {e}" 
    

