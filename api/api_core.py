import requests
import urllib.parse
import time

app_context = {
    '753': '6',
    '440': '2',
    '730': '2',
    '570': '2',
    '583950': '2',
    '433850': '2',
    '252490': '2',
    '304930': '2',
    '218620': '2',
    '238460': '2',
    '321360': '2',
    '232090': '2',
    '322330': '2',
    '578080': '2'
}

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}

bd_price = {
    '440': 'https://tf2.tm/api/v2/prices/RUB.json',
    '730': 'https://market.csgo.com/api/v2/prices/RUB.json',
    '570': 'https://market.dota2.net/api/v2/prices/RUB.json',
    '252490': 'https://rust.tm/api/v2/prices/RUB.json'
}

web = 'C14D927D1E903A90CECFD838E8160785'

#more_items
#last_assetid

class Inventory:

    def __init__(self, steam_id, app='753'):
        """
        Конструктор при создании экземпляра класса Inventory
        :param steam_id: Стим айди профиля или ссылка на профиль
        :param app: ID приложения (например CSGO - 730)
        """
        self.steam_id = check_id(steam_id)
        self.app = app
        self.data = self.fetch(self.steam_id, self.app)
        self.error = self.data.get('error', False)
        if not self.error:
            self.total_inventory_count = int(self.data.get('total_inventory_count'))
            self.assets = self.data.get('assets')
            self.descriptions = self.data.get('descriptions')
            self.price_db = requests.get(bd_price.get(self.app)).json() if bd_price.get(self.app) else None
        self.total_inventory_marketable = 0
        self.total_price = 0

    def fetch(self, steam_id, app, lang='russian'):
        """
        Запрос Steam API для получения инвентаря
        :param steam_id: Стим айди профиля или ссылка на профиль
        :param app: ID приложения (например CSGO - 730)
        :param lang: Язык на котором будет получен ответ (по умолчанию "русский")
        :return: Словарь ответа или ошибка
        """
        context_id = app_context.get(app)
        try:
            response = requests.get(f'http://steamcommunity.com/inventory/{steam_id}/{app}/{context_id}/?l={lang}&count=5000',
                                    headers=headers)
            if not response.ok:
                time.sleep(5) #Временное решение, Steam API иногда
                response = requests.get(f'http://steamcommunity.com/inventory/{steam_id}/{app}/{context_id}/?l={lang}&count=5000',
                                        headers=headers)
                if response.status_code == 403:
                    return {'error': 'Ошибка: Стим профиль или инвентарь запривачен', 'items': None}
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': 'Неправильный Steam ID', 'items': None}
        except:
            raise

    def get_inventory(self):
        """
        Метод полчения предметов, его перебора и извлечения основных свойств предов инвентаря
        :return: Список объектов с предметами и их характеристиками
        """
        if self.error:
            return self.data
        if self.total_inventory_count:
            items = []
            for elem in self.descriptions:
                count = self.inv_count(elem.get('classid'))
                if elem.get('commodity'):
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
                            "rarity": [el for el in elem.get('tags') or [] if el.get('category') == 'Rarity' or
                                       el.get('category') == 'droprate'],
                            "type": [el for el in elem.get('tags') or [] if el.get('category') == 'Type' or
                                     el.get('category') == 'item_class'] or elem.get('type'),
                            "quality": [el for el in elem.get('tags') or [] if el.get('category') == 'Quality' or
                                        el.get('category') == 'Game'],
                            "descriptions": elem.get('descriptions'),
                            "meta": [
                                el for el in elem.get('tags') or [] if
                                             el.get('category') == 'Exterior' or el.get('category') == 'Hero' or el.get(
                                                 'category') == 'Class'
                            ],
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
        """
        Метод для подсчета кол-ва конкретного предмета
        :param data: "classid" конкретного предмета
        :return: Кол-во в инветаре
        """
        item = self.get_classid()
        return item.count(data)

    def get_classid(self):
        """
        Метод получения "classid" из полученного ответа Steam API
        :return: Список со значениями "classid"
        """
        classid_list = []
        for id in self.assets:
            if id.get('classid'):
                clsid = id.get('classid')
                classid_list.append(clsid)
        return classid_list

    def generate_bg(self):
        """
        Метод генерирации фона по конкретному приложению
        :return: Ссылка
        """
        id = self.app if self.app != '753' else '945360'
        bg = f'http://cdn.akamai.steamstatic.com/steam/apps/{id}/page_bg_generated_v6b.jpg?t=1633375869'
        return bg

    def get_price_api(self, item_name):
        """
        Метод получение цены по конкретному предмету
        :param item_name: Название предмета
        :return: Цена или 0
        """
        if self.price_db:
            items = self.price_db.get('items')
            for item in items:
                if item.get('market_hash_name') == item_name:
                    return float(item.get('price'))
        return 0


def get_price(item_name, app_id, currency=5):
    """
    Функция получения цены из Торговой площадки Steam
    :param item_name: Название предмета
    :param app_id: ID приложения
    :param currency: Валюта
    :return: Цена или ошибка
    """
    item_name = urllib.parse.quote(item_name)
    try:
        response = requests.get(
            f'https://steamcommunity.com/market/priceoverview/?currency={currency}&country=us&appid={app_id}&market_hash_name={item_name}')
        data = response.json()
        if data.get('lowest_price'):
            return data
        else:
            return {'error': 'Превышен лимит запросов'}
    except ValueError as e:
        return {'error': e}


def get_profile(steamid):
    """
    Метод получения основной информации профиля
    :param steamid: Стим айди профиля или ссылка на профиль
    :return: Словарь с данными профиля
    """
    try:
        steamid = check_id(steamid)
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
            return {'error': 'Непрвильный Steam ID'}
    except ValueError:
        return {'error': 'Непрвильный запрос'}


def check_id(steam_id):
    """
    Метод работы со Steam ID
    :param steam_id: id или url
    :return: Релевантный Steam ID
    """
    if steam_id.isdigit():
        return steam_id
    list_str = steam_id.split('/')

    if len(list_str) == 1:
        profile_id = received_id(steam_id)
        return profile_id

    for elem in list_str:
        if elem.isdigit():
            return elem

        if elem == 'id':
            index = list_str.index(elem)
            profile_id = received_id(list_str[index + 1])
            return profile_id

    return steam_id


def received_id(vanityurl):
    """
    Метод получения Steam ID по Steam домену
    :param vanityurl: url
    :return: Steam ID
    """
    received_res = requests.get(
        f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={web}&vanityurl={vanityurl}').json()
    return received_res.get('response').get('steamid')
