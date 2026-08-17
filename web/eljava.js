// =====================
//  Veinat Dashboard JS
//  NOMÉS LECTURA - Espejo del JSON de ORION
// =====================

const ORION_URL = "http://100.97.229.121:1026";
const MAX_POINTS = 96;

let batteryLevel;
let batChart, histChart, tempChart, humChart, waterLevelChart;
let orionConnected = false;

// Registre d'events generats per l'automatitzacio (n8n) i llegits d'Orion
let lastEventTs = 0;
let eventsInit = false;

const baseOpts = {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
        y: { grid: { color: '#e2e8f0' }, ticks: { color: '#64748b', font: { size: 9, family: 'JetBrains Mono' } } },
        x: { display: false }
    },
    animation: { duration: 300 }
};

function mkChart(id, color, yMin, yMax) {
    const opts = JSON.parse(JSON.stringify(baseOpts));
    if (yMin !== undefined) { opts.scales.y.min = yMin; opts.scales.y.max = yMax; }
    return new Chart(document.getElementById(id), {
        type: 'line',
        data: {
            labels: Array(MAX_POINTS).fill(''),
            datasets: [{ data: Array(MAX_POINTS).fill(0), borderColor: color, borderWidth: 2, fill: true, backgroundColor: color + '18', tension: 0.4, pointRadius: 0 }]
        },
        options: opts
    });
}

function initCharts() {
    batChart  = mkChart('batteryChart', '#22c55e', 0, 100);
    tempChart = mkChart('tempChart',    '#FF6366', 0, 40);
    humChart  = mkChart('humChart',     '#06b6d4', 0, 100);
    waterLevelChart = mkChart('waterChart', '#3b82f6', 0, 100);

    const hOpts = JSON.parse(JSON.stringify(baseOpts));
    histChart = new Chart(document.getElementById('historialChart'), {
        type: 'line',
        data: {
            labels: Array(MAX_POINTS).fill(''),
            datasets: [
                { data: Array(MAX_POINTS).fill(0), borderColor: '#f59e0b', borderWidth: 2, tension: 0.4, pointRadius: 0, fill: false },
                { data: Array(MAX_POINTS).fill(0), borderColor: '#22c55e', borderWidth: 2, tension: 0.4, pointRadius: 0, fill: false, borderDash: [4, 3] }
            ]
        },
        options: hOpts
    });
}

function push(chart, val, idx) {
    chart.data.datasets[idx || 0].data.push(val);
    chart.data.datasets[idx || 0].data.shift();
}

async function getEntity(entityId) {
    try {
        const resp = await fetch(`${ORION_URL}/v2/entities/${entityId}`);
        if (!resp.ok) return null;
        return await resp.json();
    } catch (e) { return null; }
}

function getAttr(entity, attrName, defaultValue = null) {
    if (!entity || !entity[attrName]) return defaultValue;
    return entity[attrName].value !== undefined ? entity[attrName].value : defaultValue;
}

async function checkOrionConnection() {
    try {
        const resp = await fetch(`${ORION_URL}/version`);
        orionConnected = resp.ok;
        return orionConnected;
    } catch {
        orionConnected = false;
        return false;
    }
}

