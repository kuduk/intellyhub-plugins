# MQTT Listener Plugin

Plugin listener per ricevere messaggi MQTT. Si connette a broker MQTT e triggera workflow quando riceve messaggi su topic specifici.

## Caratteristiche

- ✅ Connessione a broker MQTT
- ✅ Supporto autenticazione username/password
- ✅ Subscribe a topic multipli
- ✅ Quality of Service configurabile
- ✅ Supporto messaggi retained
- ✅ Auto-reconnection

## Configurazione

### Parametri Obbligatori

- `host`: Host del broker MQTT
- `topic`: Topic MQTT da ascoltare

### Parametri Opzionali

- `port`: Porta broker (default: 1883)
- `username`: Username per autenticazione
- `password`: Password per autenticazione  
- `qos`: Quality of Service 0-2 (default: 0)

## Variabili Iniettate

- `mqtt_topic`: Topic del messaggio ricevuto
- `mqtt_payload`: Payload del messaggio MQTT
- `mqtt_qos`: Quality of Service del messaggio
- `mqtt_retain`: Flag retain del messaggio

## Esempio di Utilizzo

```yaml
listener:
  type: mqtt
  host: mqtt.broker.com
  port: 1883
  topic: sensors/temperature
  username: "{MQTT_USERNAME}"
  password: "{MQTT_PASSWORD}"
  qos: 1

states:
  - name: process_sensor_data
    type: command
    command: echo "Sensor data from $mqtt_topic: $mqtt_payload"
```

## Casi d'Uso Comuni

### Monitoraggio Sensori IoT
```yaml
listener:
  type: mqtt
  host: iot.eclipse.org
  topic: home/sensors/+
  qos: 1
```

### Home Assistant Integration
```yaml
listener:
  type: mqtt
  host: homeassistant.local
  topic: homeassistant/sensor/+/state
  username: "{HA_MQTT_USER}"
  password: "{HA_MQTT_PASSWORD}"
```

### Industrial IoT
```yaml
listener:
  type: mqtt
  host: industrial.mqtt.broker
  topic: factory/machines/+/status
  qos: 2
```

## Topic Patterns

- `sensors/temperature` - Topic specifico
- `sensors/+` - Wildcard single level
- `sensors/#` - Wildcard multi level
- `home/+/temperature` - Pattern con placeholder

## QoS Levels

- **QoS 0**: At most once (fire and forget)
- **QoS 1**: At least once (acknowledged delivery)
- **QoS 2**: Exactly once (assured delivery)

## Broker Supportati

- Eclipse Mosquitto
- HiveMQ
- AWS IoT Core
- Azure IoT Hub
- Google Cloud IoT Core
- EMQ X
- VerneMQ

## Sicurezza

- Usa credenziali sicure per broker pubblici
- Configura TLS/SSL per connessioni sicure
- Limita permessi topic per utenti
- Monitora traffico anomalo