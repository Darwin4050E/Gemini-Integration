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
    
    def process_authorization(self, current_date:str, date_afiliation:str, suggested_procedure:str, medical_report_path:str, policy_data_path:str) -> dict:
        if not os.path.exists(medical_report_path) or not os.path.exists(policy_data_path):
            return {"error": f"Error de infraestructura: Uno o ambos archivos PDF no existen en las rutas proporcionadas."}
        uploaded_report = None
        uploaded_policy = None
        try:
            uploaded_report = genai.upload_file(medical_report_path, mime_type="application/pdf")
            uploaded_policy = genai.upload_file(policy_data_path, mime_type="application/pdf")
            contents = [
                "ROLE:\n---\nActúa como un Auditor Médico experto en pre-autorizaciones quirúrgicas. Tu objetivo es decidir instantáneamente si una cirugía procede basándote en datos técnicos.\n---",
                "CONTEXTO METADATOS:\n---",
                f"Fecha de Hoy: {current_date}",
                f"Fecha de Afiliación del Paciente: {date_afiliation}",
                f"Procedimiento Solicitado: {suggested_procedure}\n---",
                "DOCUMENTO 1: INFORME MÉDICO DEL HOSPITAL (Analiza el siguiente PDF adjunto):",
                uploaded_report,
                "\nDOCUMENTO 2: PÓLIZA DE LA ASEGURADORA (Analiza el siguiente PDF adjunto):",
                uploaded_policy,
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
            if uploaded_policy:
                uploaded_policy.delete()

if __name__ == "__main__":
    API_KEY = os.getenv("GEMINI_API_KEY")
    agent = PreAuthAgent(API_KEY)
    fecha_actual = "14 de mayo de 2026"
    data_notion_fecha_afiliacion = "10 de enero de 2024"
    data_notion_procedimiento = "Apendicectomía de urgencia."
    ruta_pdf_informe = "informe_medico_urgencias.pdf"
    ruta_pdf_poliza = "poliza_cobertura_medica.pdf"
    if os.path.exists(ruta_pdf_informe) and os.path.exists(ruta_pdf_poliza):
        resultado = agent.process_authorization(
            fecha_actual, 
            data_notion_fecha_afiliacion, 
            data_notion_procedimiento, 
            ruta_pdf_informe, 
            ruta_pdf_poliza
        )
        print(json.dumps(resultado, indent=2))
    else:
        print("Por favor coloca dos archivos PDF válidos en el directorio raíz.")