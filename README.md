# 📦 Sistema de Gestión de Solicitudes de Retiro (WWS)

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Producción-green?style=for-the-badge)
![UI](https://img.shields.io/badge/UI-PySide6-orange?style=for-the-badge)
![Focus](https://img.shields.io/badge/Focus-Logística_%26_Automatización-green?style=for-the-badge)

## 📋 Descripción General
Esta solución de software está diseñada para **automatizar y estandarizar el proceso de solicitudes de retiro de mercancía** en un entorno de almacén y aduanas. 

El sistema elimina la captura manual de datos, asegura la integridad de la información mediante validaciones en tiempo real y reduce drásticamente los tiempos de despacho al integrar la generación de documentos con la subida automática a plataformas digitales mediante comandos externos.

## 🚀 Funcionalidades Clave
* **Generación de Documentación:** Creación automática de 3 archivos PDF (Solicitud de Retiro, Checklist y Delivery Order) con datos validados.
* **Automatización e.doc:** Integración asíncrona con `edocViewer.exe` para la carga automática de expedientes a la plataforma digital.
* **Calibración Dinámica:** Herramienta integrada para obtener coordenadas (X, Y) en milímetros haciendo clic sobre el PDF, facilitando la edición de plantillas.
* **Gestión de Catálogos:** Persistencia de datos en CSV para Patios de maniobras y Líneas de transporte.
* **Interfaz Moderna:** GUI desarrollada con PySide6 que garantiza una experiencia de usuario fluida y sin bloqueos gracias al manejo de hilos con `asyncio`.

## 🛠 Tecnologías Utilizadas
* **Lenguaje:** Python 3.10+
* **Interfaz Gráfica:** PySide6 (Qt for Python).
* **Motor PDF:** PyMuPDF (Fitz) para manipulación, renderizado e inserción de texto en documentos.
* **Procesamiento Asíncrono:** `asyncio` para la ejecución de comandos de terminal sin congelar la UI.
* **Persistencia:** Almacenamiento local en CSV gestionado con rutas relativas robustas.

## 📂 Estructura del Proyecto
```
├── core/               # Lógica de negocio
│   ├── data.py         # Gestión de persistencia y rutas relativas
│   ├── pdf_service.py  # Manipulación de PDFs y lógica de coordenadas
│   └── edoc_command.py # Integración asíncrona con e.doc Viewer
├── ui/                 # Componentes de la interfaz de usuario
│   ├── main_ui.py      # Diseño principal de la ventana
│   └── popout.py       # Controladores de formularios secundarios
├── assets/             # Plantillas PDF y recursos visuales
├── config/             # Archivos de configuración y catálogos (CSV)
└── main.py             # Punto de entrada de la aplicación
```

1.  Clonar el repositorio:
    ```bash
    git clone [https://github.com/Rolly93/solicitud_retiro.git](https://github.com/Rolly93/solicitud_retiro.git)
    ```
2.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Ejecutar la aplicación:
    ```bash
    python main.py


## 📈 Impacto Esperado
Con la implementación de esta herramienta, se proyecta:

*    Reducción de Tiempo: Ahorro estimado de **30 minutos por cada ciclo de solicitud** procesado.
*    Error Cero: Eliminación del **90% de errores de captura** en números de pedimento y guías de transporte.
*    Estandarización: Formatos uniformes y procesos digitales **alineados con los requerimientos aduaneros**.



---
**Desarrollado por [Rolando Rios](https://www.linkedin.com/in/rolando-guadalupe-rios-lopez-14090623b/)** *Ingeniero en Sistemas enfocado en Soluciones Logísticas.*

