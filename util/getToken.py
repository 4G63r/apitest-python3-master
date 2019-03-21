import collections
import requests
import hashlib
import time
import json


class TestEnvir:
    TEST = 0  # 测试线
    ONLINE = 1  # 线上


class GetToken:
    """
    仿真：u:'大热天的' p:'jzb111111'
    线上：u:'JZB150' p:'g9a6y5e4'
    """

    def __init__(self, uname=None, passwd=None, test_envir=1):
        self.uname = uname
        self.passwd = passwd
        self.test_envir = test_envir

    @property
    def sign(self):
        if self.test_envir == 0:
            self.uname = '大热天的'
            self.passwd = 'jzb111111'
        elif self.test_envir == 1:
            self.uname = 'JZB150'
            self.passwd = 'g9a6y5e4'
        else:
            pass

        app_secret = '5b7cc94c284f4dad745e343d7d66faee'  # 秘钥(不能泄露)
        param = collections.OrderedDict()
        param['passwd'] = self.passwd
        param['uname'] = self.uname
        param['version'] = '7.3'
        str_param = json.dumps(param, ensure_ascii=False)  # 防止中文乱码
        day = time.strftime('%Y%m%d')
        sign = app_secret + day + str_param
        sign = sign.replace(" ", "")
        m = hashlib.md5()
        m.update(sign.encode('utf-8'))
        sign = m.hexdigest()
        param['sign'] = sign
        return param

    @property
    def api_key(self):
        param = self.sign
        if self.test_envir == 0:
            res = requests.post("http://m-dev.jzb.com/user/login/v2016", data=param)
        elif self.test_envir == 1:
            res = requests.post("http://m.jzb.com/user/login/v2016", data=param)
        else:
            res = None
        try:
            return json.loads(res.text)['res']['api_key']
        except AttributeError:
            print('测试环境选择错误！环境选择举例：test_envir=TestEnvir.TEST')

    @property
    def vrf_params(self):
        res = requests.get('http://aitools.dev.jzb.com/getVrfToken')
        pinus = res.json()['objects']['pinus']
        x_identity_code = res.json()['objects']['X-Identity-Code']
        return {'pinus': pinus, 'X-Identity-Code': x_identity_code}
