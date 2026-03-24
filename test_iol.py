"""
Script de prueba para la API de InvertirOnLine (IOL).
Autentica con OAuth y obtiene el precio actual de GGAL como prueba.

Credenciales requeridas como variables de entorno:
    IOL_USUARIO   — usuario de la cuenta IOL
    IOL_PASSWORD  — contraseña de la cuenta IOL
"""

import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://api.invertironline.com"


def obtener_token(usuario: str, password: str) -> str:
    """Autentica con OAuth y retorna el access token."""
    respuesta = requests.post(
        f"{BASE_URL}/token",
        data={
            "grant_type": "password",
            "username":   usuario,
            "password":   password,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        verify=False,
        timeout=10,
    )
    respuesta.raise_for_status()
    datos = respuesta.json()
    print(f"[OK] Token obtenido — expira en {datos.get('expires_in', '?')} segundos")
    return datos["access_token"]


def obtener_cotizacion(token: str, mercado: str, simbolo: str) -> dict:
    """Obtiene la cotización actual de un título."""
    respuesta = requests.get(
        f"{BASE_URL}/api/v2/{mercado}/Titulos/{simbolo}/Cotizacion",
        headers={"Authorization": f"Bearer {token}"},
        verify=False,
        timeout=10,
    )
    respuesta.raise_for_status()
    return respuesta.json()


if __name__ == "__main__":
    usuario  = os.environ.get("IOL_USUARIO")
    password = os.environ.get("IOL_PASSWORD")

    if not usuario or not password:
        print("[ERROR] Definí las variables de entorno IOL_USUARIO e IOL_PASSWORD")
        raise SystemExit(1)

    # Autenticación
    token = obtener_token(usuario, password)

    # Cotización de GGAL en BCBA como prueba
    simbolo = "GGAL"
    mercado = "bCBA"
    print(f"\nConsultando cotización de {simbolo} en {mercado}...")
    cotizacion = obtener_cotizacion(token, mercado, simbolo)

    # Resultado
    print(f"\n{'='*40}")
    print(f"  Símbolo : {simbolo}")
    print(f"  Último  : ${cotizacion.get('ultimoPrecio', 'N/D'):,.2f} ARS")
    print(f"  Apertura: ${cotizacion.get('apertura', 'N/D'):,.2f} ARS")
    print(f"  Máximo  : ${cotizacion.get('maximo', 'N/D'):,.2f} ARS")
    print(f"  Mínimo  : ${cotizacion.get('minimo', 'N/D'):,.2f} ARS")
    print(f"  Variación: {cotizacion.get('variacion', 'N/D')}%")
    print(f"{'='*40}")
    print("\nRespuesta completa:")
    import json
    print(json.dumps(cotizacion, indent=2, ensure_ascii=False))
