import os
#from dotenv import load_dotenv
import time
import time
import asyncio
import subprocess
class EdocCommand: 
    def __init__(self):
        #load_dotenv()
     
        self._edoc = r"C:\Program Files (x86)\Expeditors\e.doc\edoc Viewer\edocViewer.exe" #os.getenv("EDOC_VIEWER_PATH")

    async    def _subir_edoc(self, ruta_archivo, referencia, key_type, document_type):
            ruta_abs = os.path.abspath(ruta_archivo)
            
            if not self._edoc:
                raise ValueError("Error: No se encontró la ruta de Edoc en las variables de entorno (.env)")


            if not os.path.exists(ruta_archivo):
                raise FileNotFoundError(f"No se encontró el archivo: {ruta_abs}")

            


            args = [
                self._edoc,
                "-c:upload",
                ruta_abs,
                f"-k:{referencia}",
                f"-y:{key_type}",
                f"-d:{document_type}"
            ]

            try:
                process = await asyncio.create_subprocess_exec(
                    self._edoc,
                    *args,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                try:
                    stdout , stderr = await asyncio.wait_for(process.communicate(),timeout=30)
                    
                    if process.returncode == 0:
                        print(f"Archivo{referencia} Procesado Correctamente")
                    else:
                        error_msg = stderr.decode().strip()
                        raise Exception(f"edcoViewer devolvio error: {error_msg}")
                except asyncio.TimeoutError:
                    process.kill()
                    raise Exception("El proceso de e.doc exedio el tiempo de espera")
                

    
            except subprocess.CalledProcessError as e:
                raise Exception(f"Error en edocViewer: {e.stderr}")
            except Exception as e:
                raise Exception(f"Error inesperado: {e}")

    async    def command (sefl , ruta_doc):

                file_name = os.path.basename(ruta_doc)
                fn = file_name.split("_")
                dcotype = f"{str(fn[0]).capitalize()} {str(fn[1]).capitalize()}"
                print(dcotype)
                if "Solicitud Retiro" in dcotype:
                    dcotype = "Solicitud de Retiro"

                ref = str(fn[2]).upper().replace(".PDF","")
                keytype = "EDMS"

                await sefl._subir_edoc(ruta_doc , ref , keytype  , dcotype)

        
            
        