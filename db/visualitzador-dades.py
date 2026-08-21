import pandas as pd
import matplotlib.pyplot as plt

def analizar_datos():
    print("Cargando dataset unificado...")
    df = pd.read_csv("/home/alex/tfg/db/dataset_veinat_completo1.csv")
    df['fecha'] = pd.to_datetime(df['fecha'])
    df.set_index('fecha', inplace=True)

    print("Generando panel de telemetría de la vivienda 'Veïnat'...")
    plt.figure(figsize=(16, 12))

    # Muestra de la primera semana de simulación (168 registros)
    semana_muestra = df.head(24 * 7)

    # --- SUBGRÁFICA 1: Balance de Potencia Eléctrica ---
    plt.subplot(4, 1, 1)
    plt.plot(semana_muestra.index, semana_muestra['produccion_w'], label='Producción Fotovoltaica (W)', color='#22c55e', alpha=0.8)
    plt.plot(semana_muestra.index, semana_muestra['consumo_w'], label='Consumo del Hogar (W)', color='#f59e0b', alpha=0.8)
    plt.title('1. SUBSISTEMA ELÉCTRICO: Balance de Potencia Activa')
    plt.ylabel('Vatios (W)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)

    # --- SUBGRÁFICA 2: Estado de Carga de la Batería ---
    plt.subplot(4, 1, 2)
    plt.plot(semana_muestra.index, semana_muestra['bateria_soc_pct'], label='Nivel de Batería (SOC %)', color='#3b82f6', linewidth=2)
    plt.axhline(100, color='gray', linestyle=':')
    plt.axhline(5, color='red', linestyle='--', label='Corte por Inversor (5%)')
    plt.title('2. ALMACENAMIENTO ELÉCTRICO: Estado de Carga de Baterías')
    plt.ylabel('Porcentaje (%)')
    plt.ylim(0, 110)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)

    # --- SUBGRÁFICA 3: Volumen del Depósito de Agua ---
    plt.subplot(4, 1, 3)
    plt.plot(semana_muestra.index, semana_muestra['nivel_agua_litres'], label='Agua Disponible (Litros)', color='#06b6d4', linewidth=2)
    plt.fill_between(semana_muestra.index, semana_muestra['nivel_agua_litres'], color='#06b6d4', alpha=0.1)
    plt.axhline(300, color='blue', linestyle=':', label='Límite de Rebose (300L)')
    plt.title('3. SUBSISTEMA HIDRÁULICO: Volumen Almacenado en Depósito de Emergencia')
    plt.ylabel('Litros (L)')
    plt.ylim(0, 330)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)

    # --- SUBGRÁFICA 4: Consumo de Agua ---
    plt.subplot(4, 1, 4)
    plt.plot(semana_muestra.index, semana_muestra['consumo_agua_lh'], label='Consumo de Red Interna (L/h)', color='#ef4444', linewidth=1.5)
    plt.title('4. FLUJOS HIDRÁULICOS: Consumo Horario')
    plt.xlabel('Evolución Temporal (Fecha/Hora)')
    plt.ylabel('Caudal (L/h)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    analizar_datos()
