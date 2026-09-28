import streamlit as st

st.set_page_config(page_title="Promocalculator", page_icon="🏷️")

st.title("🏷️ Promocalculator")
st.caption("Calculá el precio final de un producto según la promoción aplicada.")

precio = st.number_input("Precio original ($)", min_value=0.0, value=1000.0, step=10.0)
cantidad = st.number_input("Cantidad", min_value=1, value=1, step=1)

promo = st.selectbox(
    "Tipo de promoción",
    [
        "Descuento porcentual",
        "Descuento de monto fijo",
        "2x1",
        "3x2",
        "2da unidad al 50%",
        "Cuotas con interés",
    ],
)

subtotal = precio * cantidad
total = subtotal
detalle = ""

if promo == "Descuento porcentual":
    pct = st.slider("Descuento (%)", 0, 100, 20)
    total = subtotal * (1 - pct / 100)
    detalle = f"{pct}% de descuento"
elif promo == "Descuento de monto fijo":
    monto = st.number_input("Monto a descontar ($)", min_value=0.0, value=100.0, step=10.0)
    total = max(subtotal - monto, 0.0)
    detalle = f"${monto:,.2f} de descuento"
elif promo == "2x1":
    total = precio * ((cantidad + 1) // 2)
    detalle = "Pagás la mitad de las unidades (redondeando hacia arriba)"
elif promo == "3x2":
    total = precio * (cantidad - cantidad // 3)
    detalle = "Cada 3 unidades pagás 2"
elif promo == "2da unidad al 50%":
    pares = cantidad // 2
    total = precio * (cantidad - pares * 0.5)
    detalle = "La segunda unidad de cada par tiene 50% de descuento"
elif promo == "Cuotas con interés":
    cuotas = st.selectbox("Cantidad de cuotas", [1, 3, 6, 12, 18, 24], index=1)
    tna = st.number_input("Interés total (%)", min_value=0.0, value=15.0, step=1.0)
    total = subtotal * (1 + tna / 100)
    detalle = f"{cuotas} cuotas de ${total / cuotas:,.2f}"

ahorro = subtotal - total

st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("Subtotal", f"${subtotal:,.2f}")
c2.metric("Total a pagar", f"${total:,.2f}")
c3.metric("Ahorro" if ahorro >= 0 else "Recargo", f"${abs(ahorro):,.2f}")
if detalle:
    st.info(detalle)
