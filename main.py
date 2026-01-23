from details import getDetails
from catalog import getItems, searchItems
from flask_cors import CORS
from flask import Flask
from api_call import getNextPage

app = Flask(__name__)


@app.route('/')
def index():
    return "Ready"

app.add_url_rule('/api/catalog', 'catalog', getItems)

app.add_url_rule('/api/next_page', 'next_page', getNextPage)
app.add_url_rule('/api/details', 'details', getDetails)
app.add_url_rule('/api/search', 'search', searchItems)

CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

def main():
    app.run(debug=True,port=5002 , use_reloader=False)

if __name__ == "__main__":
    main()