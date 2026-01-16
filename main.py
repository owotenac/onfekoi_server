from tours import getTours
from products import getProducts
from poi import getPOI
from events import getEvents
from details import getDetails
from flask_cors import CORS
from flask import Flask
from api_call import getNextPage

app = Flask(__name__)


@app.route('/')
def index():
    return "Ready"

app.add_url_rule('/api/tours', 'tours', getTours)
app.add_url_rule('/api/products', 'products', getProducts)
app.add_url_rule('/api/poi', 'poi', getPOI)
app.add_url_rule('/api/events', 'events', getEvents)
app.add_url_rule('/api/tours', 'tours', getTours)
app.add_url_rule('/api/next_page', 'next_page', getNextPage)
app.add_url_rule('/api/details', 'details', getDetails)

CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

def main():
    app.run(debug=True,port=5002 , use_reloader=False)