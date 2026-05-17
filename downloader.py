import os
import requests

def download_informe(url, item_id):
    output_dir = "informes_descargados"
    os.makedirs(output_dir, exist_ok=True)
    if not url:
        print(f"Saltado: El registro con ID {item_id} no tiene un enlace de informe.")
        return
    try:
        file_name = f"informe_{item_id}.pdf"
        file_path = os.path.join(output_dir, file_name)
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(file_path, "wb") as pdf_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        pdf_file.write(chunk)
            print(f"Éxito: Descargado correctamente -> {file_name}")
        else:
            print(f"Error: No se pudo descargar el ID {item_id}. Código HTTP: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error de red al descargar el ID {item_id}: {e}")
    except Exception as e:
        print(f"Error: Ocurrió un error inesperado con el ID {item_id}: {e}")