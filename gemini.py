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
    
    def process_authorization(self, current_date:str, date_afiliation:str, suggested_procedure:str, medical_report:str, policy_data:str) -> dict:
        prompt = f"""
            ROLE:
            ---
            Actúa como un Auditor Médico experto en pre-autorizaciones quirúrgicas. Tu objetivo es decidir instantáneamente si una cirugía procede basándote en datos técnicos.
            ---
            CONTEXTO:
            ---
            Fecha de Hoy: {current_date}
            ---
            Fecha de Afiliación del Paciente: {date_afiliation}
            ---
            Procedimiento Solicitado: {suggested_procedure}
            ---
            Informe Médico del Hospital: {medical_report}
            ---
            Póliza de la Aseguradora: {policy_data} 
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
            {{
                "estado": "APROBADO" | "RECHAZADO" | "PENDIENTE_DOCUMENTOS",
                "justificacion": "Breve explicación técnica",
                "documentos_faltantes": ["lista", "de", "strings"]
            }}
        """
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            return {"error": f"Error en el procesamiento de Gemini: {str(e)}"}

if __name__ == "__main__":
    API_KEY = os.getenv("GEMINI_API_KEY")
    agent = PreAuthAgent(API_KEY)
    fecha_actual = "14 de mayo de 2026"
    data_notion_fecha_afiliacion = "10 de enero de 2024"
    data_notion_procedimiento = "Apendicectomía de urgencia."
    data_notion_informe = "Paciente ingresa con dolor agudo en fosa ilíaca derecha, náuseas y fiebre. Ecografía abdominal muestra apéndice inflamado de 10mm. Se requiere intervención quirúrgica inmediata por riesgo de peritonitis."
    data_notion_poliza = "Cobertura integral para cirugías generales, incluyendo apendicectomía, hernias y vesícula. Periodo de carencia: 180 días para cirugías programadas; urgencias están cubiertas desde el primer día."
    resultado = agent.process_authorization(fecha_actual, data_notion_fecha_afiliacion, data_notion_procedimiento, data_notion_informe, data_notion_poliza)
    print(json.dumps(resultado, indent=2))