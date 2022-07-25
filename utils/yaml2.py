import cleaner
import yaml
import time
import requests
_headers = {'User-Agent': 'ClashforWindows/0.18.1'}
url = 'https://api.v1.mk/sub?target=clash&url=https%3A%2F%2Fopenit.daycat.space%2Fhttps&insert=false&config=https%3A%2F%2Fraw.githubusercontent.com%2FACL4SSR%2FACL4SSR%2Fmaster%2FClash%2Fconfig%2FACL4SSR_Online_Full.ini&emoji=true&list=false&udp=false&tfo=false&expand=true&scv=false&fdn=false&new_name=true'
port = 1000
api_port = 10001
start_time = time.time()
path_yaml = './temp/temp.yaml'
resp = requests.get(url, headers=_headers)
print('下载时间%s'%(time.time() - start_time))
with open('./temp/temp.yaml', 'w',encoding="utf-8") as f:
    f.write(resp.text) 
print('写入时间%s'%(time.time() - start_time))
with open(path_yaml,encoding="UTF-8") as fp:
    print('关键词一%s'%(time.time() - start_time))
    cl = cleaner.ClashCleaner(fp)
    nodename = cl.nodesName()
    nodetype = cl.nodesType()
    proxy_group = cl.proxyGroupName()
    node_sever = cl.node_server()
print('关键词二%s'%(time.time() - start_time))
yaml2 = cl.yaml
yaml2['port'] = port
yaml2['socks-port'] = port+1
yaml2['external-controller'] = '127.0.0.1:%s'%api_port
print('关键词三%s'%(time.time() - start_time))
with open('./temp/temp2.yaml', 'w',encoding="utf-8") as f:
        yaml.dump(yaml2, f,allow_unicode=True,sort_keys=False) 
print('最终时间%s'%(time.time() - start_time))    