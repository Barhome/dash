from flask import Flask, render_template, request, jsonify
import pymongo
from flask_pymongo import PyMongo


from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import SERVICE_NAME , Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics

trace.set_tracer_provider(
TracerProvider(
    resource=Resource.create({SERVICE_NAME: 'hello-service'})))

jaeger_exporter = JaegerExporter()

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

tracer = trace.get_tracer(__name__)


app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
metrics = GunicornInternalPrometheusMetrics(app)

metrics.info('app_info','Application info', version='1.0.3')


app.config['MONGO_DBNAME'] = 'example-mongodb'
app.config['MONGO_URI'] = 'mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb'

mongo = PyMongo(app)


@app.route('/')
def homepage():
    with tracer.start_as_current_span('hello-world'):
        hello_world = 'Hello World'
    return hello_world


@app.route('/api')
def my_api():
    with tracer.start_as_current_span('my_api'):
        answer = "something"

    return jsonify(repsonse=answer)

@app.route('/star', methods=['POST'])
def add_star():
  star = mongo.db.stars
  name = request.json['name']
  distance = request.json['distance']
  star_id = star.insert({'name': name, 'distance': distance})
  new_star = star.find_one({'_id': star_id })
  output = {'name' : new_star['name'], 'distance' : new_star['distance']}
  return jsonify({'result' : output})

if __name__ == "__main__":
    app.run(debug=False)
