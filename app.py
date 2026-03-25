import json
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import urllib3
from datetime import datetime
from pathlib import Path
from ppi_data import obtener_datos_ppi, obtener_variaciones_yahoo

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Portfolio Dashboard", page_icon="📈", layout="wide")

# ---------------------------------------------------------------------------
# Sectores y colores
# ---------------------------------------------------------------------------
SECTORES = {
    "AMZN":  ("Tech",        "#4C9BE8"),
    "GOOGL": ("Tech",        "#4C9BE8"),
    "MSFT":  ("Tech",        "#4C9BE8"),
    "NVDA":  ("Tech",        "#4C9BE8"),
    "XOM":   ("Energía",     "#E8834C"),
    "PBR":   ("Energía",     "#E8834C"),
    "BBD":   ("Financiero",  "#4CAF7D"),
    "NU":    ("Financiero",  "#4CAF7D"),
    "VALE":  ("Materiales",  "#9B59B6"),
}

COLOR_SECTOR = {
    "Tech":       "#4C9BE8",
    "Energía":    "#E8834C",
    "Financiero": "#4CAF7D",
    "Materiales": "#9B59B6",
    "Otro":       "#888888",
}

ICONO_SECTOR = {
    "Tech":       "💻",
    "Energía":    "⚡",
    "Financiero": "🏦",
    "Materiales": "⛏️",
    "Otro":       "📊",
}

# ---------------------------------------------------------------------------
# Carga de portfolio: Streamlit Cloud (st.secrets) o local (portfolio.json)
# ---------------------------------------------------------------------------
try:
    # Streamlit Cloud: el portfolio viene como JSON string en secrets.toml
    _datos = json.loads(st.secrets["portfolio"]["data"])
except Exception:
    # Local: leer desde portfolio.json
    _ruta_portfolio = Path(__file__).parent / "portfolio.json"
    if not _ruta_portfolio.exists():
        st.error(
            "No se encontró `portfolio.json`. "
            "Copiá `portfolio.example.json` como `portfolio.json` y completá con tus datos."
        )
        st.stop()
    with open(_ruta_portfolio, encoding="utf-8") as _f:
        _datos = json.load(_f)

precios_ars_fallback = _datos["precios_ars"]
portfolio_principal  = _datos["portfolio_principal"]
portfolio_secundario = _datos["portfolio_secundario"]

# ---------------------------------------------------------------------------
# Precios en tiempo real desde PPI (con fallback a portfolio.json)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)  # refresca cada 5 minutos
def obtener_precios(tickers: tuple) -> tuple[dict, str, dict]:
    """Devuelve (precios, fuente, variaciones). Fuente: 'PPI' o 'portfolio.json'."""
    if os.environ.get("PPI_KEY_PUBLICA") and os.environ.get("PPI_KEY_PRIVADA"):
        try:
            precios, variaciones = obtener_datos_ppi(list(tickers))
            if precios:
                return precios, "PPI", variaciones
        except Exception as e:
            print(f"[PPI] Falló la obtención de precios: {e}")
    # Fallback: precios del JSON + variaciones desde Yahoo
    variaciones = {}
    try:
        variaciones = obtener_variaciones_yahoo(list(tickers))
    except Exception as e:
        print(f"[Yahoo] Falló la obtención de variaciones: {e}")
    return precios_ars_fallback, "portfolio.json", variaciones


_todos_los_tickers = tuple(set(portfolio_principal) | set(portfolio_secundario))
precios_ars, fuente_precios, variaciones_diarias = obtener_precios(_todos_los_tickers)

# ---------------------------------------------------------------------------
# API dólar MEP
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300)  # refresca cada 5 minutos
def obtener_dolar_mep():
    """
    Obtiene el valor del dólar MEP intentando dos fuentes en orden:
    1. DolarAPI  2. Bluelytics
    Retorna (valor, hora, fuente) o (None, None, None) si ambas fallan.
    """
    fuentes = [
        {
            "url":    "https://dolarapi.com/v1/dolares/bolsa",
            "nombre": "DolarAPI",
            "parsear": lambda d: (
                d["venta"],
                datetime.fromisoformat(d["fechaActualizacion"]).strftime("%d/%m/%Y %H:%M"),
            ),
        },
        {
            "url":    "https://api.bluelytics.com.ar/v2/latest",
            "nombre": "Bluelytics (blue)",
            "parsear": lambda d: (
                d["blue"]["value_sell"],
                datetime.fromisoformat(d["last_update"]).strftime("%d/%m/%Y %H:%M"),
            ),
        },
    ]

    headers = {"User-Agent": "Mozilla/5.0"}

    for fuente in fuentes:
        try:
            respuesta = requests.get(fuente["url"], timeout=5, verify=False, headers=headers)
            respuesta.raise_for_status()
            valor, hora = fuente["parsear"](respuesta.json())
            return valor, hora, fuente["nombre"]
        except Exception as e:
            print(f"[DEBUG] Falló {fuente['nombre']}: {type(e).__name__}: {e}")
            continue

    return None, None, None


