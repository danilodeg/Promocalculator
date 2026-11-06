"""Lógica de cálculo de descuentos bancarios con tope de reintegro."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Promo:
    nombre: str
    porcentaje: float  # 0 a 100
    tope: float | None = None  # reintegro máximo; None = sin tope
    usado: float = 0.0  # parte del tope ya consumida en el período
    minimo: float = 0.0  # compra mínima para que aplique

    @property
    def tope_disponible(self) -> float:
        if self.tope is None:
            return math.inf
        return max(self.tope - self.usado, 0.0)


def reintegro(monto: float, promo: Promo) -> float:
    """Reintegro que da una promo sobre una compra."""
    if monto <= 0 or promo.porcentaje <= 0 or monto < promo.minimo:
        return 0.0
    return min(monto * promo.porcentaje / 100, promo.tope_disponible)


def monto_optimo(promo: Promo) -> float:
    """Monto a partir del cual se agota el tope (gastar más no suma reintegro)."""
    if promo.porcentaje <= 0:
        return 0.0
    if promo.tope is None:
        return math.inf
    return max(promo.tope_disponible / (promo.porcentaje / 100), promo.minimo)


def descuento_efectivo(monto: float, promo: Promo) -> float:
    """Porcentaje real de ahorro sobre el total (cae cuando se pasa el tope)."""
    return 0.0 if monto <= 0 else reintegro(monto, promo) / monto * 100


def repartir(monto: float, promos: list[Promo]) -> tuple[list[dict], float]:
    """Divide una compra entre varias promos para maximizar el reintegro.

    Asigna primero a la promo de mayor porcentaje hasta agotar su tope,
    después a la siguiente, etc. Lo que sobra se paga sin descuento.
    """
    restante = monto
    filas: list[dict] = []
    for p in sorted(promos, key=lambda p: p.porcentaje, reverse=True):
        if restante <= 0:
            break
        if p.porcentaje <= 0 or p.tope_disponible <= 0:
            continue
        asignado = min(restante, monto_optimo(p))
        if asignado < p.minimo or asignado <= 0:
            continue
        r = reintegro(asignado, p)
        filas.append({"promo": p.nombre, "pagar": asignado, "reintegro": r})
        restante -= asignado
    if restante > 0:
        filas.append({"promo": "Sin descuento", "pagar": restante, "reintegro": 0.0})
    return filas, sum(f["reintegro"] for f in filas)
