# -*- coding: utf-8 -*-
"""
data.py
Persistencia en CSV + utilidades de rutas para que SIEMPRE busque archivos
en la MISMA carpeta del programa (.exe) o raíz del repo en desarrollo.
No usa sys._MEIPASS para recursos externos (PDFs, CSVs).

Genera/usa estos CSVs en ./config:
  - templates_solicitudes.csv  (plantilla, filename, campo, x, y)
  - templates_unidades.csv     (tipo_unidad, nombre_campo, etiqueta)
  - patios.csv                 (columnas dinámicas)
  - lineas.csv                 (columnas dinámicas)

APIs:
  - cargar_todo() -> dict
  - get_coord(destino: str, name: str) -> list[x,y] | [None,None]
  - update_file(new_data: dict) -> bool
  - get_pdf_path(filename: str) -> Path   # SIEMPRE en ./assets/<filename>
  - json_to_csv()                         # migración opcional desde templates.json
  - inicializar_datos()                   # crea CSVs si faltan
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

# ==========================================================
# 1) RUTAS ROBUSTAS: SIEMPRE JUNTO AL .EXE (o raíz del repo)
# ==========================================================

def get_base_path() -> Path:
    """
    Devuelve la carpeta donde vive el .exe (PyInstaller) o la raíz de tu proyecto (dev).
    Recomendación: colocar ./config y ./assets junto al .exe o a la raíz del repo.
    """
    if getattr(sys, "frozen", False):
        # Ejecutable generado por PyInstaller
        return Path(sys.executable).parent
    # En desarrollo, ajusta si necesitas subir más/menos niveles
    return Path(__file__).resolve().parent.parent

def resolve_external(*parts: str) -> Path:
    """
    Recurso EXTERNO (editable) que debe estar junto al .exe o al script.
    NO usa sys._MEIPASS. Úsalo para CSVs y PDFs.
    """
    return get_base_path().joinpath(*parts)

def get_json_resource_path() -> Path:
    """
    Ruta al JSON base solo si lo mantienes para migración.
    También se busca JUNTO al .exe (./config/templates.json).
    """
    return resolve_external("config", "templates.json")

# --- Rutas principales ---
FOLDER_PATH = resolve_external("config")

SOLICITUDES_CSV = FOLDER_PATH / "templates_solicitudes.csv"
UNIDADES_CSV    = FOLDER_PATH / "templates_unidades.csv"
PATIOS_CSV      = FOLDER_PATH / "patios.csv"
LINEAS_CSV      = FOLDER_PATH / "lineas.csv"

JSON_PATH       = get_json_resource_path()  # opcional (migración)

# ==========================================================
# 2) UTILIDADES CSV
# ==========================================================

def _ensure_folder() -> None:
    if not FOLDER_PATH.exists():
        FOLDER_PATH.mkdir(parents=True, exist_ok=True)

def _read_csv_safe(path: Path, columns: List[str]) -> pd.DataFrame:
    """
    Lee CSV con columnas esperadas. Si no existe o está vacío, regresa DF vacío.
    """
    try:
        if not path.exists() or path.stat().st_size == 0:
            return pd.DataFrame(columns=columns)
        df = pd.read_csv(path, encoding="utf-8")
        # Asegurar columnas esperadas
        for col in columns:
            if col not in df.columns:
                df[col] = pd.NA
        return df[columns]
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=columns)
    except Exception as e:
        print(f"[WARN] No se pudo leer {path}: {e}")
        return pd.DataFrame(columns=columns)

# ==========================================================
# 3) MIGRACIÓN OPCIONAL: JSON -> CSV
# ==========================================================

def json_to_csv() -> None:
    """
    Convierte el archivo JSON base a 4 CSVs (Solicitudes, Unidades, Patios, Lineas).
    NO usa sys._MEIPASS. Busca templates.json en ./config (junto al .exe).
    """
    _ensure_folder()

    if not JSON_PATH.exists():
        print(f"Info: No se encontró JSON base en {JSON_PATH}. Se omite migración.")
        # Si no hay JSON, al menos asegurar CSVs vacíos
        if not SOLICITUDES_CSV.exists():
            pd.DataFrame(columns=["plantilla","filename","campo","x","y"]).to_csv(SOLICITUDES_CSV, index=False, encoding="utf-8")
        if not UNIDADES_CSV.exists():
            pd.DataFrame(columns=["tipo_unidad","nombre_campo","etiqueta"]).to_csv(UNIDADES_CSV, index=False, encoding="utf-8")
        if not PATIOS_CSV.exists():
            pd.DataFrame(columns=[]).to_csv(PATIOS_CSV, index=False, encoding="utf-8")
        if not LINEAS_CSV.exists():
            pd.DataFrame(columns=[]).to_csv(LINEAS_CSV, index=False, encoding="utf-8")
        return

    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # ----- Solicitudes -----
        solicitud_list = []
        for template_name, content in (data.get('solicitud') or {}).items():
            for field in (content.get('fields') or []):
                solicitud_list.append({
                    "plantilla": template_name,
                    "filename":  content.get('filename'),
                    "campo":     field.get('name'),
                    "x":         field.get('x'),
                    "y":         field.get('y'),
                })
        pd.DataFrame(solicitud_list, columns=["plantilla","filename","campo","x","y"]).to_csv(
            SOLICITUDES_CSV, index=False, encoding="utf-8"
        )

        # ----- Unidades -----
        unidades_list = []
        for tipo, content in (data.get('unidad') or {}).items():
            for field in (content.get('fields') or []):
                unidades_list.append({
                    "tipo_unidad":  tipo,
                    "nombre_campo": field.get('name'),
                    "etiqueta":     field.get('label'),
                })
        pd.DataFrame(unidades_list, columns=["tipo_unidad","nombre_campo","etiqueta"]).to_csv(
            UNIDADES_CSV, index=False, encoding="utf-8"
        )

        # ----- Patios y Líneas -----
        pd.DataFrame(data.get('patios', [])).to_csv(PATIOS_CSV, index=False, encoding="utf-8")
        pd.DataFrame(data.get('linea_transporte', [])).to_csv(LINEAS_CSV, index=False, encoding="utf-8")

        print(f"CSVs generados exitosamente en: {FOLDER_PATH}")
    except Exception as e:
        print(f"Error al convertir JSON a CSV: {e}")

def inicializar_datos() -> None:
    """
    Asegura que existan ./config y los CSVs.
    Si TODOS faltan, intenta generarlos desde ./config/templates.json (si existe).
    Si faltan algunos, crea CSVs vacíos con sus columnas.
    """
    _ensure_folder()
    all_paths = [SOLICITUDES_CSV, UNIDADES_CSV, PATIOS_CSV, LINEAS_CSV]
    if not any(p.exists() for p in all_paths):
        # Intentar hidratar desde JSON local (junto al .exe)
        json_to_csv()
    else:
        # Crear vacíos cuando falten
        if not SOLICITUDES_CSV.exists():
            pd.DataFrame(columns=["plantilla","filename","campo","x","y"]).to_csv(SOLICITUDES_CSV, index=False, encoding="utf-8")
        if not UNIDADES_CSV.exists():
            pd.DataFrame(columns=["tipo_unidad","nombre_campo","etiqueta"]).to_csv(UNIDADES_CSV, index=False, encoding="utf-8")
        if not PATIOS_CSV.exists():
            pd.DataFrame(columns=[]).to_csv(PATIOS_CSV, index=False, encoding="utf-8")
        if not LINEAS_CSV.exists():
            pd.DataFrame(columns=[]).to_csv(LINEAS_CSV, index=False, encoding="utf-8")

# ==========================================================
# 4) API PRINCIPAL (igual a tu flujo)
# ==========================================================

def cargar_todo() -> Dict[str, Any]:
    """
    Carga los CSV y reconstruye el diccionario original para el programa.
    Devuelve: {"solicitud": {...}, "unidad": {...}, "patios": [...], "linea_transporte": [...]}
    """
    try:
        # ----- Solicitudes -----
        df_sol = _read_csv_safe(SOLICITUDES_CSV, ["plantilla","filename","campo","x","y"])
        sol_dict: Dict[str, Any] = {}
        if not df_sol.empty:
            for c in ("x","y"):
                df_sol[c] = pd.to_numeric(df_sol[c], errors="coerce")
            for plantilla in df_sol['plantilla'].dropna().unique():
                df_t = df_sol[df_sol['plantilla'] == plantilla]
                filename = df_t.iloc[0]['filename'] if "filename" in df_t.columns else None
                fields = df_t[['campo','x','y']].rename(columns={'campo':'name'}).to_dict('records')
                sol_dict[plantilla] = {"filename": filename, "fields": fields}

        # ----- Unidades -----
        df_uni = _read_csv_safe(UNIDADES_CSV, ["tipo_unidad","nombre_campo","etiqueta"])
        uni_dict: Dict[str, Any] = {}
        if not df_uni.empty:
            for t in df_uni['tipo_unidad'].dropna().unique():
                df_t = df_uni[df_uni['tipo_unidad'] == t]
                fields = df_t[['nombre_campo','etiqueta']].rename(
                    columns={'nombre_campo':'name','etiqueta':'label'}
                ).to_dict('records')
                uni_dict[t] = {"fields": fields}

        # ----- Patios y Líneas -----
        # Para conservar columnas dinámicas: detectamos encabezados si existen
        def _read_dynamic_csv(path: Path) -> pd.DataFrame:
            if not path.exists() or path.stat().st_size == 0:
                return pd.DataFrame(columns=[])
            try:
                head_cols = list(pd.read_csv(path, nrows=0).columns)
            except Exception:
                head_cols = []
            return _read_csv_safe(path, head_cols)

        df_patios = _read_dynamic_csv(PATIOS_CSV)
        df_lineas = _read_dynamic_csv(LINEAS_CSV)

        return {
            "solicitud": sol_dict,
            "unidad": uni_dict,
            "patios": df_patios.to_dict('records'),
            "linea_transporte": df_lineas.to_dict('records')
        }
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return {"solicitud": {}, "unidad": {}, "patios": [], "linea_transporte": []}

def get_coord(destino: str, name: str) -> List[Any]:
    """
    Extrae coordenadas X, Y desde templates_solicitudes.csv.
    Uso:
        get_coord("Retiro", "Campo1") -> [x, y] o [None, None]
    """
    try:
        df = _read_csv_safe(SOLICITUDES_CSV, ["plantilla","filename","campo","x","y"])
        if df.empty:
            return [None, None]
        for c in ("x","y"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
        filtro = df[(df['plantilla'] == destino) & (df['campo'] == name)]
        if not filtro.empty:
            return [filtro.iloc[0]['x'], filtro.iloc[0]['y']]
    except Exception as e:
        print(f"Error en get_coord: {e}")
    return [None, None]

def update_file(new_data: Dict[str, Any]) -> bool:
    """
    Guarda los cambios del programa en los archivos CSV.
    Estructura esperada:
      {
        "solicitud": {
          "PlantillaA": {
            "filename": "tnl-solicitud-retiro.pdf",
            "fields": [{"name":"Campo1","x":100,"y":200}, ...]
          },
          ...
        },
        "unidad": {
          "3.5T": {"fields":[{"name":"placas","label":"PLACAS"}, ...]},
          ...
        },
        "patios": [ ... ],
        "linea_transporte": [ ... ]
      }
    """
    try:
        _ensure_folder()

        # ----- Solicitudes -----
        rows_s = []
        for plantilla, content in (new_data.get('solicitud') or {}).items():
            filename = (content or {}).get('filename')
            for f in (content or {}).get('fields', []):
                rows_s.append({
                    "plantilla": plantilla,
                    "filename":  filename,
                    "campo":     f.get('name'),
                    "x":         f.get('x'),
                    "y":         f.get('y'),
                })
        pd.DataFrame(rows_s, columns=["plantilla","filename","campo","x","y"]).to_csv(
            SOLICITUDES_CSV, index=False, encoding="utf-8"
        )

        # ----- Unidades -----
        rows_u = []
        for tipo, content in (new_data.get('unidad') or {}).items():
            for f in (content or {}).get('fields', []):
                rows_u.append({
                    "tipo_unidad":  tipo,
                    "nombre_campo": f.get('name'),
                    "etiqueta":     f.get('label'),
                })
        pd.DataFrame(rows_u, columns=["tipo_unidad","nombre_campo","etiqueta"]).to_csv(
            UNIDADES_CSV, index=False, encoding="utf-8"
        )

        # ----- Patios y Líneas -----
        pd.DataFrame(new_data.get('patios', [])).to_csv(PATIOS_CSV, index=False, encoding="utf-8")
        pd.DataFrame(new_data.get('linea_transporte', [])).to_csv(LINEAS_CSV, index=False, encoding="utf-8")

        return True
    except Exception as e:
        print(f"Error al guardar CSVs: {e}")
        return False

# ==========================================================
# 5) RUTA DEL PDF (SIEMPRE JUNTO AL .EXE)
# ==========================================================

def get_pdf_path(filename: str) -> Path:
    """
    Devuelve la ruta del PDF desde ./assets/<filename>, SIEMPRE juntito al .exe.
    No usa sys._MEIPASS. Úsalo para cargar tus plantillas PDF.
    Lanza FileNotFoundError con un mensaje claro si no existe.
    """
    pdf_path = resolve_external("assets", filename)
    if not pdf_path.exists():
        raise FileNotFoundError(
            f"No se encontró el PDF en la carpeta del programa:\n{pdf_path}\n"
            "Asegúrate de que exista './assets/<filename>' junto al ejecutable."
        )
    return pdf_path

