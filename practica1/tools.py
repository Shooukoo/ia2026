import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class Tools():
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/calendar'
        ]
        self.CREDENTIALS_FILE = "credentials.json"
        self.TOKEN_FILE = "token.json"

    def get_calendar_service(self):
        creds = None
        # Revisar si existe el token y cargarlo
        if os.path.exists(self.TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, self.SCOPES)
        # No hay credenciales validas, hacer proceso de autorizacion o refrescar
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.CREDENTIALS_FILE):
                    raise FileNotFoundError(f"No se encontró el archivo de credenciales!")
                flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_FILE,
                                                                   self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Guardar el token generado
            with open(self.TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        # Regresar el servicio ya hecho
        return build("calendar", "v3", credentials=creds)
    
    def check_availability(self, time_ini, time_end):
        print(f'Llamando a la función check_availability({time_ini} - {time_end})')
        # Crear la variable body para llamar la app de google calendar
        body = {
            "timeMin": time_ini,
            "timeMax": time_end,
            "items": [
                {
                "id": "primary"
                }
            ]
        }
        # Obtener el servicio de Google Calendar
        service = self.get_calendar_service()
        # Realizamos la consulta a Google Calendar
        result = service.freebusy().query(body = body).execute()
        # Obtemer la lista de eventos que coincidan entre "time_ini" y "time_end"
        busy = result.get("calendars", {}).get("primary", {}).get("busy", [])
        # Estructurar la información a un JSON
        return {
            "calendar_id": "primary",
            "time_ini": time_ini,
            "time_end": time_end,
            "busy": busy,
            "is_free": ( len(busy) == 0 ) # Si la lista esta vacia sera "True",  si no "False"
        }

    def create_event(self, summary, time_ini, time_end):
        print(f'Llamando a la función create_event({summary}, {time_ini} - {time_end})')
        # Verificar que el horario esté disponible antes de crear el evento
        availability = self.check_availability(time_ini, time_end)
        if not availability["is_free"]:
            return {
                "error": "El horario solicitado no está disponible",
                "time_ini": time_ini,
                "time_end": time_end,
                "busy": availability["busy"]
            }
        # Crear la variable body para llamar la app de google calendar
        body = {
            "summary": summary,
            "start": {
                "dateTime": time_ini
            },
            "end": {
                "dateTime": time_end
            }
        }
        # Obtener el servicio de Google Calendar
        service = self.get_calendar_service()
        # Crear el evento
        event = service.events().insert(calendarId="primary", body=body).execute()
        # Estructurar la información a un JSON
        return {
            "event_id": event.get("id"),
            "html_link": event.get("htmlLink"),
            "summary": event.get("summary"),
            "time_ini": time_ini,
            "time_end": time_end
        }

    def update_event(self, event_id, summary=None, time_ini=None, time_end=None):
        print(f'Llamando a la función update_event({event_id}, {summary}, {time_ini} - {time_end})')
        # Armar el body solo con los campos que se quieren actualizar
        body = {}
        if summary:
            body["summary"] = summary
        if time_ini:
            body["start"] = {"dateTime": time_ini}
        if time_end:
            body["end"] = {"dateTime": time_end}
        # Obtener el servicio de Google Calendar
        service = self.get_calendar_service()
        # Actualizar el evento de forma parcial
        event = service.events().patch(calendarId="primary", eventId=event_id, body=body).execute()
        # Estructurar la información a un JSON
        return {
            "event_id": event.get("id"),
            "html_link": event.get("htmlLink"),
            "summary": event.get("summary"),
            "time_ini": event["start"].get("dateTime", event["start"].get("date")),
            "time_end": event["end"].get("dateTime", event["end"].get("date"))
        }

    def delete_event(self, event_id):
        print(f'Llamando a la función delete_event({event_id})')
        # Obtener el servicio de Google Calendar
        service = self.get_calendar_service()
        # Eliminar el evento
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        # Estructurar la información a un JSON
        return {
            "event_id": event_id,
            "deleted": True
        }

    def list_events(self, time_ini=None, time_end=None, max_results=10):
        print(f'Llamando a la función list_events({time_ini} - {time_end}, max_results={max_results})')
        # Si no se especifica un inicio, se listan los eventos a partir de ahora
        if not time_ini:
            time_ini = datetime.datetime.now(datetime.timezone.utc).isoformat()
        # Armar los parámetros de la consulta a Google Calendar
        params = {
            "calendarId": "primary",
            "timeMin": time_ini,
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime"
        }
        if time_end:
            params["timeMax"] = time_end
        # Obtener el servicio de Google Calendar
        service = self.get_calendar_service()
        # Realizar la consulta a Google Calendar
        result = service.events().list(**params).execute()
        events = result.get("items", [])
        # Estructurar la información a una lista de JSON
        return [
            {
                "id": event.get("id"),
                "summary": event.get("summary", "(Sin título)"),
                "inicio": event["start"].get("dateTime", event["start"].get("date")),
                "fin": event["end"].get("dateTime", event["end"].get("date")),
                "es_dia_completo": "date" in event["start"],
                "ubicacion": event.get("location"),
                "descripcion": event.get("description"),
                "estado": event.get("status"),
                "html_link": event.get("htmlLink")
            }
            for event in events
        ]

if __name__ == "__main__":
    tools = Tools()
    result = tools.list_events()
    print(f'{result}')