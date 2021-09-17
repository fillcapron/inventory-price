import requests

app_context = {
     '753': '6',
     '440': '6',
     '730': '2',
     '570': '6',
     '583950': '2',
     '433850':'6',
     '252490': '2',
     '304930': '6',
     '218620': '2',
     '238460': '6',
     '321360':'2',
     '232090': '6',
     '322330': '2',
     '578080': '6'
}

class Inventory:
    MARKET_API = 'http://steamcommunity.com/market/priceoverview/?appid=730&currency=5&market_hash_name='

    def __init__(self, id, app=753):
        self.data = self.fetch(id, app)
        self.total_inventory_count = int(self.data['total_inventory_count'])
        if self.total_inventory_count:
            self.assets = self.data['assets']
            self.descriptions = self.data['descriptions']
        self.total_inventory_marketable = 0

    @classmethod
    def fetch(self, id, app):
        context_id = app_context[app]
        try:
            response = requests.get(f'http://steamcommunity.com/inventory/{id}/{app}/{context_id}/')
            if response.status_code == 200:
                return response.json()
            else:
                raise
        except:
            raise ValueError

    def get_inventory(self):
        if self.total_inventory_count:
            items = []
            for elem in self.descriptions:
                count = self.inv_count(elem.get('classid'))
                if elem.get('marketable'):
                    self.total_inventory_marketable += count
                    items.append(
                        {
                            "appid": elem.get('appid'),
                            "classid": elem.get('classid'),
                            "instanceid": elem.get('instanceid'),
                            "market_name": elem.get('market_name'),
                            "name": elem.get('name'),
                            "market_hash_name": elem.get('market_hash_name'),
                            "type": [el for el in elem.get('tags') if el.get('category') == 'Rarity' or 'item_class'][0],
                            "description": [],
                            "icon_url": elem.get('icon_url'),
                            "count": count
                        }
                    )
            data = {'total': self.total_inventory_marketable, 'items': items}
            return data
        else:
            return []

    def inv_count(self, data):
        item = self.get_classid()
        return item.count(data)

    def get_classid(self):
        classid_list = []
        for id in self.assets:
            if id.get('classid'):
                clsid = id.get('classid')
                classid_list.append(clsid)
        return classid_list


def get_price(item_name, conversion):
    try:
        response = requests.get(f'https://csgo.backpack.tf/market_search?text={item_name}&conversion={conversion}')
        data = response.json()
        if data.get('items'):
            first_item_list = data.get('items')[0]
            buy_price = first_item_list.get('buyPrice')
            sell_price = first_item_list.get('sellPrice')
            return {"buyPrice": buy_price, "sellPrice": sell_price}
        else:
            return {'error': 'Price is None'}
    except ValueError as e:
        return {'error': e}
