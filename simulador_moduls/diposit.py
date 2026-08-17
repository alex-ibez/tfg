"""Model acumulatiu del dipòsit i la bomba d'aigua."""

import random


class Diposit:
    def __init__(self, maxim_litres, actual_litres, bomba_activa=False):
        self.maxim_litres = float(maxim_litres)
        self.actual_litres = float(actual_litres)
        self.bomba_activa = bool(bomba_activa)
        if self.maxim_litres <= 0:
            raise ValueError("El volum màxim del dipòsit ha de ser positiu")
        if not 0 <= self.actual_litres <= self.maxim_litres:
            raise ValueError("El nivell actual del dipòsit està fora de límits")

    def actualitzar(self, segons):
        """Aplica els cabals de consum i bomba durant el temps real del cicle."""
        percentatge = self.actual_litres / self.maxim_litres
        if percentatge <= 0.35:
            self.bomba_activa = True
        elif percentatge >= 0.90:
            self.bomba_activa = False

        hores = segons / 3600.0
        consum_litres = random.uniform(3.0, 18.0) * hores
        entrada_litres = (
            random.uniform(60.0, 90.0) * hores if self.bomba_activa else 0.0
        )
        self.actual_litres = max(
            0.0,
            min(
                self.maxim_litres,
                self.actual_litres + entrada_litres - consum_litres,
            ),
        )

    def valors(self):
        return {
            "nivell_litres": round(self.actual_litres, 1),
            "volum_max_litres": self.maxim_litres,
            "bomba_activa": self.bomba_activa,
        }
