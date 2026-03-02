# -*- coding: utf-8 -*-
"""
data.py - VERSIÓN LITE (Sin Pandas)
Optimizado para que el .EXE abra instantáneamente.
"""

import os
import sys
import csv
import json
from pathlib import Path
from typing import List, Dict, Any

# ==========================================================
# 1) RUTAS ROBUSTAS: SIEMPRE JUNTO AL .EXE
# ==========================================================

def get_base_path() -> Path:
    """
    Fuerza la ruta a la carpeta REAL donde el usuario hizo doble clic al .exe,
    ignorando la carpeta temporal de PyInstaller.
    """
    if getattr(sys, "frozen", False):
        # sys.executable es la ruta completa al archivo .exe
        # os.path.dirname obtiene la carpeta que lo contiene
        return Path(os.path.dirname(sys.executable)).absolute()
    
    # En desarrollo (script .py)
    return Path(__file__).resolve().parent.parent

def resolve_external(*parts: str) -> Path:
    """Resuelve rutas de archivos externos editables."""
    return get_base_path().joinpath(*parts)

# --- Configuración de Rutas ---
FOLDER_PATH     = resolve_external("config")
SOLICITUDES_CSV = FOLDER_PATH / "templates_solicitudes.csv"
UNIDADES_CSV    = FOLDER_PATH / "templates_unidades.csv"
PATIOS_CSV      = FOLDER_PATH / "patios.csv"
LINEAS_CSV      = FOLDER_PATH / "lineas.csv"
JSON_PATH       = FOLDER_PATH / "templates.json"  # Para migración inicial
ASSETS_PATH = resolve_external("assets") 

# ==========================================================
# 2) UTILIDADES CSV (NATIVAS Y RÁPIDAS)
# ==========================================================

def _ensure_folder() -> None:
    """Crea la carpeta config si no existe."""
    if not FOLDER_PATH.exists():
        FOLDER_PATH.mkdir(parents=True, exist_ok=True)

def _read_csv_safe(path: Path) -> List[Dict[str, str]]:
    """Lee un CSV usando el módulo nativo. Devuelve lista de dicts."""
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        with open(path, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"[WARN] Error al leer {path.name}: {e}")
        return []

