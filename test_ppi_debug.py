"""
Script de debug para diagnosticar el error de autenticación con PPI.
Prueba distintas combinaciones de headers directamente con requests,
sin usar la librería ppi-client.

Uso:
    $env:PPI_API_PUBLICA="..."
    $env:PPI_AUTHORIZED_CLIENT="..."
    $env:PPI_CLIENT_KEY="..."
    python test_ppi_debug.py
"""

import os
import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL_PROD    = "https://clientapi.portfoliopersonal.com/api/1/Account/LoginApi"
URL_SANDBOX = "https://clientapi_sandbox.portfoliopersonal.com/api/1/Account/LoginApi"
URL = URL_PROD  # cambiá a URL_SANDBOX para probar sandbox

api_publica       = os.environ.get("PPI_API_PUBLICA", "")
authorized_client = os.environ.get("PPI_AUTHORIZED_CLIENT", "")
client_key        = os.environ.get("PPI_CLIENT_KEY", "")
api_secret        = os.environ.get("PPI_API_SECRET", "")

# Valores hardcodeados del SDK de PPI para Python
SDK_AUTHORIZED_CLIENT = "API_CLI_PYTHON"
SDK_CLIENT_KEY        = "pp19PythonApp12"

combinaciones = [
    {
        "descripcion": "Combinación correcta: credenciales propias + ApiKey + ApiSecret",
        "headers": {
            "AuthorizedClient": authorized_client,
            "ClientKey":        client_key,
            "ApiKey":           api_publica,
            "ApiSecret":        api_secret,
        },
    },
    {
        "descripcion": "SDK hardcodeado + ApiKey=api_publica + ApiSecret=client_key",
        "headers": {
            "AuthorizedClient": SDK_AUTHORIZED_CLIENT,
            "ClientKey":        SDK_CLIENT_KEY,
            "ApiKey":           api_publica,
            "ApiSecret":        client_key,
        },
    },
    {
        "descripcion": "SDK hardcodeado + ApiKey=api_publica + ApiSecret=authorized_client",
        "headers": {
            "AuthorizedClient": SDK_AUTHORIZED_CLIENT,
            "ClientKey":        SDK_CLIENT_KEY,
            "ApiKey":           api_publica,
            "ApiSecret":        authorized_client,
        },
    },
    {
        "descripcion": "Credenciales propias + ApiKey=api_publica (sin ApiSecret)",
        "headers": {
            "AuthorizedClient": authorized_client,
            "ClientKey":        client_key,
            "ApiKey":           api_publica,
        },
    },
    {
        "descripcion": "Solo ApiKey=api_publica + ApiSecret=client_key (sin AuthorizedClient/ClientKey)",
        "headers": {
            "ApiKey":    api_publica,
            "ApiSecret": client_key,
        },
    },
]

for i, combo in enumerate(combinaciones, 1):
    print(f"\n{'='*60}")
    print(f"Combinación {i}: {combo['descripcion']}")
    print(f"Headers: {json.dumps(combo['headers'], indent=2)}")
    try:
        r = requests.post(URL, headers=combo["headers"], verify=False, timeout=10)
        print(f"Status: {r.status_code}")
        print(f"Respuesta: {r.text[:300]}")
        if r.status_code == 200:
            print(">>> ÉXITO <<<")
            break
    except Exception as e:
        print(f"Excepción: {e}")
