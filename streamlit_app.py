import os

import streamlit as st

from ipc import actualizar, load_series

st.set_page_config(page_title="Promocalculator", page_icon="📈")
st.title("📈 Calculadora de inflación")
st.caption("Actualiza un monto con el IPC Nacional (nivel general) del INDEC.")


def _secret(name):
    try:
        return st.secrets.get(name)
    except Exception:
        return None


token = os.environ.get("INDEC_TOKEN") or _secret("INDEC_TOKEN")
filters = _secret("INDEC_IPC_FILTERS")
filters = dict(filters) if filters else None


@st.cache_data(ttl=6 * 3600, show_spinner="Cargando IPC…")
def cargar(token, filters):
    return load_series(token, filters)


serie, fuente = cargar(token, filters)
if serie.empty:
    st.error(
        "No hay datos de IPC. Configurá `INDEC_TOKEN` (ver README) o cargá "
        "`data/ipc_nacional.csv` con columnas `periodo` (AAAAMM) e `indice`."
    )
    st.stop()

periodos = list(serie["periodo"])
etiqueta = lambda p: p.strftime("%m/%Y")

c1, c2 = st.columns(2)
desde = c1.selectbox("Desde", periodos, index=max(len(periodos) - 13, 0), format_func=etiqueta)
hasta = c2.selectbox("Hasta", periodos, index=len(periodos) - 1, format_func=etiqueta)
monto = st.number_input("Monto ($)", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")

if desde > hasta:
    st.warning("El período inicial debe ser anterior o igual al final.")
else:
    r = actualizar(monto, serie, desde, hasta)
    st.metric(f"Monto a {etiqueta(hasta)}", f"$ {r['monto_actualizado']:,.2f}")
    m1, m2 = st.columns(2)
    m1.metric("Inflación acumulada", f"{r['variacion_pct']:.2f} %")
    m2.metric("Factor", f"{r['factor']:.4f}")
    st.line_chart(serie[(serie.periodo >= desde) & (serie.periodo <= hasta)].set_index(
        serie["periodo"].astype(str))["indice"])

st.caption(f"Fuente: {fuente}. Último dato: {etiqueta(periodos[-1])}.")
