from flask import Flask
from flask import jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Scrapped Vigicrues data rest API'

@app.route('/stations')
def get_stations():
    return jsonify(station_ids=[1,2])

@app.route('/station/<int:station_id>')
def get_station(station_id):
    return jsonify(id=station_id,
                   name='Garigliano')

if __name__ == '__main__':
    app.run(debug=True)
