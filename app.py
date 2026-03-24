import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------
st.set_page_config(page_title="CEDEAR Control", layout="wide")

# ---------------------------------------------------------------------------
# Datos hardcodeados — precios en ARS (se reemplazarán por API)
# ---------------------------------------------------------------------------
precios_ars = {
    "AMZN":  22_500,
    "BBD":     310,
    "GOOGL": 20_800,
    "MSFT":  17_200,
    "NU":     2_450,
    "NVDA":  46_000,
    "PBR":    1_850,
    "VALE":   1_620,
    "XOM":   11_400,
}

portfolio_principal = {
    "AMZN":  1249,
    "BBD":    633,
    "GOOGL":  619,
    "MSFT":   126,
    "NU":     506,
    "NVDA":   624,
    "PBR":    110,
    "XOM":     66,
}

portfolio_secundario = {
    "NU":     402,
    "NVDA":   139,
    "PBR":     50,
    "VALE":   263,
}

# ---------------------------------------------------------------------------
# Funciones
# ---------------------------------------------------------------------------
def calcular_portfolio(posiciones: dict, dolar_mep: float) -> pd.DataFrame:
    """Convierte las posiciones a un DataFrame con el valor en USD de cada una."""
    filas = []
    for ticker, cantidad in posiciones.items():
        precio = precios_ars[ticker]
        valor_ars = precio * cantidad
        valor_usd = valor_ars / dolar_mep
        filas.append({
            "Ticker":      ticker,
            "Cantidad":    cantidad,
            "Precio ARS":  precio,
            "Valor ARS":   valor_ars,
            "Valor USD":   valor_usd,
        })
    return pd.DataFrame(filas)


def formatear_tabla(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica formato legible a las columnas numéricas."""
    df = df.copy()
    df["Cantidad"]   = df["Cantidad"].apply(lambda x: f"{x:,}")
    df["Precio ARS"] = df["Precio ARS"].apply(lambda x: f"${x:,.0f}")
    df["Valor ARS"]  = df["Valor ARS"].apply(lambda x: f"${x:,.0f}")
    df["Valor USD"]  = df["Valor USD"].apply(lambda x: f"${x:,.2f}")
    return df


def colorear_bajo_valor(df: pd.DataFrame) -> pd.DataFrame:
    """Resalta en rojo las filas cuyo Valor USD es menor a $500."""
    def estilo_fila(fila):
        # Convertir string formateado a float para comparar
        valor = float(fila["Valor USD"].replace("$", "").replace(",", ""))
        color = "color: #e05c5c" if valor < 500 else ""
        return [color] * len(fila)

    return df.style.apply(estilo_fila, axis=1)


# ---------------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------------
st.title("CEDEAR Control")
st.caption("Seguimiento de portfolios · valores en USD MEP")

# Ingreso del dólar MEP
col_mep, _ = st.columns([1, 3])
with col_mep:
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

st.divider()

# Cálculo de ambos portfolios
df_principal   = calcular_portfolio(portfolio_principal,   dolar_mep)
df_secundario  = calcular_portfolio(portfolio_secundario,  dolar_mep)

total_principal  = df_principal["Valor USD"].sum()
total_secundario = df_secundario["Valor USD"].sum()
total_combinado  = total_principal + total_secundario

# Métrica principal destacada
st.metric("💼 Total combinado USD", f"${total_combinado:,.2f}")

st.divider()

# ---------------------------------------------------------------------------
# Visualización en dos columnas
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Portfolio Principal")
    st.dataframe(
        colorear_bajo_valor(formatear_tabla(df_principal)),
        use_container_width=True,
        hide_index=True,
    )
    st.metric("Total USD", f"${total_principal:,.2f}")

    # Gráfico de distribución por ticker
    fig_torta = px.pie(
        df_principal,
        names="Ticker",
        values="Valor USD",
        title="Distribución por ticker (USD)",
        hole=0.3,
    )
    fig_torta.update_traces(textinfo="percent+label")
    fig_torta.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
    st.plotly_chart(fig_torta, use_container_width=True)

with col2:
    st.subheader("Portfolio Secundario")
    st.dataframe(
        colorear_bajo_valor(formatear_tabla(df_secundario)),
        use_container_width=True,
        hide_index=True,
    )
    st.metric("Total USD", f"${total_secundario:,.2f}")

st.caption("⚠️ Precios ARS hardcodeados · pendiente conexión a API de mercado")
