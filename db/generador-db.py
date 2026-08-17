import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# --- CONFIGURACIÓN DEL DATASET ---
FECHA_INICIO = datetime(2023, 1, 1, 0, 0, 0)
DIAS_A_SIMULAR = 180  # 6 meses de datos históricos
INTERVALO_MINUTOS = 60  # Un registro por hora

def generar_dataset():
    print(f"Generando dataset unificado (Energía + Agua) de {DIAS_A_SIMULAR} días...")
    datos = []
    
    # Estado inicial Sistema Energético
    bateria_soc = 50.0  # %
    capacidad_bat_kwh = 62.0
    
    # Estado inicial Sistema Hidráulico
    capacidad_agua_litres = 300.0
    nivel_agua_litres = 240.0  # Iniciamos al 80%
    
    fecha_actual = FECHA_INICIO
    tiempo_total = DIAS_A_SIMULAR * 24 * (60 // INTERVALO_MINUTOS)
    
    for _ in range(tiempo_total):
        hora = fecha_actual.hour
        mes = fecha_actual.month
        
        # --- 1. CLIMA Y RADIACIÓN ---
        prob_nuvol = 0.20 if mes in [4, 5, 10, 11] else 0.08
        es_nuvol = random.random() < prob_nuvol
        
        # --- 2. SIMULACIÓN ELÉCTRICA ---
        if 7 <= hora <= 19:
            produccion_w = 3000 * (1 - abs((hora - 13) / 6)) + random.gauss(0, 100)
            if mes in [1, 2, 11, 12]: produccion_w *= 0.6  # Invierno
            if es_nuvol: produccion_w *= 0.15              # Núvols densos redueixen la producció
        else:
            produccion_w = 0
        produccion_w = max(0, produccion_w)
        
        consumo_base_w = random.uniform(200, 500)
        if 7 <= hora <= 9 or 19 <= hora <= 22:
            consumo_w = consumo_base_w + random.uniform(1000, 2500)  # Picos de actividad
        else:
            consumo_w = consumo_base_w + random.uniform(0, 300)
            
        balance_w = produccion_w - consumo_w
        energia_kwh = (balance_w / 1000) * (INTERVALO_MINUTOS / 60)
        bateria_soc += (energia_kwh / capacidad_bat_kwh) * 100
        bateria_soc = max(5.0, min(100.0, bateria_soc))
        
        # --- 3. SIMULACIÓN HIDRÁULICA ---
        # Consumo de agua (duchas matutinas y cenas/lavavajillas por la noche)
        if 7 <= hora <= 9:
            consumo_agua_lh = random.uniform(20, 50)
        elif 20 <= hora <= 22:
            consumo_agua_lh = random.uniform(15, 35)
        else:
            consumo_agua_lh = random.uniform(1, 5)  # Consumo base mínimo
            
        # Balanç del dipòsit segons el consum.
        nivel_agua_litres = nivel_agua_litres - consumo_agua_lh
        nivel_agua_litres = max(0.0, min(capacidad_agua_litres, nivel_agua_litres))
        nivel_agua_pct = (nivel_agua_litres / capacidad_agua_litres) * 100
        
        # --- 4. EXTRACCIÓN DE DATOS ---
        datos.append({
            "fecha": fecha_actual.strftime("%Y-%m-%d %H:%M:%S"),
            "hora_del_dia": hora,
            "mes": mes,
            "produccion_w": round(produccion_w, 2),
            "consumo_w": round(consumo_w, 2),
            "balance_w": round(balance_w, 2),
            "bateria_soc_pct": round(bateria_soc, 2),
            "temp_exterior": round(15 + 10 * (1 - abs((hora - 14) / 10)) + random.gauss(0, 2), 1),
            "consumo_agua_lh": round(consumo_agua_lh, 2),
            "nivel_agua_litres": round(nivel_agua_litres, 2),
            "nivel_agua_pct": round(nivel_agua_pct, 2)
        })
        
        fecha_actual += timedelta(minutes=INTERVALO_MINUTOS)

    nombre_archivo = Path(__file__).parent / "dataset_veinat_completo.csv"
    with nombre_archivo.open("w", newline="", encoding="utf-8") as fitxer:
        escriptor = csv.DictWriter(
            fitxer, fieldnames=datos[0].keys(), lineterminator="\n"
        )
        escriptor.writeheader()
        escriptor.writerows(datos)
    print(f"Dataset unificado completado con éxito: {len(datos)} registros.")
    print(f"Archivo guardado listo para Kaggle como: {nombre_archivo}")

if __name__ == "__main__":
    generar_dataset()