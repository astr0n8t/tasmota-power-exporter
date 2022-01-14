import requests
from os import getenv
from time import sleep
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server

class TasmotaCollector(object):
    def __init__(self):
        self.ip = getenv('DEVICE_IP')
        if not self.ip:
            self.ip = "192.168.4.1"
        self.user = getenv('USER')
        self.password = getenv('PASSWORD')

    def collect(self):

        response = self.fetch()

        for key in response:
            metric_name = "tasmota_" + key.lower().replace(" ", "_") 
            metric = response[key].split()[0]
            unit = None
            if len(response[key].split()) > 1:
                unit = response[key].split()[1]
            g = GaugeMetricFamily(metric_name, key, labels=['device'], unit=unit)
            g.add_metric([self.ip], metric)
            yield g

    def fetch(self):

        url = 'http://' + self.ip + '/?m=1'

        session = requests.Session()
        
        if self.user and self.password:
            session.auth = (self.user, self.password)

        page = session.get(url)

        values = {}

        string_values = str(page.text).split("{s}")
        for i in range(1,len(string_values)-1):
            label = string_values[i].split("{m}")[0]
            value = string_values[i].split("{m}")[1].split("{e}")[0]
            values[label] = value

        return values

if __name__ == '__main__':

    port = getenv('EXPORTER_PORT')
    if not port:
        port = 8000

    start_http_server(int(port))
    REGISTRY.register(TasmotaCollector())

    while(True):
        sleep(1)
    