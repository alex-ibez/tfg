"""Descobriment i actualització dinàmica dels esquemes JSON."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Entitat:
    """Uneix una entitat NGSI amb el fitxer JSON d'on prové."""

    ruta: Path
    dades: dict

    @property
    def id(self):
        return self.dades["id"]

    @property
    def tipus(self):
        return self.dades["type"]

    @property
    def atributs(self):
        return {
            nom: meta
            for nom, meta in self.dades.items()
            if nom not in ("id", "type")
        }

    def te_atributs(self, *noms):
        return all(nom in self.atributs for nom in noms)

    def valor(self, nom):
        return self.dades[nom]["value"]

    def actualitzar(self, valors):
        """Canvia només els value que ja estan declarats a l'esquema."""
        for nom, valor in valors.items():
            if nom in self.atributs:
                self.dades[nom]["value"] = valor

    def guardar(self):
        with self.ruta.open("w", encoding="utf-8") as fitxer:
            json.dump(self.dades, fitxer, ensure_ascii=False, indent=2)
            fitxer.write("\n")


def carregar_entitats(carpeta):
    """Carrega qualsevol JSON vàlid afegit a la carpeta, sense llistes fixes."""
    entitats = []
    ids = {}

    for ruta in sorted(Path(carpeta).rglob("*.json")):
        with ruta.open(encoding="utf-8") as fitxer:
            dades = json.load(fitxer)

        if not isinstance(dades, dict) or "id" not in dades or "type" not in dades:
            raise ValueError(f"{ruta}: l'esquema necessita id i type")

        for nom, meta in dades.items():
            if nom in ("id", "type"):
                continue
            if not isinstance(meta, dict) or "type" not in meta or "value" not in meta:
                raise ValueError(f"{ruta}: l'atribut {nom} necessita type i value")

        if dades["id"] in ids:
            raise ValueError(
                f"Id duplicat {dades['id']} a {ids[dades['id']]} i {ruta}"
            )
        ids[dades["id"]] = ruta
        entitats.append(Entitat(ruta, dades))

    if not entitats:
        raise ValueError(f"No hi ha esquemes JSON a {carpeta}")
    return entitats
