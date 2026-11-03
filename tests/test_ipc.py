import pandas as pd
from ipc import actualizar, _normalize


def test_actualizar_usa_cociente_de_indices():
    serie = _normalize(pd.DataFrame({"periodo": [202401, 202402, 202403], "indice": [100.0, 110.0, 121.0]}))
    r = actualizar(1000, serie, pd.Period("2024-01"), pd.Period("2024-03"))
    assert round(r["monto_actualizado"], 2) == 1210.00
    assert round(r["variacion_pct"], 2) == 21.00


def test_periodo_inexistente():
    serie = _normalize(pd.DataFrame({"periodo": [202401], "indice": [100.0]}))
    try:
        actualizar(1, serie, pd.Period("2020-01"), pd.Period("2024-01"))
        assert False
    except KeyError:
        pass
