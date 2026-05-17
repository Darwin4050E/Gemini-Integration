import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

class PreAuthAgent:

    def __init__(self, api_key:str):
        genai.configure(api_key=api_key)
        self.system_instruction = (
            "Eres un Agente de Pre-Autorización Médica experto. Tu tarea es comparar "
            "un informe médico contra una póliza de seguro. "
            "Reglas críticas:\n"
            "1. Verifica periodos de carencia.\n"
            "2. Cruza el código del procedimiento con la cobertura.\n"
            "3. Si falta información, marca el estado como 'PENDIENTE_DOCUMENTOS'.\n"
            "4. Responde ÚNICAMENTE en formato JSON."
        )
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"},
            system_instruction=self.system_instruction
        )
    
    def process_authorization(self, item_id:str, current_date:str, date_afiliation:str, suggested_procedure:str, medical_report_path:str, policy_data:str) -> dict:
        if not os.path.exists(medical_report_path):
            return {"error": f"Error de infraestructura: El archivo PDF no existe en la ruta proporcionada."}
        uploaded_report = None
        try:
            uploaded_report = genai.upload_file(medical_report_path, mime_type="application/pdf")
            contents = [
                "ROLE:\n---\nActúa como un Auditor Médico experto en pre-autorizaciones quirúrgicas. Tu objetivo es decidir instantáneamente si una cirugía procede basándote en datos técnicos.\n---",
                "CONTEXTO METADATOS:\n---",
                f"ID del Caso: {item_id}",
                f"Fecha de Hoy: {current_date}",
                f"Fecha de Afiliación del Paciente: {date_afiliation}",
                f"Procedimiento Solicitado: {suggested_procedure}",
                f"Póliza de la Aseguradora: {policy_data}\n---",
                "DOCUMENTO 1: INFORME MÉDICO DEL HOSPITAL (Analiza el siguiente PDF adjunto):",
                uploaded_report,
                """
                ---
                REGLAS DE NEGOCIO (ESTRICTAS):
                ---
                Carencia: El paciente debe tener más de 180 días de afiliado. Si (Hoy - Fecha de Afiliación) < 180 días, el estado debe ser RECHAZADO por "Periodo de carencia no cumplido".
                ---
                Cobertura: Busca el 'Procedimiento Solicitado' en el texto de la 'Póliza'. Si el procedimiento está en una lista de "Exclusiones" o no figura como beneficio, marca como RECHAZADO.
                ---
                Justificación Médica: El 'Informe Médico' debe mencionar un diagnóstico que sea coherente con la cirugía. Si el informe está incompleto o es vago, marca como FALTAN DATOS. 
                ---
                FORMATO DE SALIDA (Responde solo esto):
                ---
                Analiza los datos y genera el resultado siguiendo este esquema JSON:
                {
                    "estado": "APROBADO" | "RECHAZADO" | "PENDIENTE_DOCUMENTOS",
                    "justificacion": "Breve explicación técnica",
                    "documentos_faltantes": ["lista", "de", "strings"]
                }
                """
            ]
            response = self.model.generate_content(contents)
            return json.loads(response.text)
        except Exception as e:
            return {"error": f"Error en el procesamiento de Gemini: {str(e)}"}
        finally:
            if uploaded_report:
                uploaded_report.delete()