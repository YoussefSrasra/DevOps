import random, logging, time
from flask import Flask, render_template, request, redirect
from prometheus_flask_exporter import PrometheusMetrics
from pythonjsonlogger import jsonlogger
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__, static_url_path="/static/", static_folder="./static/", template_folder="./templates/")

# 1. METRICS: Satisfies "expose simple metrics" 
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'URL Shortener Info', version='1.0.0')

# 2. LOGGING: Satisfies "structured logs" [cite: 13, 42]
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s %(trace_id)s')
logHandler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# 3. TRACING: Satisfies "basic request tracing" [cite: 14, 42]
FlaskInstrumentor().instrument_app(app)

saved_links = {}

def generate_link_id(length=8):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    # Logic fix: ensured initial link_id is not already in keys to enter/stay in loop
    link_id = "".join([random.choice(alphabet) for _ in range(length)])
    while link_id in saved_links:
        link_id = "".join([random.choice(alphabet) for _ in range(length)])
    return link_id

@app.route('/<string:link_id>')
def dereference_link(link_id):
    trace_id = format(trace.get_current_span().get_span_context().trace_id, '032x')
    if link_id in saved_links:
        logger.info(f"Redirecting {link_id}", extra={'trace_id': trace_id})
        return redirect(saved_links[link_id], code=302)
    logger.warning(f"Link ID {link_id} not found", extra={'trace_id': trace_id})
    return redirect("/")

@app.route('/', methods=["GET", "POST"])
def generate_link():
    trace_id = format(trace.get_current_span().get_span_context().trace_id, '032x')
    url = request.args.get("url")
    if url:
        link_id = generate_link_id()
        saved_links[link_id] = url
        shorten_link = request.url_root + link_id
        logger.info(f"Created link: {link_id} for {url}", extra={'trace_id': trace_id})
        return render_template("index.html", shorten_link=shorten_link)
    return render_template("index.html", shorten_link=None)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)