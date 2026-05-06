# AutoJob 🚀

Herramienta CLI para automatizar postulaciones de empleo en diversas plataformas (OCC, LinkedIn, Indeed, etc.) utilizando Python y Playwright.

## Características
- **Multi-plataforma:** Arquitectura escalable para soportar diferentes portales de empleo.
- **Gestión de Sesión:** Inicia sesión manualmente una vez y el bot recordará tu sesión para evitar CAPTCHAs.
- **Omisión Inteligente:** Detecta vacantes con formularios complejos o preguntas adicionales y las omite para un flujo 100% automático.
- **Log de Actividad:** Registro detallado de todas tus postulaciones en un archivo CSV.

## Requisitos
- Python 3.10+
- Playwright

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/AldoZM/AutoJob.git
   cd AutoJob
   ```

2. Crear entorno virtual e instalar dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```

## Uso

1. **Login:** Necesario la primera vez para cada plataforma.
   ```bash
   python main.py login --platform occ
   ```

2. **Postularse:**
   ```bash
   python main.py apply --search "Desarrollador Python" --location "Remoto" --limit 20
   ```

## Contribución
Este es un proyecto Open Source. Si quieres añadir soporte para una nueva plataforma:
1. Crea un archivo `tuplataforma_bot.py`.
2. Hereda de `BaseBot` en `base_bot.py`.
3. Implementa los métodos abstractos.
4. Regístralo en `main.py`.

## Licencia
MIT