# ---------------------------------------------------------------------------
# Funciones
# ---------------------------------------------------------------------------
def semaforo(peso: float) -> str:
    """Devuelve un emoji semáforo según el peso porcentual del ticker."""
    if peso > 35:
        return "🔴"
    if peso > 20:
        return "🟡"
    if peso >= 5:
        return "🟢"
    return "⚪"  # posición marginal (<5%)


def calcular_portfolio(posiciones: dict, dolar_mep: float, precios: dict, variaciones: dict) -> pd.DataFrame:
    """Convierte las posiciones a un DataFrame con valor en USD, sector, peso % y semáforo."""
    filas = []
    for ticker, cantidad in posiciones.items():
        precio = precios.get(ticker, precios_ars_fallback.get(ticker, 0))
        valor_ars = precio * cantidad
        valor_usd = valor_ars / dolar_mep
        sector, _ = SECTORES.get(ticker, ("Otro", "#888888"))
        filas.append({
            "Ticker":      ticker,
            "Sector":      sector,
            "Cantidad":    cantidad,
            "Precio ARS":  precio,
            "Valor ARS":   valor_ars,
            "Valor USD":   valor_usd,
            "Var. diaria": variaciones.get(ticker),
        })
    df = pd.DataFrame(filas)
    df["Peso %"] = df["Valor USD"] / df["Valor USD"].sum() * 100
    df["Estado"] = df["Peso %"].map(semaforo)
    return df