def _write_csv_safe(path: Path, data: List[Dict], fieldnames: List[str]) -> bool:
    """Escribe un CSV de forma segura."""
    _ensure_folder()
    try:
        with open(path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        print(f"[ERROR] Error al escribir {path.name}: {e}")
        return False

# ==========================================================
# 3) MIGRACIÓN OPCIONAL: JSON -> CSV
# ==========================================================

def json_to_csv() -> None:
    """Migra datos de un JSON antiguo a la nueva estructura CSV."""
    if not JSON_PATH.exists():
        # Si no hay JSON, creamos los CSVs con encabezados vacíos
        inicializar_datos()
        return

    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Migrar Solicitudes
        rows_s = []
        for plant, content in (data.get('solicitud') or {}).items():
            fname = content.get('filename')
            for fld in (content.get('fields') or []):
                rows_s.append({
                    "plantilla": plant, "filename": fname,
                    "campo": fld.get('name'), "x": fld.get('x'), "y": fld.get('y')
                })
        _write_csv_safe(SOLICITUDES_CSV, rows_s, ["plantilla", "filename", "campo", "x", "y"])

        # Migrar Unidades
        rows_u = []
        for tipo, content in (data.get('unidad') or {}).items():
            for fld in (content.get('fields') or []):
                rows_u.append({
                    "tipo_unidad": tipo, "nombre_campo": fld.get('name'), "etiqueta": fld.get('label')
                })
        _write_csv_safe(UNIDADES_CSV, rows_u, ["tipo_unidad", "nombre_campo", "etiqueta"])

        # Migrar Patios y Líneas
        patios = data.get('patios', [])
        if patios:
            _write_csv_safe(PATIOS_CSV, patios, list(patios[0].keys()))
        
        lineas = data.get('linea_transporte', [])
        if lineas:
            _write_csv_safe(LINEAS_CSV, lineas, list(lineas[0].keys()))

    except Exception as e:
        print(f"Error en migración: {e}")

def inicializar_datos() -> None:
    """Crea los archivos CSV con sus encabezados si no existen."""
    _ensure_folder()
    files_to_init = [
        (SOLICITUDES_CSV, ["plantilla", "filename", "campo", "x", "y"]),
        (UNIDADES_CSV, ["tipo_unidad", "nombre_campo", "etiqueta"]),
        (PATIOS_CSV, []),
        (LINEAS_CSV, [])
    ]
    for path, headers in files_to_init:
        if not path.exists():
            _write_csv_safe(path, [], headers)

# ==========================================================
# 4) API PRINCIPAL PARA EL PROGRAMA
# ==========================================================

def cargar_todo() -> Dict[str, Any]:
    """Carga los CSV y reconstruye el diccionario esperado por la App."""
    # --- Solicitudes ---
    raw_sol = _read_csv_safe(SOLICITUDES_CSV)
    sol_dict = {}
    for row in raw_sol:
        p = row['plantilla']
        if p not in sol_dict:
            sol_dict[p] = {"filename": row.get('filename'), "fields": []}
        sol_dict[p]["fields"].append({
            "name": row.get('campo'),
            "x": float(row['x']) if row.get('x') and row['x'] != "" else None,
            "y": float(row['y']) if row.get('y') and row['y'] != "" else None
        })

    # --- Unidades ---
    raw_uni = _read_csv_safe(UNIDADES_CSV)
    uni_dict = {}
    for row in raw_uni:
        t = row['tipo_unidad']
        if t not in uni_dict:
            uni_dict[t] = {"fields": []}
        uni_dict[t]["fields"].append({
            "name": row.get('nombre_campo'),
            "label": row.get('etiqueta')
        })

    return {
        "solicitud": sol_dict,
        "unidad": uni_dict,
        "patios": _read_csv_safe(PATIOS_CSV),
        "linea_transporte": _read_csv_safe(LINEAS_CSV)
    }

def get_coord(destino: str, name: str) -> List[Any]:
    """Busca coordenadas específicas sin cargar todo el sistema."""
    data = _read_csv_safe(SOLICITUDES_CSV)
    for row in data:
        if row.get('plantilla') == destino and row.get('campo') == name:
            try:
                return [float(row['x']), float(row['y'])]
            except:
                return [None, None]
    return [None, None]

def update_file(new_data: Dict[str, Any]) -> bool:
    """Guarda el estado actual del programa en los CSVs."""
    try:
        # Guardar Solicitudes
        rows_s = []
        for plant, content in new_data.get('solicitud', {}).items():
            fname = content.get('filename')
            for f in content.get('fields', []):
                rows_s.append({
                    "plantilla": plant, "filename": fname,
                    "campo": f.get('name'), "x": f.get('x'), "y": f.get('y')
                })
        _write_csv_safe(SOLICITUDES_CSV, rows_s, ["plantilla", "filename", "campo", "x", "y"])

        # Guardar Unidades
        rows_u = []
        for tipo, content in new_data.get('unidad', {}).items():
            for f in content.get('fields', []):
                rows_u.append({
                    "tipo_unidad": tipo, "nombre_campo": f.get('name'), "etiqueta": f.get('label')
                })
        _write_csv_safe(UNIDADES_CSV, rows_u, ["tipo_unidad", "nombre_campo", "etiqueta"])

        # Guardar Patios y Líneas (Dinámicos)
        for key, path in [('patios', PATIOS_CSV), ('linea_transporte', LINEAS_CSV)]:
            data_list = new_data.get(key, [])
            headers = list(data_list[0].keys()) if data_list else []
            _write_csv_safe(path, data_list, headers)

        return True
    except Exception as e:
        print(f"Error al guardar: {e}")
        return False

# ==========================================================
# 5) RUTA DEL PDF
# ==========================================================

def get_pdf_path(filename: str) -> Path:
    """Busca el PDF en ./assets/ junto al exe."""
    #pdf_path = resolve_external("assets", filename)
    return ASSETS_PATH / filename
