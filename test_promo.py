import math

from promo import Promo, descuento_efectivo, monto_optimo, reintegro, repartir


def test_reintegro_con_tope():
    p = Promo("A", 30, tope=15000)
    assert reintegro(10000, p) == 3000
    assert reintegro(100000, p) == 15000
    assert monto_optimo(p) == 50000
    assert descuento_efectivo(100000, p) == 15


def test_usado_y_minimo():
    p = Promo("A", 25, tope=10000, usado=2000, minimo=5000)
    assert reintegro(4000, p) == 0
    assert reintegro(100000, p) == 8000
    assert monto_optimo(p) == 32000


def test_sin_tope():
    p = Promo("A", 10)
    assert reintegro(1_000_000, p) == 100_000
    assert math.isinf(monto_optimo(p))


def test_repartir():
    promos = [Promo("A", 30, 15000), Promo("B", 20, 8000, minimo=10000), Promo("C", 25, 10000, 2000)]
    filas, total = repartir(120000, promos)
    assert [f["promo"] for f in filas] == ["A", "C", "B"]
    assert [f["pagar"] for f in filas] == [50000, 32000, 38000]
    assert total == 15000 + 8000 + 7600
    assert sum(f["pagar"] for f in filas) == 120000
