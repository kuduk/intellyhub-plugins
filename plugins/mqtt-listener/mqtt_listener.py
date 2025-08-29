import logging
import json
import paho.mqtt.client as mqtt
from yaml import safe_load
import time
from flow.flow import FlowDiagram
from .base_listener import BaseListener

logger = logging.getLogger(__name__)

class MQTTListener(BaseListener):
    def __init__(self, event_config, global_context=None):
        super().__init__(event_config)
        # Initialize global context
        self.global_context = global_context or {}

        # Format and initialize connection parameters
        raw_broker = event_config.get("broker", "localhost")
        self.broker = self.format_recursive(raw_broker, self.global_context)

        raw_port = event_config.get("port", 1883)
        formatted_port = self.format_recursive(str(raw_port), self.global_context)
        self.port = int(formatted_port)

        raw_topic = event_config.get("topic", "#")
        self.topic = self.format_recursive(raw_topic, self.global_context)

        raw_client_id = event_config.get("client_id", "mqtt_listener")
        self.client_id = self.format_recursive(raw_client_id, self.global_context)

        # Create MQTT client
        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Placeholder for config file path
        self.config_file = None

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Connected to MQTT broker {self.broker} (rc={rc})")
            client.subscribe(self.topic)
            logger.info(f"Subscribed to topic {self.topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker, rc={rc}")

    def on_message(self, client, userdata, msg):
        logger.info(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
        try:
            # Parse payload
            message_data = json.loads(msg.payload.decode())

            # Load YAML configuration
            with open(self.config_file, 'r') as file:
                config = safe_load(file)

            # Initialize and run flow
            flow = FlowDiagram(config, self.global_context)
            # Inject MQTT context
            flow.variables.update({
                'topic': msg.topic,
                'data': message_data
            })
            # Merge any keys from payload into variables
            flow.variables.update(message_data)

            flow.run()
        except json.JSONDecodeError as e:
            logger.error(f"MQTT payload JSON decode error: {e}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def listen(self, config_file):
        # Store config file for use in on_message
        self.config_file = config_file

        # Retry loop for connecting to broker
        while True:
            try:
                self.client.connect(self.broker, self.port, keepalive=60)
                break
            except Exception as e:
                logger.error(f"MQTT connection error: {e}")
                logger.info("Retrying connection in 5 seconds...")
                time.sleep(5)

        # Start MQTT network loop
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            logger.info("MQTT listener interrupted by user")
            self.client.disconnect()
        except Exception as e:
            logger.error(f"Error in MQTT loop: {e}")
            self.client.disconnect()
