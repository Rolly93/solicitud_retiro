import json
from pathlib import Path

#from data import cargar_todo , update_file
from core.data import cargar_todo , update_file
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

    def obtener_direccion (self, patio: str) ->list[str]:
        """"funcion para obtener el estado y direccion
        str: estado
        str: municipio"""
        
        direc = self._dict_patios()
        yard = patio.upper()
        direccion = direc[yard]
        split_address = direccion.split("+")
        estado = split_address[1]
        direccion = split_address[0]
        
        
        format =""
        for i ,char in enumerate(direccion):
            if i ==27:
                format = f"{format+ char}\n"
            else:   
                format = format + char

        return [estado , format]
    

    def _dict_patios(self)->dict[str:str]:
        
        dict_yard= {
            nombre.get("nombre_patio").upper(): f"{nombre.get("calle").upper()} + {nombre.get("estado").upper()}" 
            
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
    
    def get_coord(self,destino:str , name :str)->list:
        """
        Funcion par extraer las coordenadas de las plantillas dependiendo de la plantilla seleccionada
        
        """
        solicitudes = (patios for patios in cargar_todo()["solicitud"].items())

        for solicitud ,coodr  in solicitudes:
            is_requested = solicitud == destino
            if is_requested:
                for cord in coodr["fields"]:
                    if cord["name"] == name:

                        return [cord["x"] , cord["y"]]
        return [None,None]
    
    def validar_Referencia(self,referecia:str) ->bool:
        count = len(referecia)
        ref= referecia.upper()
        count == 10 and (ref.startswith("92B") or ref.startswith("82B"))
        if not count:
            raise ValueError (f"Referencia: \n{ref} es invalida")
        return True
        
    def insert_new_address (sefl,name:str,calle:str,estado:str)->None:
        
        if "patios" not in sefl._all_data:
            sefl._all_data["patios"] = []
        if sefl.does_exist(name
                           ,calle
                           ,"patios",
                           "nombre_patio",
                           "calle",):
            raise ValueError  (f"El Patio {name} ya existe en el registro")
        
        new_yard ={
            "nombre_patio":name,
            "calle":calle,
            "estado":estado
        }
        sefl._all_data["patios"].append(new_yard)
        
        update_file(sefl._all_data)
    def insert_new_transfer(self,transfername:str=None, scac:str = None)->None:
        
   
        if "linea_transporte" not in self._all_data:
            self._all_data["linea_transporte"] = []

        if self.does_exist(transfername,scac,"linea_transporte","name","scac")  :
            print("Transfer Duplicado")
            return
        
        new_transfer ={
            "name":transfername,
            "scac":scac
        }
        
        self._all_data["linea_transporte"].append(new_transfer)
        
        update_file(self._all_data)
    
    def does_exist(self, key:str , value:str , main_key:str , dict_key:str , dict_value:str)-> bool:
        
        is_duplicate1 = any(
            item[f"{dict_key}"].lower() == key.lower().strip()
            for item in self._all_data[f"{main_key}"])
        
        is_duplicate2= any(
            item[f"{dict_value}"].upper() == value.upper().strip()
                           for item in self._all_data[f"{main_key}"])
        
        if is_duplicate1 or is_duplicate2:
            return True
        return False
    



