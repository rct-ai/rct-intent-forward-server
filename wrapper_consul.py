import consul
import random
import requests
import json


def consul_http(url, interval, timeout=None, deregister=None, header=None):
    ret = {'http': url, 'interval': interval}
    if timeout:
        ret['timeout'] = timeout
    if deregister:
        ret['DeregisterCriticalServiceAfter'] = deregister
    if header:
        ret['header'] = header
    return ret


class Consul(object):
    ip_list = ["172.26.183.110", "172.26.18.1", "172.26.17.237"]
    port = 8506
    service_id = ""
    name = ""
    consulAddress = ""

    def __init__(self):
        '''初始化，连接consul服务器'''
        ip = random.choice(self.ip_list)
        self._consul = consul.Consul(ip, self.port)

    def ip_int(self, ip):
        res = 0
        for j, i in enumerate(ip.split('.')[::-1]):
            res += 256 ** j * int(i)
        return int(res)

    def getConsulAgentAddress(self, num):
        return self.ip_list[num % len(self.ip_list)]

    def RegisterService(self, name, ip, port, tags=None):

        tags = tags or []
        # 注册服务
        self.service_id = name + "-" + ip + "-" + str(port)
        # name = name
        check = consul_http("http://{0}:{1}/health".format(ip, port), "5s", "3s", "20s")
        payload = {}
        payload['name'] = name
        if self.service_id:
            payload['id'] = self.service_id
        if ip:
            payload['address'] = ip
        if port:
            payload['port'] = port
        if tags:
            payload['tags'] = tags
        if check:
            payload['check'] = check
        self.consulAddress = self.getConsulAgentAddress(self.ip_int(ip))
        url = 'http://' + self.consulAddress + ":8506/v1/agent/service/register"
        r = requests.put(url, json.dumps(payload), timeout=3)
        print(url, r.status_code, r.text)
        return self.service_id

    def UnregisterService(self, server_id):
        url = 'http://' + self.consulAddress + ':8506/v1/agent/service/deregister/%s' % server_id
        r = requests.put(url, timeout=3)
        print(url, r.status_code, r.text)


# 获取要访问的服务的url
def GetServiceUrl(name, path):
    return "http://consul-internal.rctdev.cn/" + name + path
