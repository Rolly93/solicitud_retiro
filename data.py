import json
from pathlib import Path

FOLDER_PATH = Path(__file__).parent / "templates"
JSON_PATH = FOLDER_PATH / "templates.json"

def cargar_todo():
    """Carga el diccionario completo para no perder datos de otras secciones."""
    if not JSON_PATH.exists():
        return {"solicitudes": {}, "unidades": {}, "patios": []}
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def cargar_patios():
    """Solo para lectura y visualización."""
    todo = cargar_todo()
    data = todo.get("patios", [])
    # Normalizamos para que el resto del código use siempre 'name' y 'direccion'
    return [{"name": p.get("nombre_patio", p.get("name", "")), 
             "direccion": p.get("direccion", "")} for p in data]

def save_master(todo):
    """Guarda el objeto completo sin borrar secciones."""
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(todo, f, indent=4, ensure_ascii=False)

def insert_patio(patio_name, address):
    todo = cargar_todo()
    patios = todo.get("patios", [])

    # Verificar duplicados
    if any(p.get("name", "").lower() == patio_name.lower() for p in patios):
        return False, f"El patio '{patio_name}' ya existe."

    # Agregamos a la lista original
    patios.append({"name": patio_name, "direccion": address})
    todo["patios"] = patios # Actualizamos la sección en el objeto maestro
    
    save_master(todo)
    return True, "Agregado con éxito"

def delete_patio(patio_name):
    todo = cargar_todo()
    patios_viejos = todo.get("patios", [])
    
    # Filtramos la lista
    patios_nuevos = [p for p in patios_viejos if p.get("name", "").lower() != patio_name.lower()]
    
    if len(patios_viejos) == len(patios_nuevos):
        return False, "No se encontró el patio."

    todo["patios"] = patios_nuevos
    save_master(todo)
    return True, "Eliminado con éxito"

def crear_capa():#tamano_pagina, fields, datos
    """funcion para extaer las coordenadas de las plantillas dependiendo de 
    la plantilla seleccionada"""
    solicitudes = [patios for patios in cargar_todo().get("solicitud", {}).values()]

    


crear_capa()

