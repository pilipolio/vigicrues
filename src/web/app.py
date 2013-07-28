from flask import Flask, jsonify, render_template, request

import scraping

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stationFlowGraph/<int:station_id>')
def get_station_flow_graph(station_id):
    return render_template('station_flow_graph.html')

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
