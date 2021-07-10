from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from api.api_core import Inventory, get_price

app = Flask(__name__)
CORS(app)

@app.route('/api', methods=["POST"])
def api():
    if request.method == 'POST':
        res=json.loads(request.data)
        data=Inventory(res['id'])
        inv=data.get_inventory()
        return jsonify(inv)
    else:
        return jsonify({'error': 'Do not get requests'})

@app.route('/market_search', methods=["GET"])
def market():
    item_name = request.args.get('text', default='None', type=str)
    conversion = request.args.get('conversion', default=440, type=int)
    data = get_price(item_name, conversion)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)