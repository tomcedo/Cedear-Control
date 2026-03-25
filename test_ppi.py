"""
Script de prueba para la API de Portfolio Personal Inversiones (PPI).
Usa la librería oficial ppi-client para autenticarse y obtener
el precio actual de GGAL.

Credenciales requeridas como variables de entorno:
    PPI_KEY_PUBLICA — API key pública
    PPI_KEY_PRIVADA — API key privada
"""

import os
import json
from ppi_client.ppi import PPI

if __name__ == "__main__":
    if not os.environ.get("PPI_KEY_PUBLICA") or not os.environ.get("PPI_KEY_PRIVADA"):
        print("[ERROR] Definí las variables de entorno PPI_KEY_PUBLICA y PPI_KEY_PRIVADA")
        raise SystemExit(1)

    # Autenticación
    ppi = PPI(sandbox=False)
    ppi.account.login_api(os.environ['PPI_KEY_PUBLICA'], os.environ['PPI_KEY_PRIVADA'])
    print("[OK] Autenticación exitosa")

    # Cotización actual de GGAL (acción argentina, liquidación A-48HS)
    ticker = "GGAL"
    print(f"\nConsultando cotización de {ticker}...")
    cotizacion = ppi.marketdata.current(ticker, "Acciones", "A-48HS")

    # Resultado
    print(f"\n{'='*40}")
    print(f"  Símbolo  : {ticker}")
    print(f"  Último   : ${cotizacion.get('price',        'N/D'):,.2f} ARS")
    print(f"  Apertura : ${cotizacion.get('openingPrice', 'N/D'):,.2f} ARS")
    print(f"  Máximo   : ${cotizacion.get('max',          'N/D'):,.2f} ARS")
    print(f"  Mínimo   : ${cotizacion.get('min',          'N/D'):,.2f} ARS")
    print(f"  Volumen  : {cotizacion.get('volume',        'N/D')}")
    print(f"{'='*40}")
    print("\nRespuesta completa:")
    print(json.dumps(cotizacion, indent=2, ensure_ascii=False))
