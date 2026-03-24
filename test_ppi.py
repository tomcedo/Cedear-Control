"""
Script de prueba para la API de Portfolio Personal Inversiones (PPI).
Usa la librería oficial ppi-client para autenticarse y obtener
el precio actual de GGAL.

Credenciales requeridas como variables de entorno:
    PPI_KEY    — API Pública (public key)
    PPI_SECRET — Client Key (private key)
"""

import os
import json
from ppi_client.ppi import PPI

if __name__ == "__main__":
    ppi_key    = os.environ.get("PPI_KEY")
    ppi_secret = os.environ.get("PPI_SECRET")

    if not ppi_key or not ppi_secret:
        print("[ERROR] Definí las variables de entorno PPI_KEY y PPI_SECRET")
        raise SystemExit(1)

    # Autenticación
    ppi = PPI(sandbox=False)
    ppi.account.login_api(ppi_key, ppi_secret)
    print("[OK] Autenticación exitosa")

    # Cotización actual de GGAL
    ticker = "GGAL"
    print(f"\nConsultando cotización de {ticker}...")
    cotizacion = ppi.marketdata.current(ticker, "CEDEARS", "A-48HS")

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
