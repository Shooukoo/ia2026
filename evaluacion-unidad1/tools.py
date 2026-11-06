import os.path
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def _dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def fmt_hora(ini, fin):
    """Solo hora si el rango cabe en un día; con fecha si abarca varios."""
    return "%H:%M" if ini.date() == (fin - timedelta(seconds=1)).date() else "%d/%m %H:%M"


def calcular_ocupacion(busy, time_ini, time_end):
    """Fusiona intervalos busy, suma horas ocupadas y encuentra huecos libres."""
    ini, fin = _dt(time_ini), _dt(time_end)
    tz = ini.tzinfo
    # recortar al rango y ordenar
    ivs = sorted(
        (max(_dt(b["start"]).astimezone(tz), ini), min(_dt(b["end"]).astimezone(tz), fin))
        for b in busy
    )
    merged = []
    for s, e in ivs:
        if e <= s:
            continue
        if merged and s <= merged[-1][1]:  # traslape se extiende el último
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    horas = sum((e - s).total_seconds() for s, e in merged) / 3600
    # huecos = espacios entre los intervalos ocupados dentro del rango
    fmt = fmt_hora(ini, fin)
    huecos, cursor = [], ini
    for s, e in merged + [[fin, fin]]:
        if s > cursor:
            huecos.append(f"{cursor:{fmt}} - {s:{fmt}}")
        cursor = max(cursor, e)
    return round(horas, 2), huecos


class Tools():
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.CREDENTIALS_FILE = "credentials.json"
        self.TOKEN_FILE = "token.json"

    def get_calendar_service(self):
        creds = None
        if os.path.exists(self.TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.CREDENTIALS_FILE):
                    raise FileNotFoundError("No se encontró el archivo de credenciales!")
                flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        return build("calendar", "v3", credentials=creds)

    def _eventos(self, service, time_ini, time_end, q=None):
        params = dict(calendarId="primary", timeMin=time_ini, timeMax=time_end,
                      singleEvents=True, orderBy="startTime", maxResults=250)
        if q:
            params["q"] = q  # búsqueda de texto libre
        items = []
        while True:  # paginar: la API devuelve máx. 250 por página
            page = service.events().list(**params).execute()
            items += page.get("items", [])
            if not page.get("nextPageToken"):
                break
            params["pageToken"] = page["nextPageToken"]
        # sin cancelados, de día completo ni marcados como "libre"
        return [e for e in items if e.get("status") != "cancelled" and "dateTime" in e["start"]
                and e.get("transparency") != "transparent"]

    def analizar_dia(self, time_ini, time_end):
        print(f'Llamando a la función analizar_dia({time_ini} - {time_end})')
        try:
            service = self.get_calendar_service()
            tz = _dt(time_ini).tzinfo
            # info del calendario principal 
            cal = service.calendars().get(calendarId="primary").execute()
            eventos = self._eventos(service, time_ini, time_end)
            if not eventos:
                return {"success": True, "total_reuniones": 0, "mensaje": "No se encontraron eventos"}
            # ocupación desde los mismos eventos listados 
            busy = [{"start": e["start"]["dateTime"], "end": e["end"]["dateTime"]} for e in eventos]
            horas, huecos = calcular_ocupacion(busy, time_ini, time_end)
            fmt = fmt_hora(_dt(time_ini), _dt(time_end))
            hora = lambda e: f'{_dt(e["start"]["dateTime"]).astimezone(tz):{fmt}} - {e.get("summary", "(Sin título)")}'
            return {
                "success": True,
                "calendario": cal.get("summary"),
                "total_reuniones": len(eventos),
                "horas_ocupadas": horas,
                "primera_reunion": hora(eventos[0]),
                "ultima_reunion": hora(eventos[-1]),
                "huecos_libres": huecos,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def buscar_por_tema(self, time_ini, time_end, tema):
        print(f'Llamando a la función buscar_por_tema({time_ini} - {time_end}, tema={tema})')
        try:
            eventos = self._eventos(self.get_calendar_service(), time_ini, time_end, q=tema)
            if not eventos:
                return {"success": True, "tema": tema, "total": 0, "mensaje": "No se encontraron eventos"}
            return {
                "success": True,
                "tema": tema,
                "total": len(eventos),
                "titulos": [e.get("summary", "(Sin título)") for e in eventos],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