def _fmt_variacion(v) -> str:
    """Formatea la variación diaria como '↑ 1.23%', '↓ 0.45%' o '-'."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "-"
    if v > 0:
        return f"↑ {v:.2f}%"
    if v < 0:
        return f"↓ {abs(v):.2f}%"
    return "0.00%"


def renderizar_tabla(df: pd.DataFrame) -> None:
    """
    Muestra el DataFrame con column_config de Streamlit:
    sector con icono, barra de progreso para Peso %, formato de moneda,
    y variación diaria coloreada (↑ verde / ↓ rojo).
    """
    df_display = df.copy()
    df_display["Sector"] = df_display["Sector"].map(
        lambda s: f"{ICONO_SECTOR.get(s, '')} {s}"
    )
    df_display["Var. diaria"] = df_display["Var. diaria"].map(_fmt_variacion)

    def _color_var(val):
        if isinstance(val, str) and val.startswith("↑"):
            return "color: #2ecc71"
        if isinstance(val, str) and val.startswith("↓"):
            return "color: #e74c3c"
        return ""

    styled = df_display.style.map(_color_var, subset=["Var. diaria"])

    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
        column_order=["Estado", "Ticker", "Sector", "Cantidad", "Precio ARS", "Valor ARS", "Valor USD", "Var. diaria", "Peso %"],
        column_config={
            "Estado":      st.column_config.TextColumn("",             width="small"),
            "Ticker":      st.column_config.TextColumn("Ticker",       width="small"),
            "Sector":      st.column_config.TextColumn("Sector",       width="medium"),
            "Cantidad":    st.column_config.NumberColumn("Cantidad",   format="%d"),
            "Precio ARS":  st.column_config.NumberColumn("Precio ARS", format="$%,.0f"),
            "Valor ARS":   st.column_config.NumberColumn("Valor ARS",  format="$%,.0f"),
            "Valor USD":   st.column_config.NumberColumn("Valor USD",  format="$%,.2f"),
            "Var. diaria": st.column_config.TextColumn("Var. diaria",  width="small"),
            "Peso %":      st.column_config.ProgressColumn(
                "Peso %",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
        },
    )


def resumen_concentracion(df: pd.DataFrame, nombre: str) -> None:
    """Analiza el portfolio y muestra alertas de concentración por ticker y por sector."""
    rojos    = df[df["Peso %"] > 35]["Ticker"].tolist()
    amarillos = df[(df["Peso %"] > 20) & (df["Peso %"] <= 35)]["Ticker"].tolist()

    por_sector = df.groupby("Sector")["Peso %"].sum()
    sectores_criticos  = por_sector[por_sector > 60].index.tolist()
    sectores_altos     = por_sector[(por_sector > 40) & (por_sector <= 60)].index.tolist()

    sin_problemas = not rojos and not amarillos and not sectores_criticos and not sectores_altos

    st.markdown(f"**{nombre}**")

    if sin_problemas:
        st.success("🟢 Bien diversificado. Ningún ticker supera el 20% ni ningún sector el 40%.")
        return

    for ticker in rojos:
        peso = df.loc[df["Ticker"] == ticker, "Peso %"].iloc[0]
        st.error(f"🔴 **{ticker}** representa el {peso:.1f}% — concentración crítica (>35%).")

    for ticker in amarillos:
        peso = df.loc[df["Ticker"] == ticker, "Peso %"].iloc[0]
        st.warning(f"🟡 **{ticker}** representa el {peso:.1f}% — concentración moderada (20–35%).")

    for sector in sectores_criticos:
        st.error(f"🔴 Sector **{sector}**: {por_sector[sector]:.1f}% del portfolio — exposición sectorial crítica (>60%).")

    for sector in sectores_altos:
        st.warning(f"🟡 Sector **{sector}**: {por_sector[sector]:.1f}% del portfolio — exposición sectorial alta (40–60%).")


def grafico_torta(df: pd.DataFrame) -> None:
    """Torta por ticker, color distinto por cada acción."""
    fig = px.pie(
        df,
        names="Ticker",
        values="Valor USD",
        color_discrete_sequence=px.colors.qualitative.Plotly,
        hole=0.3,
    )
    fig.update_traces(
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{percent}<br>$%{value:,.0f} USD<extra></extra>",
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Obtención del dólar MEP + variación por sesión
# ---------------------------------------------------------------------------
mep_api, mep_hora, mep_fuente = obtener_dolar_mep()

mep_delta = None
if mep_api:
    if "mep_previo" not in st.session_state:
        st.session_state.mep_previo = mep_api
    else:
        delta = mep_api - st.session_state.mep_previo
        mep_delta = f"{delta:+.2f}" if delta != 0 else None
        st.session_state.mep_previo = mep_api
    dolar_mep = mep_api
else:
    st.warning("No se pudo obtener el dólar MEP desde ninguna fuente. Ingresalo manualmente.")
    dolar_mep = st.number_input(
        "Dólar MEP (ARS)",
        min_value=1.0,
        value=1_400.0,
        step=10.0,
        format="%.2f",
    )

if dolar_mep <= 0:
    st.error("Ingresá un valor válido para el dólar MEP.")
    st.stop()

# ---------------------------------------------------------------------------
# Cálculo de portfolios
# ---------------------------------------------------------------------------
df_principal  = calcular_portfolio(portfolio_principal,  dolar_mep, precios_ars, variaciones_diarias)
df_secundario = calcular_portfolio(portfolio_secundario, dolar_mep, precios_ars, variaciones_diarias)

total_principal  = df_principal["Valor USD"].sum()
total_secundario = df_secundario["Valor USD"].sum()
total_combinado  = total_principal + total_secundario

# ---------------------------------------------------------------------------
# Header: título + 4 métricas destacadas
# ---------------------------------------------------------------------------
st.title("📈 Portfolio Dashboard")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.metric("💼 Total Combinado", f"${total_combinado:,.0f} USD")
with col_m2:
    pct_principal = total_principal / total_combinado * 100
    st.metric("Portfolio Principal", f"${total_principal:,.0f} USD", f"{pct_principal:.1f}% del total")
with col_m3:
    pct_secundario = total_secundario / total_combinado * 100
    st.metric("Portfolio Secundario", f"${total_secundario:,.0f} USD", f"{pct_secundario:.1f}% del total")
with col_m4:
    if mep_api:
        st.metric(
            f"USD MEP · {mep_fuente}",
            f"${mep_api:,.2f}",
            delta=mep_delta,
            help=f"Actualizado: {mep_hora} · caché 5 min",
        )
    else:
        st.metric("USD MEP (manual)", f"${dolar_mep:,.2f}")

st.divider()

# ---------------------------------------------------------------------------
# Portfolio Principal — fila completa
# ---------------------------------------------------------------------------
st.subheader("Portfolio Principal")
col_t1, col_g1 = st.columns([7, 3])
with col_t1:
    renderizar_tabla(df_principal)
with col_g1:
    grafico_torta(df_principal)

st.divider()

# ---------------------------------------------------------------------------
# Portfolio Secundario — fila completa
# ---------------------------------------------------------------------------
st.subheader("Portfolio Secundario")
col_t2, col_g2 = st.columns([7, 3])
with col_t2:
    renderizar_tabla(df_secundario)
with col_g2:
    grafico_torta(df_secundario)

st.divider()

# ---------------------------------------------------------------------------
# Resumen de concentración
# ---------------------------------------------------------------------------
st.subheader("Resumen de concentración")
st.caption("🟢 Saludable (5–20%) · 🟡 Moderado (20–35%) · 🔴 Crítico (+35%) · ⚪ Marginal (<5%)")

col_r1, col_r2 = st.columns(2)
with col_r1:
    resumen_concentracion(df_principal, "Portfolio Principal")
with col_r2:
    resumen_concentracion(df_secundario, "Portfolio Secundario")

st.divider()
if fuente_precios == "PPI":
    st.caption("Precios ARS obtenidos en tiempo real desde **PPI** · caché 5 min")
else:
    st.caption("⚠️ Precios de demostración · Conectá tus credenciales PPI para precios en tiempo real")
