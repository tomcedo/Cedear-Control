"""
Módulo para obtener precios de CEDEARs desde la API de PPI.
Requiere variables de entorno: PPI_KEY_PUBLICA y PPI_KEY_PRIVADA
"""

import os
from ppi_client.ppi import PPI


def obtener_precios_ppi(tickers: list[str]) -> dict[str, float]:
    """
    Obtiene el precio actual de una lista de tickers desde la API de PPI.

    :param tickers: lista de símbolos, e.g. ["GGAL", "AMZN", "NVDA"]
    :returns: dict {ticker: precio_ars}. Tickers con error se omiten del resultado.
    :raises Exception: si las credenciales no están definidas o el login falla.
    """
    key_publica = os.environ.get("PPI_KEY_PUBLICA")
    key_privada = os.environ.get("PPI_KEY_PRIVADA")

    if not key_publica or not key_privada:
        raise ValueError("Faltan las variables de entorno PPI_KEY_PUBLICA y/o PPI_KEY_PRIVADA")

    ppi = PPI(sandbox=False)
    ppi.account.login_api(os.environ['PPI_KEY_PUBLICA'], os.environ['PPI_KEY_PRIVADA'])

    precios = {}
    for ticker in tickers:
        try:
            datos = ppi.marketdata.current(ticker, "CEDEARS", "A-48HS")
            precio = datos.get("price")
            if precio is not None:
                precios[ticker] = float(precio)
        except Exception as e:
            print(f"[PPI] Error al obtener {ticker}: {e}")

    return precios
