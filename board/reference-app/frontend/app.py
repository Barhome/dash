from flask import Flask, render_template, request
from prometheus_flask_exporter import PrometheusMetrics
app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.3')


@app.route('/')
def homepage():
    return render_template("main.html")

metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    ),
    metrics.histogram(
        'requests_by_status_and_path', 'Request latencies by status and path',
         labels={'status': lambda r: r.status_code, 'path': lambda: request.path}
         ),
    metrics.counter('invocation_by_type', 'Number of invocations by type',
         labels={'item_type': lambda: request.view_args['type']})
)

if __name__ == "__main__":
    app.run()