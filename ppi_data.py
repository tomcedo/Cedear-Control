"""
Módulo para obtener precios y variaciones de CEDEARs.
Fuente primaria: API de PPI (requiere PPI_KEY_PUBLICA y PPI_KEY_PRIVADA).
Fuente secundaria: Yahoo Finance (sin credenciales).
"""

import os
import yfinance as yf
from ppi_client.ppi import PPI

# Tickers que en Yahoo Finance usan un símbolo distinto al del portfolio
TICKER_YAHOO = {
    "VALE": "VALE3.SA",
}


def obtener_datos_ppi(tickers: list[str]) -> tuple[dict, dict]:
    """
    Obtiene precio y variación diaria de una lista de tickers desde PPI.

    :returns: (precios, variaciones) — dicts {ticker: valor}.
              Tickers con error se omiten de ambos resultados.
    :raises ValueError: si faltan las variables de entorno de credenciales.
    """
    if not os.environ.get("PPI_KEY_PUBLICA") or not os.environ.get("PPI_KEY_PRIVADA"):
        raise ValueError("Faltan las variables de entorno PPI_KEY_PUBLICA y/o PPI_KEY_PRIVADA")

    ppi = PPI(sandbox=False)
    ppi.account.login_api(os.environ['PPI_KEY_PUBLICA'], os.environ['PPI_KEY_PRIVADA'])

    precios    = {}
    variaciones = {}
    for ticker in tickers:
        try:
            datos = ppi.marketdata.current(ticker, "CEDEARS", "A-48HS")
            if datos.get("price") is not None:
                precios[ticker] = float(datos["price"])
            if datos.get("marketChangePercent") is not None:
                variaciones[ticker] = float(datos["marketChangePercent"])
        except Exception as e:
            print(f"[PPI] Error al obtener {ticker}: {e}")

    return precios, variaciones


def obtener_precios_ppi(tickers: list[str]) -> dict[str, float]:
    """Wrapper de obtener_datos_ppi que devuelve solo los precios."""
    precios, _ = obtener_datos_ppi(tickers)
    return precios


def obtener_variaciones_yahoo(tickers: list[str]) -> dict[str, float]:
    """
    Obtiene la variación porcentual diaria de una lista de tickers desde Yahoo Finance.
    Usa TICKER_YAHOO para traducir símbolos que difieren (ej. VALE → VALE3.SA).

    :returns: dict {ticker: variacion_pct}. Tickers con error se omiten.
    """
    variaciones = {}
    for ticker in tickers:
        simbolo = TICKER_YAHOO.get(ticker, ticker)
        try:
            hist = yf.download(simbolo, period="2d", progress=False, auto_adjust=True)
            if len(hist) >= 2:
                cierre_hoy      = float(hist["Close"].iloc[-1])
                cierre_anterior = float(hist["Close"].iloc[-2])
                variaciones[ticker] = (cierre_hoy / cierre_anterior - 1) * 100
        except Exception as e:
            print(f"[Yahoo] Error al obtener {ticker} ({simbolo}): {e}")

    return variaciones
