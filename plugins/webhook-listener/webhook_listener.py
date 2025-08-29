from flask import Flask, request, jsonify
from yaml import safe_load
from flow.flow import FlowDiagram
from .base_listener import BaseListener

class WebhookListener(BaseListener):
    def __init__(self, event_config, global_context=None):
        super().__init__(event_config, global_context)
        self.webhook_port = event_config.get("webhook_port", 5000)
        self.webhook_url = event_config.get("webhook_url", "/webhook")

    def listen(self, config_file):
        app = Flask(__name__)

        @app.route(self.webhook_url, methods=['POST'])
        def webhook():
            try:
                data = request.json
                with open(config_file, 'r') as file:
                    config = safe_load(file)
                flow = FlowDiagram(config, self.global_context)
                flow.variables.update(data)
                flow.run()
                return jsonify({"status": "success"}), 200
            except Exception as e:
                app.logger.error(f"Error processing webhook: {e}", exc_info=True)
                return jsonify({"status": "error", "message": str(e)}), 500

        app.run(port=self.webhook_port)
