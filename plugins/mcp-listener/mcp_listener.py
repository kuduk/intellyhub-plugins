from flask import Flask, request, jsonify
from yaml import safe_load
from .base_listener import BaseListener
from flow.flow import FlowDiagram

class MCPListener(BaseListener):
    def __init__(self, event_config, global_context=None):
        super().__init__(event_config)
        # Inizializza il contesto globale
        self.global_context = global_context or {}

        # Format host
        raw_host = event_config.get("host", "0.0.0.0")
        self.host = self.format_recursive(raw_host, self.global_context)

        # Format port (lo tratti come stringa per sostituzioni e poi cast)
        raw_port = event_config.get("port", 5001)
        formatted_port = self.format_recursive(str(raw_port), self.global_context)
        self.port = int(formatted_port)

        # Format endpoint
        raw_endpoint = event_config.get("endpoint", "/context")
        self.endpoint = self.format_recursive(raw_endpoint, self.global_context)

    def listen(self, config_file):
        app = Flask(__name__)

        @app.route(self.endpoint, methods=["GET"])
        def context():
            resource_id = request.args.get("resource_id")
            try:
                # Carica la configurazione YAML
                with open(config_file, 'r') as f:
                    config = safe_load(f)

                # Esegui il flow
                flow = FlowDiagram(config, self.global_context)
                flow.variables["resource_id"] = resource_id
                flow.run()

                return jsonify(flow.variables)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        app.run(host=self.host, port=self.port)
