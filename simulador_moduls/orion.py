"""Publicació individual d'entitats a Orion Context Broker."""

import requests


class ClientOrion:
    def __init__(self, url):
        self.url = url.rstrip("/")
        self.headers = {"Content-Type": "application/json"}

    def enviar(self, entitat):
        """Actualitza una entitat; si no existeix, la crea amb el JSON complet."""
        atributs = entitat.atributs
        try:
            resposta = requests.patch(
                f"{self.url}/v2/entities/{entitat.id}/attrs",
                json=atributs,
                headers=self.headers,
                timeout=3,
            )
            if resposta.status_code in (200, 204):
                print(f"{entitat.id}: actualitzada")
                return True
            if resposta.status_code != 404:
                print(f"{entitat.id}: error HTTP {resposta.status_code}")
                return False

            resposta = requests.post(
                f"{self.url}/v2/entities",
                json=entitat.dades,
                headers=self.headers,
                timeout=3,
            )
            if resposta.status_code in (200, 201, 204):
                print(f"{entitat.id}: creada")
                return True
            print(f"{entitat.id}: error HTTP {resposta.status_code}")
        except requests.RequestException as error:
            print(f"{entitat.id}: Orion no disponible ({error})")
        return False
