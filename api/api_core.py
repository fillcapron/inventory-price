import requests


class Inventory:
    MARKET_API = 'http://steamcommunity.com/market/priceoverview/?appid=730&currency=5&market_hash_name='
    PROFILE_INVENTORY_API = 'profiles'

    def __init__(self, req):
        self.data = self.fetch(req)
        self.rg_inventory = self.data['rgInventory']
        self.rg_descriptions = self.data['rgDescriptions']

    def fetch(self, req):
        try:
            response = requests.get(f'http://steamcommunity.com/profiles/{req}/inventory/json/730/2/')
            if response.status_code == 200:
                return response.json()
            else:
                return {'rgInventory': None, 'rgDescriptions': None, 'error': 500}
        except ValueError as ex:
            return {'rgInventory': None, 'rgDescriptions': None, 'error': ex}

    def get_inventory(self):
        try:
            items = []
            for elem in self.rg_descriptions.values():
                count = self.inv_count(elem.get('classid'))
                items.append(
                    {
                        "classid": elem.get('classid'),
                        "instanceid": elem.get('instanceid'),
                        "market_name": elem.get('market_name'),
                        "name": elem.get('name'),
                        "market_hash_name": elem.get('market_hash_name'),
                        "type": elem.get('type'),
                        "description": [],
                        "icon_url": elem.get('icon_url'),
                        "count": count
                    }
                )
            return items
        except:
            return self.data

    def inv_count(self, data):
        item = self.get_classid()
        return item.count(data)

    def get_classid(self):
        classid_list = []
        for id in self.rg_inventory.values():
            if id.get('classid'):
                clsid = id.get('classid')
                classid_list.append(clsid)
        return classid_list


def get_price(item_name, conversion):
    try:
        response = requests.get(f'https://csgo.backpack.tf/market_search?text={item_name}&conversion={conversion}')
        data = response.json()
        first_item_list = data.get('items')[0]
        item_name_data = first_item_list.get('itemName')
        buy_price = first_item_list.get('buyPrice')
        sell_price = first_item_list.get('sellPrice')
        return { "itemName": item_name_data, "buyPrice": buy_price, "sellPrice": sell_price}
    except ValueError as e:
        return {'error': e}
