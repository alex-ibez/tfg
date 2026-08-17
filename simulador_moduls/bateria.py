"""Model acumulatiu d'una bateria ideal."""


class Bateria:
    def __init__(self, maxima_kwh, actual_kwh):
        self.maxima_kwh = float(maxima_kwh)
        self.actual_kwh = float(actual_kwh)
        if self.maxima_kwh <= 0:
            raise ValueError("La capacitat màxima de bateria ha de ser positiva")
        if not 0 <= self.actual_kwh <= self.maxima_kwh:
            raise ValueError("La capacitat actual de bateria està fora de límits")

    def actualitzar(self, produccio_w, consum_w, segons):
        """Integra només l'energia real produïda durant el cicle."""
        balanc_w = produccio_w - consum_w
        variacio_kwh = (balanc_w / 1000.0) * (segons / 3600.0)
        self.actual_kwh = max(
            0.0, min(self.maxima_kwh, self.actual_kwh + variacio_kwh)
        )
        return balanc_w

    def valors(self):
        return {
            "capacitat_maxima_kwh": self.maxima_kwh,
            "capacitat_actual_kwh": round(self.actual_kwh, 3),
        }
