
import json
import requests

BASE_URL = "https://dev.integration.jps.go.cr"
ENDPOINT = "/api/App/nuevostiempos/last"


def obtener_ultimo_resultado():
    url = f"{BASE_URL}{ENDPOINT}"

    print("LottoLab CR - Prueba de conexion con JPS")
    print(f"Consultando: {url}\n")

    try:
        response = requests.get(
            url,
            headers={"Accept": "application/json"},
            timeout=15
        )

        print(f"Codigo HTTP: {response.status_code}")

        response.raise_for_status()

        try:
            datos = response.json()
        except ValueError:
            print("La respuesta no contiene JSON valido.")
            print(response.text[:500])
            return

        print("\nRespuesta de la API:")
        print(json.dumps(datos, indent=4, ensure_ascii=False)[:4000])

    except requests.exceptions.Timeout:
        print("Error: la solicitud supero el tiempo de espera.")

    except requests.exceptions.HTTPError as error:
        print(f"Error HTTP: {error}")
        print(f"Detalle: {response.text[:500]}")

    except requests.exceptions.RequestException as error:
        print(f"Error de conexion: {error}")


if __name__ == "__main__":
    obtener_ultimo_resultado()
