import requests
import hashlib
import re
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from time import sleep
import xml.etree.ElementTree as ET

URL = 'http://192.168.188.120/'
USER = 'user'
PASSWORD = 'user'
LISTEN_PORT = 9157

def parse_instance(instance_xml):
    kv_pairs = list(node.text for node in instance_xml)
    names = kv_pairs[::2]
    values = kv_pairs[1::2]
    return dict(zip(names, values))

def parse_instances(parent):
    instances = []
    for instance in parent.findall("Instance"):
        instances.append(parse_instance(instance))
    return instances

def parse_xml(xml):
    tree = ET.fromstring(xml)
    all_instances = {}
    for elem in tree:
        instances = parse_instances(elem)
        if instances:
            all_instances[elem.tag] = instances

    return all_instances

mappings = {
    "Status": {
        "Up": 1,
        "Down": 0,
    },
    "CurrentProfile": {
        "17a": 1,
        "35b": 2,
    }
}

dsl_metric_names = [
    'Link_retrain',
    'DownCrc_errors',
    'Upstream_power',
    'DownInterleaveDelay',
    'Downstream_noise_margin',
    'Downstream_attenuation',
    'Downstream_current_rate',
    'CurrentProfile',
    'UpCrc_errors',
    'Showtime_start',
    'UpstreamInp',
    'Fec_errors',
    'UpInterleaveDelay',
    'Upstream_noise_margin',
    'Status',
    'Upstream_attenuation',
    'Upstream_max_rate',
    'UpInterleaveDepth',
    'Downstream_power',
    'Downstream_max_rate',
    'Upstream_current_rate',
    'DownInterleavedepth',
    'DownstreamInp',
    'Atuc_fec_errors'
]

lan_metric_names = [
    'BytesReceived',
    'Status',
    'LinkSpeed',
    'BytesSent'
]

class CustomCollector(object):

    def request(self):
        s = requests.Session()
        r = s.get(URL+'function_module/login_module/login_page/logintoken_lua.lua')
        token = re.search('(\d+)', str(r.content)).group(0)
        
        values = {'action': 'login',
                  'Username': USER,
                  'Password': hashlib.sha256(str(PASSWORD+token).encode('utf-8')).hexdigest()}
        cookies = {'_TESTCOOKIESUPPORT': "1"}

        r = s.post(URL, data=values, cookies=cookies)
        cookies.update(s.cookies.get_dict())
        
        s.get(URL+"getpage.lua?pid=123&nextpage=Internet_AdminInternetStatus_DSL_t.lp&Menu3Location=0", cookies=cookies)
        r = s.get(URL+"common_page/internet_dsl_interface_lua.lua", cookies=cookies)
        dsl_info = parse_xml(r.content)

        s.get(URL+"getpage.lua?pid=123&nextpage=Localnet_LocalnetStatusAd_t.lp&Menu3Location=0", cookies=cookies)
        r = s.get(URL+"common_page/lanStatus_lua.lua", cookies=cookies)
        lan_info = parse_xml(r.content)

        return {"dsl_info": dsl_info, "lan_info": lan_info}

    def collect(self):
        metrics = self.request()
        dsl_info = metrics["dsl_info"]["OBJ_DSLINTERFACE_ID"]

        dsl_metrics = {}
        for metric_name in dsl_metric_names:
            this_metric = GaugeMetricFamily(metric_name, "-- n/a --", labels=["inst_id"])
            for instance in dsl_info:
                value = instance[metric_name]
                mapping = mappings.get(metric_name)

                if mapping:
                    value = mapping.get(value, 0)

                this_metric.add_metric([instance["_InstID"]], value)

            yield this_metric

        lan_info = metrics["lan_info"]["OBJ_ETH_ID"]
        lan_metrics = {}
        for metric_name in lan_metric_names:
            this_metric = GaugeMetricFamily(metric_name, "-- n/a --", labels=["inst_id"])
            for instance in lan_info:
                value = instance[metric_name]
                mapping = mappings.get(metric_name)

                if mapping:
                    value = mapping.get(value, 0)

                this_metric.add_metric([instance["_InstID"]], value)

            yield this_metric

REGISTRY.register(CustomCollector())
start_http_server(LISTEN_PORT)
print("Listening on "+str(LISTEN_PORT))

while True:
    sleep(100)
