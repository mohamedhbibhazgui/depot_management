from flask import Flask
from routes import employee_bp

app = Flask(__name__)

# Register the Blueprint
app.register_blueprint(employee_bp)

if __name__ == '__main__':
    app.run(debug=True)