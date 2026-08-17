"""
Punt d'entrada del simulador.

Cada cicle:
1. Llegeix una fila d'energia i una de clima.
2. Actualitza els models acumulatius (bateria i dipòsit).
3. Calcula els atributs de cada JSON descobert dinàmicament.
4. Guarda cada JSON i l'envia individualment a Orion.
"""

import argparse
import json
import time
from pathlib import Path

from simulador_moduls.entitats import MotorEntitats
from simulador_moduls.esquemes import carregar_entitats
from simulador_moduls.fonts_csv import carregar_clima, carregar_energia
from simulador_moduls.orion import ClientOrion


ARREL = Path(__file__).resolve().parent
ORION_URL = "http://100.97.229.121:1026"
CARPETA_ESQUEMES = ARREL / "esquema-json"
CARPETA_ENERGIA = ARREL / "db" / "generacio"
CARPETA_CLIMA = ARREL / "db" / "clima"
SEGONS_ENTRE_CICLES = 5


def arguments():
    parser = argparse.ArgumentParser(description="Simulador modular del veïnat")
    parser.add_argument("--loop", type=int, default=0, help="0 = cicles infinits")
    return parser.parse_args()


def seleccionar_csv(titol, carpeta):
    """Mostra els CSV disponibles i retorna el que seleccione l'usuari."""
    opcions = sorted(carpeta.glob("*.csv"))
    if not opcions:
        raise FileNotFoundError(
            f"No hi ha cap CSV per a {titol.lower()} a {carpeta}"
        )

    print(f"\nCSV de {titol}:")
    for numero, ruta in enumerate(opcions, start=1):
        print(f"{numero}) {ruta.name}")

    while True:
        try:
            seleccio = int(input(f"\n Selecciona el CSV de {titol.lower()}: "))
            return opcions[seleccio - 1]
        except (ValueError, IndexError):
            print(f"\n Selecciona un número entre 1 i {len(opcions)}.")


def main():
    args = arguments()
    if args.loop < 0:
        raise ValueError("--loop no pot ser negatiu")

    # No hi ha ids ni estances escrits al codi: tot surt dels JSON disponibles.
    entitats = carregar_entitats(CARPETA_ESQUEMES)
    ruta_energia = seleccionar_csv("energia", CARPETA_ENERGIA)
    ruta_clima = seleccionar_csv("clima", CARPETA_CLIMA)
    energia = carregar_energia(ruta_energia)
    clima = carregar_clima(ruta_clima)
    motor = MotorEntitats(entitats)
    orion = ClientOrion(ORION_URL)

    print(f"Simulador iniciat amb {len(entitats)} entitats")
    cicle = 0

    try:
        while args.loop == 0 or cicle < args.loop:
            cicle += 1
            fila_energia = energia.seguent()
            fila_clima = clima.seguent()
            motor.iniciar_cicle(
                fila_energia, fila_clima, SEGONS_ENTRE_CICLES
            )

            balanc = fila_energia["produccio_w"] - fila_energia["consum_w"]
            print(
                f"\nCicle {cicle} | {fila_energia['fecha']} | "
                f"producció {fila_energia['produccio_w']:.2f} W | "
                f"consum {fila_energia['consum_w']:.2f} W | "
                f"balanç {balanc:.2f} W"
            )

            for entitat in entitats:
                entitat.actualitzar(motor.valors(entitat))
                entitat.guardar()
                orion.enviar(entitat)

            if args.loop == 0 or cicle < args.loop:
                time.sleep(SEGONS_ENTRE_CICLES)
    except KeyboardInterrupt:
        print("\nSimulador aturat")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"Error de configuració: {error}") from error
