import math

import pandas as pd
import streamlit as st

from promo import Promo, descuento_efectivo, monto_optimo, reintegro, repartir

st.set_page_config(page_title="Promocalculator", page_icon="💳", layout="centered")


def pesos(x: float) -> str:
    if math.isinf(x):
        return "sin límite"
    return "$ " + f"{x:,.0f}".replace(",", ".")


st.title("💳 Promocalculator")
st.caption("Calculá cuánto te reintegran los descuentos bancarios con tope y cómo aprovecharlos.")

tab_una, tab_varias = st.tabs(["Una promo", "Comparar y repartir"])

# --- Una promo -------------------------------------------------------------
with tab_una:
    c1, c2 = st.columns(2)
    monto = c1.number_input("Monto de la compra ($)", min_value=0.0, value=100000.0, step=1000.0)
    pct = c2.number_input("Descuento (%)", min_value=0.0, max_value=100.0, value=30.0, step=5.0)
    c3, c4 = st.columns(2)
    tope = c3.number_input("Tope de reintegro ($, 0 = sin tope)", min_value=0.0, value=15000.0, step=1000.0)
    usado = c4.number_input("Ya usado del tope en el período ($)", min_value=0.0, value=0.0, step=1000.0)
    minimo = st.number_input("Compra mínima ($)", min_value=0.0, value=0.0, step=1000.0)

    p = Promo("Promo", pct, tope if tope > 0 else None, usado, minimo)
    r = reintegro(monto, p)

    m1, m2, m3 = st.columns(3)
    m1.metric("Reintegro", pesos(r))
    m2.metric("Pagás en realidad", pesos(monto - r))
    m3.metric("Descuento efectivo", f"{descuento_efectivo(monto, p):.1f} %")

    opt = monto_optimo(p)
    if monto < p.minimo:
        st.warning(f"No llegás a la compra mínima de {pesos(p.minimo)}.")
    elif p.tope is not None and p.tope_disponible == 0:
        st.error("Ya agotaste el tope de esta promo en el período.")
    elif not math.isinf(opt) and monto > opt:
        st.info(
            f"Pasaste el tope: lo ideal es gastar hasta **{pesos(opt)}** con esta promo. "
            f"Los {pesos(monto - opt)} restantes no suman reintegro; conviene pagarlos con otro medio."
        )
    elif not math.isinf(opt):
        st.success(f"Te quedan {pesos(opt - monto)} de compra para agotar el tope.")

# --- Varias promos -------------------------------------------------------
with tab_varias:
    st.write("Cargá tus promos (podés editar, agregar o borrar filas).")
    dias = ["Todos", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    if "promos" not in st.session_state:
        st.session_state.promos = pd.DataFrame(
            [
                {"Promo": "Banco A", "Día": "Miércoles", "%": 30.0, "Tope": 15000.0, "Usado": 0.0, "Mínimo": 0.0},
                {"Promo": "Billetera B", "Día": "Todos", "%": 20.0, "Tope": 8000.0, "Usado": 0.0, "Mínimo": 10000.0},
                {"Promo": "Tarjeta C", "Día": "Miércoles", "%": 25.0, "Tope": 10000.0, "Usado": 2000.0, "Mínimo": 0.0},
            ]
        )

    df = st.data_editor(
        st.session_state.promos,
        num_rows="dynamic",
        width="stretch",
        column_config={
            "Día": st.column_config.SelectboxColumn(options=dias, required=True, default="Todos"),
            "%": st.column_config.NumberColumn(min_value=0, max_value=100, format="%.0f %%"),
            "Tope": st.column_config.NumberColumn("Tope ($, 0 = sin tope)", min_value=0, format="$ %.0f"),
            "Usado": st.column_config.NumberColumn("Ya usado ($)", min_value=0, format="$ %.0f"),
            "Mínimo": st.column_config.NumberColumn("Compra mínima ($)", min_value=0, format="$ %.0f"),
        },
        key="editor",
    )

    c1, c2 = st.columns(2)
    total = c1.number_input("Monto total a gastar ($)", min_value=0.0, value=120000.0, step=1000.0)
    dia = c2.selectbox("¿Qué día comprás?", dias, index=0)

    promos = []
    for _, f in df.dropna(subset=["Promo", "%"]).iterrows():
        if dia != "Todos" and f.get("Día") not in ("Todos", dia):
            continue
        t = float(f.get("Tope") or 0)
        promos.append(
            Promo(
                str(f["Promo"]),
                float(f["%"]),
                t if t > 0 else None,
                float(f.get("Usado") or 0),
                float(f.get("Mínimo") or 0),
            )
        )

    if not promos:
        st.warning("No hay promos que apliquen ese día.")
    else:
        st.subheader("Si pagás todo con una sola")
        ranking = pd.DataFrame(
            [
                {
                    "Promo": p.nombre,
                    "Reintegro": reintegro(total, p),
                    "Descuento efectivo": f"{descuento_efectivo(total, p):.1f} %",
                    "Gasto óptimo": pesos(monto_optimo(p)),
                }
                for p in promos
            ]
        ).sort_values("Reintegro", ascending=False)
        ranking["Reintegro"] = ranking["Reintegro"].map(pesos)
        st.dataframe(ranking, hide_index=True, width="stretch")

        st.subheader("Mejor forma de repartir la compra")
        filas, ahorro = repartir(total, promos)
        tabla = pd.DataFrame(filas).rename(
            columns={"promo": "Pagar con", "pagar": "Monto", "reintegro": "Reintegro"}
        )
        tabla["Monto"] = tabla["Monto"].map(pesos)
        tabla["Reintegro"] = tabla["Reintegro"].map(pesos)
        st.dataframe(tabla, hide_index=True, width="stretch")
        a1, a2 = st.columns(2)
        a1.metric("Reintegro total", pesos(ahorro))
        a2.metric("Descuento efectivo", f"{(ahorro / total * 100 if total else 0):.1f} %")
        st.caption("Sugerencia: llená primero los topes de mayor porcentaje. Verificá siempre las bases y condiciones de cada promo.")
