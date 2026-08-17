"""Lectors cíclics per a les fonts d'energia i clima."""

import csv
from pathlib import Path


def _llegir_text(ruta):
    ruta = Path(ruta)
    if not ruta.is_file():
        raise FileNotFoundError(f"No existeix el fitxer {ruta}")
    try:
        return ruta.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return ruta.read_text(encoding="latin-1")


def _numero(valor):
    return float(str(valor).strip().replace(" ", "").replace(",", "."))


def _files_csv(ruta):
    text = _llegir_text(ruta)
    primera = text.splitlines()[0] if text.splitlines() else ""
    separador = ";" if primera.count(";") > primera.count(",") else ","
    lector = csv.DictReader(text.splitlines(), delimiter=separador)
    return set(lector.fieldnames or []), lector


class FontCiclica:
    """Retorna files en ordre i torna al principi en arribar al final."""

    def __init__(self, files):
        if not files:
            raise ValueError("La font CSV no conté files vàlides")
        self.files = files
        self.index = 0

    def seguent(self):
        fila = self.files[self.index]
        self.index = (self.index + 1) % len(self.files)
        return fila


def carregar_energia(ruta):
    """Adapta generacio_panells.csv a producció i consum en watts."""
    columnes, lector = _files_csv(ruta)
    simple = {"fecha", "produccion_w", "consumo_w"}.issubset(columnes)
    consum_original = next(
        (nom for nom in ("Cosumo (W)", "Consumo (W)") if nom in columnes),
        None,
    )
    produccio_original = next(
        (
            nom
            for nom in ("Generación Total (W)", "Generacio Total (W)")
            if nom in columnes
        ),
        None,
    )

    if not simple and not (consum_original and produccio_original):
        raise ValueError("El CSV energètic no té columnes reconegudes")

    files = []
    for numero, fila in enumerate(lector, start=2):
        try:
            if simple:
                fecha = fila["fecha"]
                produccio = _numero(fila["produccion_w"])
                consum = _numero(fila["consumo_w"])
            else:
                if not (fila.get(consum_original) or "").strip():
                    continue
                if not (fila.get(produccio_original) or "").strip():
                    continue
                fecha = (
                    f"{fila.get('Mes', '')} {fila.get('Dia', '')} "
                    f"{fila.get('Hora (24h)', '')}"
                ).strip()
                produccio = _numero(fila[produccio_original])
                consum = _numero(fila[consum_original])
        except (TypeError, ValueError) as error:
            raise ValueError(f"Fila energètica {numero} invàlida") from error

        if produccio < 0 or consum < 0:
            raise ValueError(f"Fila energètica {numero} amb valors negatius")
        files.append({"fecha": fecha, "produccio_w": produccio, "consum_w": consum})

    return FontCiclica(files)


def carregar_clima(ruta):
    """Llegeix una temperatura base de clima_simulacio.csv."""
    columnes, lector = _files_csv(ruta)
    columna_temperatura = next(
        (
            nom
            for nom in ("temperatura_c", "temp_exterior", "temperatura")
            if nom in columnes
        ),
        None,
    )
    if columna_temperatura is None:
        raise ValueError("El CSV climàtic no té una columna de temperatura")

    files = []
    for numero, fila in enumerate(lector, start=2):
        try:
            temperatura = _numero(fila[columna_temperatura])
        except (TypeError, ValueError) as error:
            raise ValueError(f"Fila climàtica {numero} invàlida") from error
        files.append(
            {
                "fecha": fila.get("fecha", str(numero - 1)),
                "temperatura_c": temperatura,
            }
        )
    return FontCiclica(files)
