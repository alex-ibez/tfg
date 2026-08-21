"""Registre de comportaments basat en atributs, no en ids prefixats."""

import random

from .bateria import Bateria
from .clima import temperatura_variada
from .diposit import Diposit


class MotorEntitats:
    """
    Detecta què representa cada JSON pels atributs que declara.

    Un JSON nou sempre es carrega, es guarda i s'envia. Si usa atributs
    reconeguts també rep automàticament el comportament corresponent.
    """

    def __init__(self, entitats):
        self.bateries = {}
        self.diposits = {}
        self.estances = {}

        for entitat in entitats:
            if entitat.te_atributs(
                "capacitat_maxima_kwh", "capacitat_actual_kwh"
            ):
                self.bateries[entitat.id] = Bateria(
                    entitat.valor("capacitat_maxima_kwh"),
                    entitat.valor("capacitat_actual_kwh"),
                )
            if entitat.te_atributs("volum_max_litres", "nivell_litres"):
                bomba = (
                    entitat.valor("bomba_activa")
                    if "bomba_activa" in entitat.atributs
                    else False
                )
                self.diposits[entitat.id] = Diposit(
                    entitat.valor("volum_max_litres"),
                    entitat.valor("nivell_litres"),
                    bomba,
                )

        self.energia = {}
        self.temperatura_base = 20.0
        self.bateria_pct = 0.0

    def iniciar_cicle(self, energia, clima, segons):
        self.energia = energia
        self.temperatura_base = clima["temperatura_c"]
        self.estances = {}

        for bateria in self.bateries.values():
            bateria.actualitzar(
                energia["produccio_w"], energia["consum_w"], segons
            )
        if self.bateries:
            primera = next(iter(self.bateries.values()))
            self.bateria_pct = primera.actual_kwh / primera.maxima_kwh * 100

        for diposit in self.diposits.values():
            diposit.actualitzar(segons)

    def _dades_estanca(self, nom):
        if nom not in self.estances:
            encesa = random.random() < 0.3
            humitat = round(random.uniform(35.0, 65.0), 1)
            self.estances[nom] = {
                "estanca": nom,
                "encesa": encesa,
                "consum_w": (
                    round(random.uniform(15.0, 30.0), 2) if encesa else 0.0
                ),
                "temperatura_c": temperatura_variada(self.temperatura_base),
                "humitat_pct": humitat,
                "humitat_": humitat,
                "ocupacio": random.random() < 0.4,
            }
        return self.estances[nom]

    def valors(self, entitat):
        """Calcula només valors d'atributs que el JSON ja conté."""
        atributs = entitat.atributs
        valors = {}

        if "potencia_w" in atributs:
            valors["potencia_w"] = round(self.energia["produccio_w"], 2)
        if "potencia_total_w" in atributs:
            valors["potencia_total_w"] = round(self.energia["consum_w"], 2)
        if "mode_estalvi" in atributs:
            valors["mode_estalvi"] = self.bateria_pct < 30
        if "alerta_bateria" in atributs:
            valors["alerta_bateria"] = self.bateria_pct < 20

        if entitat.id in self.bateries:
            valors.update(self.bateries[entitat.id].valors())
        if entitat.id in self.diposits:
            valors.update(self.diposits[entitat.id].valors())

        if "estanca" in atributs:
            valors.update(self._dades_estanca(entitat.valor("estanca")))

        if "co2_ppm" in atributs:
            co2 = random.randint(400, 1500)
            valors["co2_ppm"] = co2
            if "actiu" in atributs:
                valors["actiu"] = co2 > 800 or random.random() < 0.7
            if "mode" in atributs:
                valors["mode"] = "auto"

        # Qualsevol atribut de temperatura, també en JSON nous, prové del clima.
        for nom, meta in atributs.items():
            nom_min = nom.lower()
            if meta["type"] in ("Float", "Number") and (
                "temperatura" in nom_min or nom_min.startswith("temp_")
            ):
                valors[nom] = temperatura_variada(self.temperatura_base)

        # El filtre d'Entitat.actualitzar impedirà afegir atributs no declarats.
        return valors
