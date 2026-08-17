from flask import Flask, request
import sqlite3
import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('historico_veinat.db')
    c = conn.cursor()
    # Creamos la tabla para guardar todo el histórico
    c.execute('''CREATE TABLE IF NOT EXISTS lecturas
                 (fecha TEXT, entidad_id TEXT, tipo TEXT, atributo TEXT, valor TEXT)''')
    conn.commit()
    conn.close()

@app.route('/orion-webhook', methods=['POST'])
def orion_webhook():
    data = request.json
    if not data or 'data' not in data:
        return 'OK', 200
    
    conn = sqlite3.connect('historico_veinat.db')
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    
    # Orion envía los datos dentro del array 'data'
    for entity in data['data']:
        ent_id = entity.get('id')
        ent_type = entity.get('type')
        
        # Iteramos sobre los atributos de la entidad
        for attr_name, attr_val in entity.items():
            if attr_name not in ['id', 'type'] and isinstance(attr_val, dict) and 'value' in attr_val:
                val = attr_val['value']
                c.execute("INSERT INTO lecturas VALUES (?, ?, ?, ?, ?)", 
                          (now, ent_id, ent_type, attr_name, str(val)))
    
    conn.commit()
    conn.close()
    print(f"[{now}] Datos guardados de {len(data['data'])} entidades.")
    return 'OK', 200

if __name__ == '__main__':
    init_db()
    # Ejecutamos el servidor en el puerto 5000
    app.run(host='0.0.0.0', port=5000)