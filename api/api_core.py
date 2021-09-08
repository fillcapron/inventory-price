import requests


class Inventory:
    MARKET_API = 'http://steamcommunity.com/market/priceoverview/?appid=730&currency=5&market_hash_name='
    PROFILE_INVENTORY_API = 'profiles'

    def __init__(self, id, app):
        self.data = self.fetch(id, app)
        self.total_inventory_count = int(self.data['total_inventory_count'])
        self.assets = self.data['assets']
        self.descriptions = self.data['descriptions']

    def fetch(self, id, app):
        context_id = '2' if app != '753' else '6'
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
                    items.append(
                        {
                            "classid": elem.get('classid'),
                            "instanceid": elem.get('instanceid'),
                            "market_name": elem.get('market_name'),
                            "name": elem.get('name'),
                            "market_hash_name": elem.get('market_hash_name'),
                            "type": elem.get('tags'),
                            # "description": elem.get('descriptions'),
                            "icon_url": elem.get('icon_url'),
                            "count": count,
                            # "price": get_price(elem.get('name'), 440)
                        }
                    )
            return items
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
            return { "buyPrice": buy_price, "sellPrice": sell_price}
        else:
            return {'error': 'Price is None'}
    except ValueError as e:
        return {'error': e}
