import consul
import uuid

# from flask import Flask
import random
import socket

class Consul(object):
    ip_list = ["172.26.183.110", "172.26.18.1", "172.26.17.237"]
    port = 8506
    service_id = ""
    name = ""
    def __init__(self):
        '''初始化，连接consul服务器'''
        ip = random.choice(self.ip_list)
        self._consul = consul.Consul(ip, self.port)

    def RegisterService(self, name, host, port, tags=None):
        tags = tags or []
        # 注册服务
        self.service_id = name + "-" + str(uuid.uuid4())
        self.name = name
        self._consul.agent.service.register(
            name,
            self.service_id,
            host,
            port,
            tags,
            check=consul.Check.http("http://{0}:{1}/health".format(host, port), "5s", "3s", "20s"),
        )
    def UnregisterService(self):
        self._consul.agent.service.deregister(self.service_id)

# 获取要访问的服务的url
def GetServiceUrl(name, path):
    return "http://consul-internal.rctdev.cn/" + name + path