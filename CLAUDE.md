# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto

Dashboard en Python + Streamlit para seguimiento de portfolios de inversión en CEDEARs. Muestra el valor en USD MEP de cada posición y permite comparar dos portfolios.

## Ejecutar

```bash
streamlit run app.py
```

## Arquitectura

Aplicación Streamlit de una sola página. La fórmula central es:

```
valor_usd = (precio_ars × cantidad) / dolar_mep
```

El dólar MEP se obtiene dinámicamente (ver scripts de referencia en `prueba-claude/calcular_mep.py`).

## Portfolios

Los datos de portfolio se leen desde portfolio.json (no incluido en el repo).
Ver portfolio.example.json para el formato esperado.

## Convenciones

- Comentarios y nombres de variables en español
- Archivos en `snake_case`
