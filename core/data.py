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

def cargar_patios():
    """Solo para lectura y visualización."""
    todo = cargar_todo()
    data = todo.get("patios", [])
    # Normalizamos para que el resto del código use siempre 'name' y 'direccion'
    return [{
        "name": p.get("nombre_patio", p.get("name", "")), 
             "direccion": p.get("direccion", "")} for p in data]





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



def get_scac_linea_transporte(scac):
    linea_transfer = get_data_transfer()
    print(linea_transfer.get(scac))
    return linea_transfer

def get_data_transfer():
    linea_transfer = {
        datos.get("scac") : datos.get("name") for datos in cargar_todo().get("linea_transporte", {})}

    return linea_transfer
