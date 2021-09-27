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
web = 'C14D927D1E903A90CECFD838E8160785'


class Inventory:

    def __init__(self, steam_id, app=753):
        self.data = self.fetch(steam_id, app)
        if self.data.get('error'):
            self.error = True
        else:
            self.error = False
            self.total_inventory_count = int(self.data.get('total_inventory_count'))
            self.assets = self.data.get('assets')
            self.descriptions = self.data.get('descriptions')
        self.total_inventory_marketable = 0

    @classmethod
    def fetch(cls, steam_id, app, lang='russian'):
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
                    items.append(
                        {
                            "appid": elem.get('appid'),
                            "classid": elem.get('classid'),
                            "instanceid": elem.get('instanceid'),
                            "market_name": elem.get('market_name'),
                            "name": elem.get('name'),
                            "market_hash_name": elem.get('market_hash_name'),
                            "type": [el for el in elem.get('tags') if el.get('category') == 'Rarity' or
                                     el.get('category') == 'droprate'][0],
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


def get_price(item_name, conversion = 440):
    try:
        response = requests.get(f'https://csgo.backpack.tf/market_search?text={item_name}&conversion={conversion}')
        data = response.json()
        print(response.json())
        if data.get('items'):
            first_item_list = data.get('items')[0]
            buy_price = first_item_list.get('buyPrice')
            sell_price = first_item_list.get('sellPrice')
            return {"buyPrice": buy_price, "sellPrice": sell_price}
        else:
            return {'error': 'Price is None'}
    except ValueError as e:
        return {'error': e}


def get_profile(steamid):
    try:
        response = requests.get(f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={web}i&steamids={steamid}')
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
        return {'error': 'Bar request'}