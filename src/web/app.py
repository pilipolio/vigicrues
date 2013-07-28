from flask import Flask, jsonify, render_template, request, make_response

from datetime import datetime, timedelta 
import time
import json
import scraping

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stationFlowGraph/<int:station_id>')
def get_station_flow_graph(station_id):
    return render_template('station_flow_graph.html', station_id=station_id)

@app.route('/stationFlows/<int:station_id>')
def get_station_flows(station_id):
    time_y_tuples = scraping.get_flows(station_id)
    data = [dict(x=(time.mktime(t.timetuple())), y=flow) for t, flow in time_y_tuples]
    # As advertised here, cannot use jsonify to return array
    # https://github.com/mitsuhiko/flask/issues/510
    #return jsonify([{'name': str(station_id), 'data': data}])
    return make_response(json.dumps([{'name': str(station_id), 'data': data}]))

@app.route('/stations')
def get_stations():
    scraper = scraping.Scraper('../data/')  
    return jsonify(ids=[s['id'] for s in scraper.load_stations()])

@app.route('/station/<int:station_id>')
def get_station(station_id):
    scraper = scraping.Scraper('../data/')
    return jsonify([station for station in scraper.load_stations() if station['id'] == station_id][0])

if __name__ == '__main__':
    app.run(debug=True)
