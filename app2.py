import argparse

from flask import Flask, render_template, jsonify, request
import requests
import random
from datetime import datetime
import re
import os
import json
from split_text import SplitSentence
from wrapper_consul import Consul, GetServiceUrl
import socket
import waitress
split_sentence = SplitSentence()
app = Flask(__name__)
puncs_fine = ['……', '\r\n', '，', '。', ';', '；', '…', '！',
              '!', '?', '？', '\r', '\n', '“', '”', '‘', '’',
              '：', ":", ".", "\"", "$", "&"]
count = 0
import json

with open("intent.json", "rb") as f:
    zh_en = json.load(f)
# zh_en={"询问bot基本信息":"ask_for_bot_informations","表示意见":"express_opinions","表达不满焦虑":"negative_emotions_agitated","消极情绪羞辱":"negative_emotions_insult","表示沮丧":"negative_emotions_unhappy","表示礼貌":"polite_behavior","常规事件":"regular_event","表示歉意":"user_apologize_to_bot","表示关心":"user_care_about","表示安慰":"user_comfort_bot","表示失落":"user_emotion_in_low_spirits","表示侮辱":"user_express_abuse","表示很开心":"user_express_mood_great","表示分享":"user_express_share","表示问候":"user_greetings","表示短暂告别":"user_polite_say_goodbye","表示赞美":"user_praised","分享负面事件":"user_share_negative_events","分享积极事件":"user_share_positive_events","表示感谢":"user_thank"}
with open("intent_sanji.json", "rb") as f:
    sanji_json = json.load(f)
    print(sanji_json)
print(zh_en)
tags_zh_en = {"中性意图": "neutral", "正向意图": "positive", "负向意图": "negative"}


def judge_en(sentence):
    # 判断英文
    ignores = []
    result = ''.join(re.findall(r'[A-Za-z]', sentence))
    result = result.lower()
    for ignore in ignores:
        if ignore in result:
            result = result.replace(ignore, "")
    if len(result) > len(sentence) / 2:
        return True
    else:
        return False


def judge_zh(sentence):
    # 判断中文
    result = ''.join(re.findall(re.compile("([\u4E00-\u9FA5]+)"), sentence))
    if len(result) > len(sentence) / 2:
        return True
    else:
        return False


def query_ernie_token():
    # import requests

    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=rY4P1P75XBnAoHnKVDwV015X&client_secret=HjZ2vS5PYathHK6A0W44caWU8lUt6XIE'
    response = requests.get(host)
    if response:
        print(response.json())
    return response.json()["access_token"]


def query_ernie(inpu):
    headers = {
        'User-Agent': 'Apipost client Runtime/+https://www.apipost.cn/',
        'Content-Type': 'application/json',
    }

    params = (
        ('access_token', query_ernie_token()),
    )

    data = {"text": f"判断以下文本的意图：{inpu}", "max_gen_len": "40"}

    print(data)

    response = requests.post('https://aip.baidubce.com/rpc/2.0/ai_custom/v1/text_gen/intent_chat', headers=headers,
                             params=params, json=data)
    print(response.json())
    if "result" in response.json():
        result = response.json()["result"]["content"]
        return {"category": zh_en.get(result, "others")}
    else:
        return response.json()["error_msg"]


def query_cpm(text):
    url = "http://172.26.183.115:8015/z"

    payload = json.dumps({
        "prompt": f"句子：{text} 意图：",
        "number": 1,
        "length": 150,
        "top_p": 1,
        "top_k": 1,
        "temperature": 0.8,
        "strategy": "append"
    })
    headers = {
        'User-Agent': 'apifox/1.0.0 (https://www.apifox.cn)',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    category = zh_en.get(response.json()["new_sentence"].replace("《", "").replace("》", ""), "others")
    return {"category": category, "tags": tags_zh_en.get(sanji_json.get(category, "中性意图"))}


def query_ZH(text):
    headers = {
        'User-Agent': 'Apipost client Runtime/+https://www.apipost.cn/',
        'Content-Type': 'application/json',
    }

    data = json.dumps({"sentence": text})
    response = requests.post('http://39.101.149.45:8084/classifier/intent_classifier', headers=headers, data=data)
    return response.json()


def query_EN(text):
    headers = {
        'User-Agent': 'Apipost client Runtime/+https://www.apipost.cn/',
        'Content-Type': 'application/json',
    }

    data = json.dumps(
        {"prompt": f"{text} \nIntent:", "max_tokens": 50, "top_p": 0.9, "temperature": 0.95, "frequency_penalty": 0.3,
         "presence_penalty": 1, "model": "davinci:ft-rct-studio:text-davinci-001-2022-04-15-08-21-56", "stop": ["\n"]})

    response = requests.post('http://52.53.227.127:8000/v1/completions', headers=headers, data=data)
    category = "_".join(response.json()["choices"][0]["text"].split(" "))
    return {"category": category, "tags": tags_zh_en.get(sanji_json.get(category, "中性意图"))}


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/api-v1/bot/get_response/", methods=["POST"])
def query():
    raw_data = request.get_json()
    print(raw_data)
    text = raw_data["sentence"]
    if judge_zh(text):
        print(text)
        # response=query_ernie(text)
        response = query_cpm(text)
    elif judge_en(text):
        response = query_EN(text)
    else:
        response = {"category": "please_enter_ZH_or_EN"}

    return jsonify(response), 200


# 健康检查，必须
@app.route("/health")
def check_health():
    return "ok!"


# 容器环境内该方法不一定有效
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Intent forward server")
    parser.add_argument('--port', type=int, default=8077, help='The server port')
    parser.add_argument('--debug', type=bool, default=True, help='Is debug modal')
    parser.add_argument('--name', type=str, default='intent', help='The server name')
    args = parser.parse_args()
    consul_client = Consul()
    # 服务名字，要唯一,建议算法除了-之外，别加别的特殊符号
    host = get_ip()  # 本地ip，如果是docker部署，主要是宿主机的ip
    print(host)
    consul_client.RegisterService(args.name, host, args.port)
    try:
        waitress.serve(app, debug=args.debug, host='0.0.0.0', port=args.port)
        # app.run(debug=args.debug, host='0.0.0.0', port=args.port)
    except Exception as e:
        print(e)
    finally:
        consul_client.UnregisterService()

