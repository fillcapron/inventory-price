from .api_core import Inventory

class Telebot(Inventory):

    def __init__(self, data):
        super().__init__(data)

    def get(self):
        try:
            items=[]
            inv=self.get_inventory()
            for item in inv:
                item_name=item.get('name')
                item_count=str(item.get('count'))
                items.append(
                    f'Предмет -{item_name} x{item_count}'
                )
            return items
        except Exception as ex:
            return None