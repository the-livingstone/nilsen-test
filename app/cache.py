from datetime import datetime
from collections import OrderedDict

from app.schemas import Intake

class Cache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.items = OrderedDict()

    def _check_time(self):
        for key in list(self.items.keys()):
            if self.items[key].get('ttl') is not None:
                if self.items[key]['updated'] + self.items[key]['ttl'] < datetime.now().timestamp():
                    self.items.pop(key)

    async def get_item(self, key: str):
        self._check_time()
        self.items[key] = self.items.pop(key)
        self.items[key]['updated'] = datetime.now().timestamp()
        return self.items[key]['value']

    async def put_item(self, key: str, intake: Intake):
        self._check_time()
        exist = True
        payload = intake.model_dump()
        try:
            self.items.pop(key)
        except KeyError:
            exist = False
        payload['updated'] = datetime.now().timestamp()
        self.items[key] = payload
        if len(self.items) > self.capacity:
            self.items.popitem(last=False)

        return exist

    async def delete_item(self, key: str):
        self._check_time()
        self.items.pop(key)

    async def stats(self):
        self._check_time()
        return {
            "size": len(self.items),
            "capacity": self.capacity,
            "items": [x for x in reversed(self.items)]
        }