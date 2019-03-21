from util.rwCaseData import RWCaseData
from base import HTMLTestReportCN
from base.hsfclient import *
import unittest
import time

data = RWCaseData()
suite = unittest.TestSuite()
rows = data.case_lines
for row in range(2, rows + 1):
    is_run = data.get_is_run(row)
    if is_run:
        case_id = data.get_case_id(row)
        case_name = data.get_case_name(row)
        url = data.get_url(row)
        method = data.get_request_method(row)
        headers = data.get_headers(row)
        body_type = data.get_body_type(row)
        body_content = data.get_body_content(row)
        depend_case_id = data.get_depend_case_id(row)
        depend_data = data.get_depend_data(row)
        depend_key = data.get_depend_key(row)
        expect_status_code = 200
        expect_res_time = 500
        except_res_value = data.get_expect_res_value(row)

        if depend_case_id:
            r = data.get_case_id_row(depend_case_id)
            url_d = data.get_url(r)
            method_d = data.get_request_method(r)
            headers_d = data.get_headers(r)
            body_type_d = data.get_body_type(r)
            body_content_d = data.get_body_content(r)
            client = HSFClient(url_d, method_d, body_type_d)
            client.set_headers(headers_d)
            client.set_body(body_content_d)
            client.send()
            val = client.json_value_by_path(depend_data)
            if isinstance(val, int):
                val = '&' + depend_key + '=' + str(val)
            url = url + val

        CASE_TEMPLATE = '''class {class_name}(unittest.TestCase):
    def {method_name}(self):
        client = HSFClient(url="{url}", method="{method}", body_type=BodyType.{body_type})
        client.set_headers({headers})
        client.set_body({body_content})
        client.send()\n'''.format(class_name=case_id, method_name=case_name, url=url, method=method,
                                  body_type=body_type, headers=headers, body_content=body_content)
        if except_res_value == None:
            exec(CASE_TEMPLATE)
            exec("suite.addTest(%s('%s'))" % (case_id, case_name))
        else:
            # 校验状态码&响应时间&字段值
            check_values_contain = except_res_value[0]
            check_null = except_res_value[1]
            check_len = except_res_value[2]
            check_value_equal = except_res_value[3]
            CASE_TEMPLATE += '''        try:
            client.check_status_code_is({status_code})
            client.check_response_time_less_than({res_time})
            for i in {check_values_contain}:
                client.check_contain(i, client.text)
            for i in {check_null}:
                client.check_is_null(i, client.text)
            for k, v in {check_len}.items():
                client.check_length(path=k, exp=v)
            for k, v in {check_value_equal}.items():
                client.check_true(k, v)
        except Exception as e:
            data.write_result({row}, "fail")
            data.write_result({row}, client.text, 1)
            raise e
        else:
            client.log("{case_name}测试通过√")
            data.write_result({row}, "pass")
            data.write_result({row}, "", 1)\n'''.format(status_code=expect_status_code, res_time=expect_res_time,
                                                        case_name=case_name, row=row,
                                                        check_values_contain=check_values_contain,
                                                        check_null=check_null, check_len=check_len,
                                                        check_value_equal=check_value_equal)
            # print(CASE_TEMPLATE)
            exec(CASE_TEMPLATE)
            exec("suite.addTest(%s('%s'))" % (case_id, case_name))

now = time.strftime('%Y%m%d_%H%M%S')
# with open('./report/%s.html' % now, 'wb') as f:
with open('./report/index.html', 'wb') as f:
    HTMLTestReportCN.HTMLTestRunner(stream=f, title='接口自动化报告').run(suite)
