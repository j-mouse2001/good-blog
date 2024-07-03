import datetime
import hashlib
import base64
import json

import requests


# class for using YunYongXin achieve sms verification feature
class YunTongXin:

    base_url = 'https://app.cloopen.com:8883'

    def __init__(self, accountSid, accountToke, appId, templateId):
        self.accountSid = accountSid
        self.accountToken = accountToke
        self.appId = appId
        self.templateId = templateId

    def get_request_url(self, sig):
        url = self.base_url + '/2013-12-26/Accounts/%s/SMS/TemplateSMS?sig=%s' % (self.accountSid, sig)
        return url

    def get_sig(self, timestamp):
        # create the sig from the server
        s = self.accountSid + self.accountToken + timestamp
        m = hashlib.md5()
        m.update(s.encode())
        return m.hexdigest().upper()

    def get_timestamp(self):
        # create timestamp and return
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    def get_request_header(self, timestamp):
        # create request header
        s = self.accountSid + ':' + timestamp
        auth = base64.b64encode(s.encode()).decode()
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': auth
        }

    def get_request_body(self, phone, code):
        return {
            'to': phone,
            'appId': self.appId,
            'templateId': self.templateId,
            'datas': [code, '5']
        }

    def request_api(self, url, header, body):
        response = requests.post(url=url, headers=header, data=body)
        return response.text

    def run(self, phone, code):
        # get the time stamp
        timestamp = self.get_timestamp()
        sig = self.get_sig(timestamp)
        request_url = self.get_request_url(sig)
        header = self.get_request_header(timestamp)
        body = self.get_request_body(phone, code)
        data = self.request_api(request_url, header, json.dumps(body))
        return data

if __name__ == '__main__':
    obj = YunTongXin('2c94811c8cd4da0a01901c42eedf3faa', '092dafa2fac04f79ae8b51145dc03703',
                     '2c94811c8cd4da0a01901c42f06c3fb1', '1')
    res = obj.run('13369928212', '0112')
    print(res)