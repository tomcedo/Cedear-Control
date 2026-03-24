# CEDEAR Control

Dashboard interactivo para el seguimiento de portfolios de inversión en CEDEARs, con valuación en dólares MEP en tiempo real.

![Screenshot](screenshot.png)
> *Captura de pantalla próximamente*

---

## Características

- Valuación de posiciones en USD MEP: `(precio ARS × cantidad) / dólar MEP`
- Dólar MEP obtenido automáticamente desde APIs públicas, con fallback a ingreso manual
- Comparación lado a lado de dos portfolios
- Gráficos de distribución por ticker (torta) y peso porcentual (barras)
- Resaltado de posiciones con valor menor a USD 500

## Tecnologías

| | |
|---|---|
| [Python 3](https://www.python.org/) | Lenguaje principal |
| [Streamlit](https://streamlit.io/) | Framework del dashboard |
| [Plotly Express](https://plotly.com/python/plotly-express/) | Gráficos interactivos |
| [Requests](https://requests.readthedocs.io/) | Consumo de APIs |
| [DolarAPI](https://dolarapi.com/) / [Bluelytics](https://bluelytics.com.ar/) | Fuentes del tipo de cambio MEP |

## Instalación

**Requisitos:** Python 3.8+

```bash
# Clonar el repositorio
git clone https://github.com/tomcedo/Cedear-Control.git
cd Cedear-Control

# Instalar dependencias
pip install streamlit plotly requests

# Correr el dashboard
streamlit run app.py
```

El dashboard queda disponible en `http://localhost:8501`.

## Estructura

```
cedear-control/
├── app.py        # Aplicación principal
└── CLAUDE.md     # Guía para Claude Code
```

---

## Construido con Claude Code

Este proyecto fue desarrollado de forma asistida usando [Claude Code](https://claude.ai/code), el agente de programación de Anthropic que opera directamente en la terminal.

Claude Code fue usado para generar la estructura inicial del dashboard, integrar las APIs de tipo de cambio, diseñar los gráficos, resolver problemas de conectividad SSL en Windows, y mantener el historial de commits a lo largo del desarrollo.