async function updateSensors() {
    if (!orionConnected && !await checkOrionConnection()) return;

    try {
        // 1. LECTURA DE PLAQUES I CONSUM
        const solar = await getEntity("SolarPanel:Veinat:001");
        const produccio = solar ? getAttr(solar, 'potencia_w', 0) : 0;

        const consum_ent = await getEntity("Consum:Veinat:001");
        const consum_w = consum_ent ? getAttr(consum_ent, 'potencia_total_w', 0) : 0;
        const balanc = produccio - consum_w;

        // LECTURA DE LA BATERIA AMB ELS NOUS ATRIBUTS EN KWH
        const bateria = await getEntity("Bateria:Veinat:001");
        let prediccioBateria = null;
        if (bateria) {
            const capMax = getAttr(bateria, 'capacitat_maxima_kwh', 62.0);
            const capAct = getAttr(bateria, 'capacitat_actual_kwh', 31.0);
            // Calculem el % en temps real per alimentar el panell visual de la web
            batteryLevel = (capAct / capMax) * 100.0;
            // La predicció ja ve calculada per n8n; ací només es mostra
            prediccioBateria = getAttr(bateria, 'prediccio_bateria', null);
        } else {
            batteryLevel = 0.0;
        }

        // 2. LECTURA DE SIBER
        const siber = await getEntity("Siber:Veinat:001");
        if (siber) {
            const siberActiu = getAttr(siber, 'actiu', false);
            const siberMode = getAttr(siber, 'mode', 'auto');
            const siberTemp = getAttr(siber, 'temp_siber_c', 22.0);
            const siberCo2 = getAttr(siber, 'co2_ppm', 400);

            document.getElementById('siber-img').src = siberActiu ? 'public/siber_on.png' : 'public/siber_off.png';
            document.getElementById('ac-mode-text').textContent = siberMode;
            document.getElementById('target-ac').innerText = siberTemp.toFixed(1);

            const estatEl = document.getElementById('ac-estat');
            estatEl.textContent = siberActiu ? 'Actiu' : 'Apagat';
            estatEl.className = 'mono text-xs ' + (siberActiu ? 'text-emerald-400' : 'text-slate-600');
            // L'alerta de CO2 la publica ara n8n com a entitat Event (veure checkEventLog)
        }

        // 3. LECTURA DE DIPÒSIT D'AIGUA
        const agua = await getEntity("Deposit:Veinat:001");
        if (agua) {
            const agua_volum = getAttr(agua, 'nivell_litres', 0);
            const agua_maxim = getAttr(agua, 'volum_max_litres', 1);
            const agua_nivell = agua_maxim > 0 ? (agua_volum / agua_maxim) * 100 : 0;
            const bomba_activa = getAttr(agua, 'bomba_activa', false);

            document.getElementById('water-now').textContent = agua_nivell.toFixed(1);
            document.getElementById('water-vol').textContent = Math.round(agua_volum) + ' L';
            
            push(waterLevelChart, parseFloat(agua_nivell.toFixed(1)));
            waterLevelChart.update('none');
            
            document.getElementById('pump-img').src = bomba_activa ? 'public/bomba_activa.png' : 'public/bomba_inactiva.png';

            const estEl = document.getElementById('water-estat');
            estEl.textContent = bomba_activa ? 'Operatiu' : 'Aturat';
            estEl.className = 'mono text-xs ' + (bomba_activa ? 'text-emerald-400' : 'text-amber-500');
        }

        // 4. LECTURA D'ESTANCES
        let temp_mig = 0, hum_mig = 0;
        const roomsContainer = document.getElementById('rooms-container');
        const [respSensors, respLlums] = await Promise.all([
            fetch(`${ORION_URL}/v2/entities?type=SensorAmbient`),
            fetch(`${ORION_URL}/v2/entities?type=Llum`)
        ]);
        
        if (respSensors.ok && respLlums.ok) {
            const estances = await respSensors.json();
            const llums = await respLlums.json();
            const llumsPerEstanca = new Map(
                llums.map(llum => [getAttr(llum, 'estanca', ''), llum])
            );
            if (estances && estances.length > 0) {
                let htmlEstances = "";
                estances.forEach(estanca => {
                    const nom = getAttr(estanca, 'estanca', estanca.id.split(':').pop());
                    const t = getAttr(estanca, 'temperatura_c', 20);
                    const h = getAttr(estanca, 'humitat_pct', getAttr(estanca, 'humitat_', 50));
                    const llumEncesa = getAttr(llumsPerEstanca.get(nom), 'encesa', false);
                    const ocupacio = getAttr(estanca, 'ocupacio', false);

                    temp_mig += t; hum_mig += h;

                    htmlEstances += `
                        <div class="card">
                            <div class="room-header">
                                <span class="font-semibold text-sm">${nom}</span>
                                <div class="mono text-sm">
                                    <span class="text-red-400">${t.toFixed(1)}</span>°
                                    <span class="text-slate-500 mx-1">|</span>
                                    <span class="text-cyan-400">${Math.round(h)}</span>%
                                </div>
                            </div>
                            <div class="p-4">
                                <div class="flex justify-between items-center mb-3">
                                    <span class="text-sm text-slate-400">
                                        <i class="fas fa-lightbulb mr-2 text-yellow-600"></i>Il·luminació
                                    </span>
                                    <img src="public/${llumEncesa ? 'iluminacion_on' : 'iluminacion_off'}.png" class="h-8 w-8 rounded-lg object-contain">
                                </div>
                                <div class="flex justify-between items-center mb-3">
                                    <span class="text-sm text-slate-400">
                                        <i class="fas fa-person-shelter mr-2 text-violet-600"></i>Ocupació
                                    </span>
                                    <span class="mono text-xs ${ocupacio ? 'text-emerald-400' : 'text-slate-600'}">${ocupacio ? 'Ocupat' : 'Buit'}</span>
                                </div>
                            </div>
                        </div>`;
                });
                roomsContainer.innerHTML = htmlEstances;
                temp_mig /= estances.length; hum_mig /= estances.length;
            }
        }

        // --- ACTUALITZACIÓ GRÀFIQUES I VALORS GLOBALS ---
        push(batChart, parseFloat(batteryLevel.toFixed(1)));     batChart.update('none');
        push(tempChart, parseFloat(temp_mig.toFixed(1)));        tempChart.update('none');
        push(humChart, parseFloat(hum_mig.toFixed(1)));          humChart.update('none');
        push(histChart, consum_w, 0); 
        push(histChart, produccio, 1);                           
        histChart.update('none');

        document.getElementById('battery-now').textContent = batteryLevel.toFixed(1) + ' %';
        document.getElementById('temp-val').textContent    = temp_mig.toFixed(1) + ' °C';
        document.getElementById('hum-val').textContent     = hum_mig.toFixed(1) + ' %';
        document.getElementById('prod-val').textContent    = (produccio / 1000).toFixed(2) + ' kW';
        document.getElementById('cons-val').textContent    = (consum_w / 1000).toFixed(2) + ' kW';

        const carregant = balanc > 0;
        const estatEl = document.getElementById('bat-estat');
        estatEl.textContent = carregant ? '↑ Carregant' : '↓ Descarregant';
        estatEl.className   = 'mono text-sm ' + (carregant ? 'text-emerald-400' : 'text-red-400');
        document.getElementById('bat-autonomia').textContent =
            prediccioBateria === null ? '-' : prediccioBateria.toFixed(1) + ' h';

        const bal_kw  = (balanc / 1000).toFixed(2);
        const balCls  = 'mono text-sm ' + (balanc > 0 ? 'text-emerald-400' : 'text-red-400');
        document.getElementById('bat-balanc').textContent  = (balanc > 0 ? '+' : '') + bal_kw + ' kW';
        document.getElementById('bat-balanc').className    = balCls;
        document.getElementById('balanc-val').textContent  = (balanc > 0 ? '+' : '') + bal_kw + ' kW';
        document.getElementById('balanc-val').className    = balCls;

    } catch (e) { console.error('Error llegint dades:', e); }
}

