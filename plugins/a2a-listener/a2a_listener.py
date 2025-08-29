from flask import Flask, request, jsonify
from yaml import safe_load
from .base_listener import BaseListener
from flow.flow import FlowDiagram

class A2AListener(BaseListener):
    def __init__(self, event_config, global_context=None):
        super().__init__(event_config)
        # Salva il contesto globale
        self.global_context = global_context or {}

        # Format host e port con le variabili nel contesto
        raw_host = event_config.get("host", "0.0.0.0")
        formatted_host = self.format_recursive(raw_host, self.global_context)
        self.host = formatted_host

        raw_port = event_config.get("port", 4000)
        # Se port è fornito come str con placeholder, format e poi cast
        formatted_port = self.format_recursive(str(raw_port), self.global_context)
        self.port = int(formatted_port)

    def listen(self, config_file):
        app = Flask(__name__)

        @app.route("/rpc", methods=["POST"])
        def rpc():
            payload = request.json
            try:
                # Carica config YAML
                with open(config_file, 'r') as f:
                    config = safe_load(f)

                # Avvia il flow con le variabili
                flow = FlowDiagram(config, self.global_context)
                flow.variables.update(payload.get('params', {}))
                flow.run()

                return jsonify({
                    "jsonrpc": "2.0",
                    "result": flow.variables,
                    "id": payload.get('id')
                })
            except Exception as e:
                return jsonify({
                    "jsonrpc": "2.0",
                    "error": {"message": str(e)},
                    "id": payload.get('id')
                }), 500

        app.run(host=self.host, port=self.port)
