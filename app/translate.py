#百度通用翻译API,不包含词典、tts语音合成等资源，如有相关需求请联系translate_api@baidu.com
# coding=utf-8
import http.client
import hashlib
import urllib
import random
import json
from flask import current_app
from flask_babel import _



def translate(text, source_language, dest_language):
    if 'TRANSLATOR_KEY' not in current_app.config or \
            not current_app.config['TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')
    httpClient = None
    appid = current_app.config['APPID']
    secretKey = current_app.config['TRANSLATOR_KEY']
    myurl = '/api/trans/vip/translate'
    fromLang = source_language  # 原文语种
    toLang = dest_language  # 译文语种
    salt = random.randint(32768, 65536)
    q = text
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)
        return result['trans_result'][0]['dst']
    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()


if __name__ == '__main__':
    text = 'apple'
    print(translate(text=text, dest_language='zh'))