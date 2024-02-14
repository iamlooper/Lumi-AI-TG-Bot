import json


class Str:
    def __str__(self):
        return json.dumps(self.__dict__, indent=4, ensure_ascii=False, default=str)
