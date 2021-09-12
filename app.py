from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from api.api_core import Inventory, get_price


app = Flask(__name__)
CORS(app)

@app.route('/api', methods=["POST"])
def api():
    if request.method == 'POST':
        try:
            res=json.loads(request.data)
            data=Inventory(res['id'], res['app'])
            inv=data.get_inventory()
            return jsonify(inv)
        except ValueError:
            return jsonify({'error': 'Введен неправильный steam ID'})

@app.route('/price', methods=["GET"])
def market():
    item_name = request.args.get('name', default='None', type=str)
    currency = request.args.get('conversion', default=3, type=int)
    data = get_price(item_name, currency)
    return jsonify(data)

if __name__ == '__main__':
    app.run()