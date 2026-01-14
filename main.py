from tours import getTours
from products import getProducts
from flask_cors import CORS
from flask import Flask
app = Flask(__name__)


@app.route('/')
def index():
    return "Ready"

app.add_url_rule('/api/tours', 'tours', getTours)
app.add_url_rule('/api/products', 'products', getProducts)

CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

def main():
    app.run(debug=True,port=5002 , use_reloader=False)