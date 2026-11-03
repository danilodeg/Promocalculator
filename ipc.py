"""Datos y cálculo del IPC Nacional (INDEC) para la calculadora de inflación."""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

API_BASE = "https://api.indec.gob.ar/v1/ipc_nacional"
CSV_PATH = Path(__file__).parent / "data" / "ipc_nacional.csv"


def _get(url: str, token: str) -> list[dict]:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def _pick(values, *needles):
    """Primer valor que contiene todos los textos (sin distinguir mayúsculas)."""
    for v in values:
        s = str(v).lower()
        if all(n in s for n in needles):
            return v
    return None


def load_from_api(token: str, filters: dict | None = None) -> pd.DataFrame:
    """Serie mensual del índice IPC nivel general nacional.

    Los textos exactos de region/nivel/indicador los define el INDEC y no
    están en la spec; si no se pasan en `filters` se detectan sobre el último
    período. Se pueden fijar con la config `filters` (ver README).
    """
    filters = dict(filters or {})
    if not filters:
        last = _get(f"{API_BASE}?select=periodo&order=periodo.desc&limit=1", token)[0]["periodo"]
        rows = _get(f"{API_BASE}?periodo=eq.{last}&limit=1000", token)
        df = pd.DataFrame(rows)
        region = _pick(df["region"].unique(), "nacional")
        indic = _pick(df["tipo_de_indicador_descripcion"].dropna().unique(), "índice") or _pick(
            df["tipo_de_indicador_descripcion"].dropna().unique(), "indice"
        )
        general = _pick(df["descripcion"].dropna().unique(), "nivel general")
        if not (region and indic and general):
            raise RuntimeError(
                "No pude identificar región/indicador/nivel general del IPC; "
                "definilos en la config 'filters'."
            )
        filters = {
            "region": region,
            "tipo_de_indicador_descripcion": indic,
            "descripcion": general,
        }
    q = "&".join(f"{k}=eq.{urllib.parse.quote(str(v))}" for k, v in filters.items())
    rows = _get(f"{API_BASE}?{q}&select=periodo,valor&order=periodo&limit=1000", token)
    return _normalize(pd.DataFrame(rows).rename(columns={"valor": "indice"}))


def load_from_csv(path: Path = CSV_PATH) -> pd.DataFrame:
    return _normalize(pd.read_csv(path))


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["periodo", "indice"])
    df = df[["periodo", "indice"]].copy()
    df["periodo"] = pd.to_datetime(df["periodo"].astype(str), format="%Y%m").dt.to_period("M")
    df["indice"] = pd.to_numeric(df["indice"])
    return df.drop_duplicates("periodo").sort_values("periodo").reset_index(drop=True)


def load_series(token: str | None = None, filters: dict | None = None) -> tuple[pd.DataFrame, str]:
    """API si hay token; si falla o no hay, CSV local. Devuelve (serie, fuente)."""
    if token:
        try:
            return load_from_api(token, filters), "API INDEC"
        except Exception as exc:  # red, auth, formato inesperado
            err = f" (la API falló: {exc})"
    else:
        err = ""
    return load_from_csv(), "CSV local" + err


def actualizar(monto: float, serie: pd.DataFrame, desde: pd.Period, hasta: pd.Period) -> dict:
    """Actualiza `monto` expresado en precios de `desde` a precios de `hasta`."""
    idx = serie.set_index("periodo")["indice"]
    if desde not in idx.index or hasta not in idx.index:
        raise KeyError("Período fuera de la serie disponible")
    factor = idx[hasta] / idx[desde]
    return {"factor": factor, "variacion_pct": (factor - 1) * 100, "monto_actualizado": monto * factor}
