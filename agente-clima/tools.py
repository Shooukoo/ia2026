import requests


class Tools():
    def __init__(self):
        pass

    def get_lat_long(self, ciudad:str):
        if not ciudad:
            return {
                "succes": False,
                "message": "Error, se debe proporcionar una ciudad"
            }

        url = f"https://geocoding-api.open-meteo.com/v1/search?name={ciudad}&count=1&language=es&format=json"

        response = requests.get(url)
        data = response.json()

        resultados = data.get("results")
        if not resultados:
            return {
                "succes": False,
                "message": f"No se encontraron resultados para la ciudad: {ciudad}"
            }

        primer_resultado = resultados[0]
        return {
            "succes": True,
            "latitude": primer_resultado["latitude"],
            "longitude": primer_resultado["longitude"],
            "name": primer_resultado["name"],
            "country": primer_resultado["country"]
        }
    
    def get_weather(self, lat:str, long:str):
        if not lat or not long:
            return {
                "succes": False,
                "message": "Error, se debe proporcionar latitud y longitud"
            }
        
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current_weather=true"

        response = requests.get(url)
        data = response.json()

        clima_actual = data.get("current_weather")
        if not clima_actual:
            return {
                "succes": False,
                "message": "No se encontró información del clima para esa ubicación"
            }

        return {
            "succes": True,
            "temperature": clima_actual["temperature"],
            "windspeed": clima_actual["windspeed"],
            "winddirection": clima_actual["winddirection"],
            "weathercode": clima_actual["weathercode"],
            "time": clima_actual["time"]
        }

if __name__ == "__main__":
    tools = Tools()
    result = tools.get_lat_long("Puebla")
    print(f'{result}')