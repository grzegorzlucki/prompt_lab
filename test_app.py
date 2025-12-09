from flask import Flask
from controllers.departures_controller import departures_bp

app = Flask(__name__)
app.register_blueprint(departures_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
