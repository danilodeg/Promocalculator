# 💳 Promocalculator

App en Streamlit para calcular descuentos bancarios con tope de reintegro.

- **Una promo:** reintegro, precio final, descuento efectivo y monto óptimo para agotar el tope (considerando lo ya usado y la compra mínima).
- **Comparar y repartir:** tabla editable con varias promos (banco, billetera, tarjeta), filtro por día, ranking si pagás todo con una sola y la mejor forma de dividir la compra para maximizar el reintegro.

## Correrla localmente

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Tests: `pytest`

## Publicarla

En [share.streamlit.io](https://share.streamlit.io) → *Create app* → elegí este repo, rama `main`, archivo `streamlit_app.py`.