// Registre d'events. nivell: info (local/estat) | auto | alerta | ok
function addLog(msg, nivell = 'info', hora = null) {
    const log = document.getElementById('event-log');
    const d = document.createElement('div');
    const estils = {
        info:   'text-slate-600 border-slate-800',
        auto:   'text-amber-300 border-amber-500 bg-amber-500/5 rounded-r',
        alerta: 'text-red-300 border-red-500 bg-red-500/5 rounded-r',
        ok:     'text-emerald-300 border-emerald-500 bg-emerald-500/5 rounded-r',
    };
    const icones = { info: '', auto: '⚡ ', alerta: '⚠ ', ok: '✓ ' };
    d.className = `border-l pl-2 leading-relaxed ${estils[nivell] || estils.info}`;
    const t = hora || new Date().toLocaleTimeString();
    d.innerHTML = `<span class="text-blue-900">[${t}]</span> ${icones[nivell] || ''}${msg}`;
    log.prepend(d);
    if (log.children.length > 40) log.removeChild(log.lastChild);
}

// Llegeix les entitats Event d'Orion (que publiquen les automatitzacions
// de n8n) i pinta al registre nomes les que son noves.
async function checkEventLog() {
    try {
        const resp = await fetch(`${ORION_URL}/v2/entities?type=Event&options=keyValues&limit=1000`);
        if (!resp.ok) return;
        const events = await resp.json();
        if (!Array.isArray(events) || events.length === 0) return;

        events.sort((a, b) => (a.ts || 0) - (b.ts || 0));

        if (!eventsInit) {
            // Primera lectura: fixem la base per no repetir l'historial antic
            lastEventTs = events[events.length - 1].ts || 0;
            eventsInit = true;
            return;
        }

        for (const e of events) {
            if ((e.ts || 0) > lastEventTs) {
                addLog(e.missatge, e.nivell || 'info', e.hora);
                lastEventTs = e.ts;
            }
        }
    } catch (e) { /* Orion no disponible */ }
}

document.addEventListener('DOMContentLoaded', async () => {
    initCharts();
    addLog('Iniciant mode lectura...');
    
    if (await checkOrionConnection()) {
        addLog('ORION connectat. Llegint dades.');
        orionConnected = true;
    } else {
        addLog('No s\'ha pogut connectar a ORION');
    }
    
    setInterval(() => { document.getElementById('live-clock').innerText = new Date().toLocaleTimeString(); }, 1000);

    async function bucleLectura() {
        await updateSensors();
        await checkEventLog();
        setTimeout(bucleLectura, 3000);
    }
    bucleLectura();
});