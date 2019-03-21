import json
import os

current_path = os.path.dirname(__file__)
path = '%s/login.json' % current_path.replace('util', 'data')


class OperaJson:
    def __init__(self, json_path=None):
        if json_path:
            self.json_path = json_path
        else:
            self.json_path = path
        self.res = self.read_json()

    def read_json(self):
        """读取json文件"""
        with open(self.json_path) as load_f:
            res = json.load(load_f)
            return res

    def get_value(self, key):
        """获取json文件的key值"""
        return self.res.get(key)
