# Sistema de Pre-Autorización de Procedimientos Médicos con Notion ft. Gemini

Automatiza la revisión de solicitudes médicas almacenadas en Notion. El proyecto toma los casos pendientes, descarga el informe médico en PDF, lo envía a Gemini junto con los datos de la póliza y escribe el resultado de vuelta en la página de Notion.

## 🚀 ¡Prúebalo ahora!
1. Accede a este formulario: [Formulario en Notion](https://easy-enquiry-0b2.notion.site/363e10c619518087ac15d71f1b22edf9)
2. Verifica la actualización en la base de datos: [Base de datos en Notion](https://easy-enquiry-0b2.notion.site/361e10c6195180f999d0e4cabd3f6b99?v=361e10c6195180af8116000c63a24af5)

> [!NOTE]
> La pestaña de la base de datos no se actualiza en tiempo real ¡Recarga la pestaña!

3. Espera y observa la magia! ✨✨

## Qué hace

- Consulta una base de datos de seguros para construir el mapa de pólizas.
- Consulta una base de casos en Notion y filtra solo los registros con estado `Pendiente`.
- Descarga el informe médico asociado a cada caso.
- Envía el PDF y los datos del caso a Gemini para obtener una decisión de preautorización.
- Actualiza la página de Notion con el estado y la justificación generada por IA.
- Limpia los PDF descargados al final del proceso.

## Flujo general

1. El script lee las credenciales desde el archivo `.env`.
2. Consulta la base de datos de pólizas en Notion.
3. Consulta la base de casos y selecciona los registros pendientes.
4. Descarga el archivo adjunto del informe médico.
5. Llama a Gemini con las reglas de negocio definidas en el código.
6. Actualiza la página de Notion con la respuesta final.

## Requisitos

- Python instalado.
- Una cuenta y una integración de Notion con acceso a las bases de datos.
- Una API key de Gemini.
- Conexión a internet para consultar Notion, descargar PDFs y usar Gemini.

## Instalación

1. Crea y activa un entorno virtual.
2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto con estas variables:

```env
NOTION_TOKEN=tu_token_de_notion
DATASOURCE_ID=id_de_la_base_de_casos
SEGUROSDS_ID=id_de_la_base_de_seguros
GEMINI_API_KEY=tu_api_key_de_gemini
```

## Estructura esperada en Notion

El código asume que existen estas propiedades en la base de casos:

- `Estado`: selector con al menos el valor `Pendiente`.
- `Informe Medico`: archivo con el PDF adjunto.
- `Procedimiento Sugerido`: texto enriquecido.
- `Fecha de Afiliacion`: fecha.
- `Poliza del Seguro`: relación con la base de seguros.

En la base de seguros se espera una propiedad llamada `Póliza` con el nombre o descripción de la cobertura.

## Uso

### Ejecución directa

Procesa los casos pendientes ejecutando el script principal:

```bash
python main.py
```

### Servicio web

También puedes exponer un endpoint HTTP con FastAPI:

```bash
uvicorn backend:app --host 0.0.0.0 --port 8000
```

Luego dispara el procesamiento con una petición `POST` a:

`/notion-trigger`

## Respuesta de la IA

El flujo actual está pensado para que Gemini devuelva un JSON con esta forma:

```json
{
	"estado": "PREAPROBADO",
	"justificacion": "Breve explicación técnica de la decisión tomada"
}
```

Si el estado resultante no coincide con `PREAPROBADO` o `RECHAZADO`, el script no actualiza la página.

## Configuración interna

- Modelo usado: `gemini-2.5-flash`.
- Versión de Notion API: `2026-03-11`.
- Los PDFs se guardan temporalmente en `informes_descargados/`.
- Entre casos se espera 60 segundos antes de procesar el siguiente.

## Estructura del proyecto

```text
main.py               # Lógica principal de consulta, análisis y actualización en Notion
backend.py            # API FastAPI con el endpoint /notion-trigger
downloader.py         # Descarga y almacenamiento temporal de informes médicos
gemini.py             # Cliente y lógica de preautorización con Gemini
page_edit.py          # Actualización de páginas de Notion con el resultado
informes_descargados/ # PDFs temporales generados durante la ejecución
```

## Notas

- El proyecto elimina los PDFs descargados al terminar el procesamiento.
- Si una página no tiene informe médico, la descarga se omite para ese caso.
- Si una respuesta de IA no contiene `page_id`, no se realiza la actualización en Notion.

## Autores
Este proyecto fue realizado por miembros del Club de Inteligencia Artificial Politécnico (CIAP) de ESPOL
- Darwin Diaz
- Jaren Pazmiño
- David Sandoval

<img alt="Logo_CIAP (Tortuga y letras) 2" src="https://github.com/user-attachments/assets/3cc8c7d2-f1ac-4a31-9407-87263e2d8557" />