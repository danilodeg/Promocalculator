# 🎈 Blank app template

A simple Streamlit app template for you to modify!

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

### Calculadora de inflación

Actualiza un monto entre dos meses usando el IPC Nacional (nivel general) del INDEC:
`monto × índice(hasta) / índice(desde)`.

**Datos**: si existe `INDEC_TOKEN` (variable de entorno o `.streamlit/secrets.toml`,
token generado en https://api.indec.gob.ar) consulta la API; si no, usa
`data/ipc_nacional.csv` (columnas `periodo` AAAAMM e `indice`).
Si la autodetección de región/indicador falla, fijalos en `secrets.toml`:

```toml
[INDEC_IPC_FILTERS]
region = "..."
tipo_de_indicador_descripcion = "..."
descripcion = "..."
```

Tests: `python -m pytest`
