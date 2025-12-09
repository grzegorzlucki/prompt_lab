from flask import Flask
from flask_cors import CORS


from src.public_transport_api.controllers.departures_controller import departures_bp
from src.public_transport_api.controllers.trips_controller import trips_bp


app = Flask(__name__)

CORS(app)


app.register_blueprint(departures_bp)
app.register_blueprint(trips_bp)


@app.route("/")
def index():
    return "Welcome to the Public Transport API for Wrocław!"

if __name__ == "__main__":
    app.run(debug=True, port=5001)