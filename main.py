from tours import getTours
from products import getProducts, getProductsNext
from poi import getPOI, getPOINext
from flask_cors import CORS
from flask import Flask
app = Flask(__name__)


@app.route('/')
def index():
    return "Ready"

app.add_url_rule('/api/tours', 'tours', getTours)
app.add_url_rule('/api/products', 'products', getProducts)
app.add_url_rule('/api/products_next', 'products_next', getProductsNext)
app.add_url_rule('/api/poi', 'poi', getPOI)
app.add_url_rule('/api/poi_next', 'poi_next', getPOINext)

CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

def main():
    app.run(debug=True,port=5002 , use_reloader=False)