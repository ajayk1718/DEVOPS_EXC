from flask import Flask
import requests

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

app = Flask(__name__)

resource = Resource.create({
    "service.name": "checkout-service"
})

provider = TracerProvider(resource=resource)

processor = BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint="http://tempo.monitoring.svc.cluster.local:4318/v1/traces"
    )
)

provider.add_span_processor(processor)

trace.set_tracer_provider(provider)

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/")
def checkout():

    print("Checkout Service Called")

    response = requests.get(
        "http://inventory-service:5000/"
    )

    return "Checkout -> " + response.text

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
