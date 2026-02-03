import json
from pathlib import Path

from core.data import cargar_todo , update_file
#from data import cargar_todo
class DataManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.asset_dir = self.base_dir / "assets"
        self.config_path = self.base_dir / "config" / "templates.json"
        self._all_data= cargar_todo()
        
        self.list_solicitud = self.obtener_lista_solicitudes()
        self.list_yard = self.obtener_nombres_patios()
        self.get_data_transfer = self.obtener_transfer()
        self.list_tipo_unidad = self.obtener_tipo_unidad()
        
        
    def obtener_lista_solicitudes (self)-> list:
        solicitudes = {str(nombre).replace("-"," ").upper()  
                       for nombre , ruta in 
                       self._all_data.get("solicitud" , {}).items()} 
        

        return sorted(solicitudes)        

    def _dict_solicitudes(self)-> dict:
        
        dict_soli ={ 
            nombre:
            str(self.asset_dir / ruta.get("filename")) 
            for nombre , ruta in   self._all_data.get("solicitud",{}).items()}
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
                  self._all_data.get("patios",{})}
        return sorted(dict_yard)

    def obtener_direccion (self, patio: str) ->str :
        direc = self._dict_patios()
        yard = patio.upper()
        direccion = direc[yard]

        print(direccion)
        
        return direccion

    def _dict_patios(self)->dict[str:str]:
        
        dict_yard= {
            nombre.get("nombre_patio").upper(): nombre.get("direccion").upper()
            
                  for nombre in 
                  self._all_data.get("patios")}       
        
        
        return dict_yard

    def obtener_transfer(self) ->list:
        transfer_data = [transfer.get("name").upper() 
                         for transfer in self._all_data.get("linea_transporte")]
        
        return transfer_data
    
    def _dict_linea_trasnfer(self)->dict:
        dic_transfer = {
            name.get("name") : name.get("scac")
            for name in self._all_data["linea_transporte"]
        }
        return dic_transfer
        
    def get_transfer_scac(self, transfer_name :str) ->str:
        
        nombre = transfer_name.lower()
        scac = self._dict_linea_trasnfer()[nombre]
        
        
        return scac.upper()
    
    def _dict_tipo_request(self,request_input:str)->dict[str,list[dict,str]]:
        
        inputs = {
            
            unidad:campos 
            for unidad , campos in
            self._all_data["unidad"][request_input].items()
        }        
        return inputs
    
    def request_input_type_unit(self, tipo_unidad :str)->dict[str,list]:
        inptus = self._dict_tipo_request(tipo_unidad.lower())
        
        return inptus
        
        
        
    
    def obtener_tipo_unidad(self)->list[str]:
        tipo_unidad = [unidad.upper()
                       for unidad in
                       self._all_data["unidad"]]
        
        return tipo_unidad
    
    def insert_new_transfer(self,transfername:str=None, scac:str = None)->None:
        
   
        if "linea_transporte" not in self._all_data:
            self._all_data["linea_transporte"] = []
            
        existe_nombre = any(item["name"].lower() == transfername.lower() for item in self._all_data["linea_transporte"])
        existe_scac = any(item["scac"].upper() == scac.upper() for item in self._all_data["linea_transporte"])
        
        if existe_scac or existe_nombre  :
            print("Transfer Duplicado")
            return
        
        new_transfer ={
            "name":transfername,
            "scac":scac
        }
        
        self._all_data["linea_transporte"].append(new_transfer)
        
        update_file(self._all_data)
    
    def does_exist(self, v1 , v2):
        
        is_duplicate1 = any(item["name"].lower() == v1.lower() for item in self._all_data["linea_transporte"])
        is_duplicate2= any(item["scac"].upper() == v2.upper() for item in self._all_data["linea_transporte"])
        
        if is_duplicate1 == is_duplicate2:
            return True
        return False
data = DataManager()
