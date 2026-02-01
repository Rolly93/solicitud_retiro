import json
from pathlib import Path

from core.data import cargar_todo

class DataManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.asset_dir = self.base_dir / "assets"
        self.config_path = self.base_dir / "config" / "templates.json"
        
        self.list_solicitud = self.obtener_lista_solicitudes()
        self.list_yard = self.obtener_nombres_patios()
        self.ruta = self.obtener_ruta_solicitud("CFI SOLICITUD RETIRO")
        
    def obtener_lista_solicitudes (self)-> list:
        solicitudes = {str(nombre).replace("-"," ").upper()  
                       for nombre , ruta in 
                       cargar_todo().get("solicitud" , {}).items()} 
        

        return sorted(solicitudes)        

    def _dict_solicitudes(self)-> dict:
        
        dict_soli ={ 
            nombre:
            str(self.asset_dir / ruta.get("filename")) 
            for nombre , ruta in   cargar_todo().get("solicitud",{}).items()}
        return dict_soli

    def obtener_ruta_solicitud(self , solicitud: str)->str :
        soli = solicitud.replace(" ","-").lower()
        
        pdf_formatos = self._dict_solicitudes()

        ruta = pdf_formatos[soli]
        if not ruta:
            raise FileNotFoundError(f"No se encontro el mapeo para la solicitud: {soli}")
        
        return ruta
    
    def obtener_nombres_patios(self)->list:
        dict_yard = {nombre.get("nombre_patio").upper()
                  for nombre in 
                  cargar_todo().get("patios",{})}
        return sorted(dict_yard)

    def obtener_direccion (self, patio: str) ->str :
        direc = self._dict_patios()
        yard = patio.upper()
        direccion = direc[yard]

        print(direccion)
        
        return direccion

    def _dict_patios(self)-> dict:
        
        dict_yard= {
            nombre.get("nombre_patio").upper(): nombre.get("direccion").upper()
            
                  for nombre in 
                  cargar_todo().get("patios")}       
        
        
        return dict_yard


data = DataManager()
data.obtener_direccion("BODEGA LRD")
