import requests

app_context = {
    '753': '6',
    '440': '6',
    '730': '2',
    '570': '2',
    '583950': '2',
    '433850': '6',
    '252490': '2',
    '304930': '6',
    '218620': '2',
    '238460': '6',
    '321360': '2',
    '232090': '6',
    '322330': '2',
    '578080': '6'
}

bd_price = {
    440: 'https://tf2.tm/api/v2/prices/RUB.json',
    730: 'https://market.csgo.com/api/v2/prices/RUB.json',
    570: 'https://market.dota2.net/api/v2/prices/RUB.json',
    252490: 'https://rust.tm/api/v2/prices/RUB.json'
}

web = 'C14D927D1E903A90CECFD838E8160785'


class Inventory:

    def __init__(self, steam_id, app=753):
        self.app = int(app)
        self.data = self.fetch(steam_id, app)
        if self.data.get('error'):
            self.error = True
        else:
            self.error = False
            self.total_inventory_count = int(self.data.get('total_inventory_count'))
            self.assets = self.data.get('assets')
            self.descriptions = self.data.get('descriptions')
            self.price_db = requests.get(bd_price.get(self.app)).json() if bd_price.get(self.app) else None
        self.total_inventory_marketable = 0
        self.total_price = 0

    def fetch(self, steam_id, app, lang='russian'):
        context_id = app_context[app]
        try:
            response = requests.get(f'http://steamcommunity.com/inventory/{steam_id}/{app}/{context_id}/?l={lang}')
            if response.status_code == 403:
                return {'error': 'Failed: Steam profile/inventory is set to private', 'items': None}
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': 'Incorrect Steam ID', 'items': None}
        except:
            raise

    def get_inventory(self):
        if self.error:
            return self.data
        if self.total_inventory_count:
            items = []
            for elem in self.descriptions:
                count = self.inv_count(elem.get('classid'))
                if elem.get('marketable'):
                    self.total_inventory_marketable += count
                    price_item = self.get_price_api(elem.get('market_hash_name'))
                    self.total_price += price_item * count
                    items.append(
                        {
                            "appid": elem.get('appid'),
                            "classid": elem.get('classid'),
                            "instanceid": elem.get('instanceid'),
                            "market_name": elem.get('market_name'),
                            "name": elem.get('name'),
                            "market_hash_name": elem.get('market_hash_name'),
                            "rarity": [el for el in elem.get('tags') if el.get('category') == 'Rarity' or
                                     el.get('category') == 'droprate'][0],
                            "type": [el for el in elem.get('tags') if el.get('category') == 'Type' or
                                     el.get('category') == 'item_class'][0],
                            "quality": [el for el in elem.get('tags') if el.get('category') == 'Quality' or
                                     el.get('category') == 'Game'][0],
                            "description": [],
                            "icon_url": elem.get('icon_url'),
                            "count": count,
                            "price": price_item
                        }
                    )
            data = {'total_items': self.total_inventory_marketable, 'total_price': int(self.total_price),
                    'items': items,
                    'app': self.app,
                    'bg': self.generate_bg()}
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

    def generate_bg(self):
        id = self.app if self.app != '753' else 945360
        bg = f'http://cdn.akamai.steamstatic.com/steam/apps/{id}/page_bg_generated_v6b.jpg?t=1633375869'
        return bg

    def get_price_api(self, item_name):
        if self.price_db:
            items = self.price_db.get('items')
            for item in items:
                if item.get('market_hash_name') == item_name:
                    return float(item.get('price'))
        return 0


def get_price(item_name, app_id, currency=5):
    try:
        response = requests.get(
            f'https://steamcommunity.com/market/priceoverview/?currency={currency}&country=us&appid={app_id}&market_hash_name={item_name}')
        data = response.json()
        if data.get('lowest_price'):
            return data
        else:
            return {'error': 'Request limit reached'}
    except ValueError as e:
        return {'error': e}


def get_profile(steamid):
    try:
        response = requests.get(
            f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={web}&steamids={steamid}')
        data = response.json()
        response = data.get('response')
        players = response.get('players')
        if len(players):
            return {
                'avatar': players[0].get('avatarmedium'),
                'name': players[0].get('personaname'),
                'status': players[0].get('personastate'),
                'profilevisiblity': players[0].get('communityvisibilitystate'),
                'profileurl': players[0].get('profileurl'),
                'steamid': players[0].get('steamid')
            }
        else:
            return {'error': 'Incorrect Steam ID'}
    except ValueError:
        return {'error': 'Bad request'}
