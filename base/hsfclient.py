import requests
import unittest
import urllib3
import json
import jsonpath

urllib3.disable_warnings()


class BodyType:
    URL_ENCODE = 1
    FORM = 2
    XML = 3
    JSON = 4
    FILE = 5


class HSFClient(unittest.TestCase):
    connect = None

    def __init__(self, url, method="GET", body_type=0, params=None):
        super(HSFClient, self).__init__()
        self.url = url
        self.method = method
        self.headers = {}
        self.body_type = body_type
        self.body = {}
        self.params = params
        self.res = None
        self._type_equality_funcs = {}

    def set_headers(self, headers):
        """设置请求头，参数为字典格式"""
        if isinstance(headers, dict):
            self.headers = headers
        else:
            raise TypeError('请求头参数请以字典格式传递')

    def set_header(self, key, value):
        """设置多个请求头"""
        self.headers[key] = value

    def set_body(self, body):
        """设置请求体，参数为字典格式"""
        if isinstance(body, dict):
            self.body = body
        else:
            raise TypeError('正文内容请以字典格式传递，xml正文格式如下：{"xml": xml字符串}')

    def send(self):
        """发送请求"""
        self.method = self.method.upper().strip()
        if self.method == 'GET':
            self.res = requests.get(url=self.url, headers=self.headers, params=self.params, verify=False)
        elif self.method == 'POST':
            if self.body_type == 1:
                self.set_header('Content-Type', 'application/x-www-form-urlencoded')
                self.res = requests.post(url=self.url, headers=self.headers, data=self.body, verify=False)
            elif self.body_type == 2:
                self.res = requests.post(url=self.url, headers=self.headers, data=self.body, verify=False)
            elif self.body_type == 3:
                self.set_header('Content-Type', 'text/xml')
                xml = self.body.get('xml')
                self.res = requests.post(url=self.url, headers=self.headers, data=xml, verify=False)
            elif self.body_type == 4:
                self.set_header('Content-Type', 'application/json')
                self.res = requests.post(url=self.url, headers=self.headers, json=self.body, verify=False)
            elif self.body_type == 5:
                self.res = requests.post(url=self.url, headers=self.headers, files=self.body, verify=False)
            elif self.body_type == 0:
                self.res = requests.post(url=self.url, headers=self.headers, verify=False)
            else:
                raise ValueError('正文格式类型参数错误')
        else:
            raise TypeError('请求方法类型错误，只支持get和post')

    @property
    def status_code(self):
        """响应状态码"""
        if self.res:
            code = self.res.status_code
            print('响应状态码为[%d]' % code)
            return code
        else:
            return None

    @property
    def response_time(self):
        """响应时间(毫秒)"""
        if self.res:
            time = round(self.res.elapsed.total_seconds() * 1000)
            print('响应时长为[%d]' % time)
            return time
        else:
            return None

    @property
    def text(self):
        """json格式响应正文"""
        if self.res:
            json_res = self.response_to_json()
            res = json.dumps(json_res, ensure_ascii=False, sort_keys=True)
            return res
        else:
            return None

    def response_to_json(self):
        """响应转为json对象"""
        if self.res:
            return self.res.json()
        else:
            return None

    def json_value_by_path(self, path):
        """通过jsonpath获取对象"""
        res = self.response_to_json()
        if res:
            val = jsonpath.jsonpath(res, path)[0]
            return val
        else:
            return None

    def check_status_code_is(self, status_code):
        if isinstance(status_code, str):
            status_code = int(status_code)
        self.assertEqual(self.status_code, status_code, '响应状态码不是[%d]' % status_code)

    def check_status_code_is_200(self):
        self.assertEqual(self.status_code, 200, '响应状态码不是200')

    def check_response_time_less_than(self, duration=None):
        if duration == None:
            duration = 200
        else:
            if isinstance(duration, str):
                duration = int(duration)
        self.assertLess(self.response_time, duration, '响应时间超过[%d]ms' % duration)

    def check_contain(self, exp, res):
        self.assertIn(exp, res, '预期结果[%s]不在实际结果内' % exp)

    def check_true(self, path1, path2):
        fir = len(self.json_value_by_path(path1))
        sec = self.json_value_by_path(path2)
        self.assertTrue(fir == sec, '字段值[%d]和[%d]不相等' % (fir, sec))

    def check_is_null(self, key, container):
        temp1 = '{}: null'.format(key)
        temp2 = '{}: ""'.format(key)
        temp3 = '{}: []'.format(key)
        temp4 = '{}: {}'.format(key, {})
        members = [temp1, temp2, temp3, temp4]
        for i in members:
            self.assertNotIn(i, container, '预期字段[%s]为空' % key)

    def check_length(self, exp, key=None, path=None):
        """长度校验"""
        if path == None:
            key = '"{}"'.format(key)
            count = self.text.count(key)
            self.assertEqual(count, exp, '[%s]字段长度和预期结果不一致' % key)
        else:
            data = self.json_value_by_path(path)
            if data:
                count = len(data[0])
                self.assertEqual(count, exp, '预期个数和实际不一致')
            else:
                return None

    def check_json_value(self, key, exp):
        """检查json最外层元素"""
        if self.response_to_json():
            first = self.response_to_json().get(key)
        else:
            first = None
        self.assertEqual(first, exp, '值检查失败！实际结果：{} 预期结果：{}'.format(first, exp))

    def check_json_value_by_path(self, path, exp):
        first = self.json_value_by_path(path)
        if first:
            self.assertEqual(first, exp, '值检查失败！实际结果：{} 预期结果：{}'.format(first, exp))
        else:
            return None

    def check_db(self, sql):
        cursor = self.connect.cursor()
        cursor.execute(sql)
        self.connect.commit()
        return cursor.fetchone()

    def log(self, msg):
        print(msg)
