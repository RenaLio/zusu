import requests
from pyrogram.errors import RPCError
import subprocess
import tqdm
import time
import threading
from retry import retry
import json
import yaml

with open('./config.yaml',encoding="UTF-8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
path_yaml = './temp/temp.yaml'
retry_times = 3     #重试次数
thread_num = 32     #线程数量
# time_out = '5' # 5000毫秒

thread_max_num =threading.Semaphore(32)
'''
master-workers
'''

# def testurl(client,message,nodename,api_port):
def testurl(nodename,api_port):
    global path_clash
    start_time = time.time()
    # 运行clash
    path_clash = './Clash.Meta-windows-amd64.exe'
    clash = subprocess.Popen([path_clash, '-f', path_yaml])
    time.sleep(3)
    print(111)
    # 检测延迟
    # thread_num = 32
    proxy_ping = {}
    print(222)
    # thread_max_num =threading.Semaphore(thread_num)
    print(333)
    for proxy_name in nodename:
        #为每个新URL创建下载线程
        t = threading.Thread(target=https_ping, args=(proxy_name,proxy_ping,api_port,5))
        #加入线程池并启动
        t.start()
    clash.terminate()
    print('测试延迟%s'%(time.time() - start_time))
    print(9999)
    print(proxy_ping)
    return proxy_ping



def https_ping(proxy_name,proxy_ping,api_port,timeout):
    ctime_out =str(timeout*1000)
    test_url = 'https://www.gstatic.com/generate_204'
    with thread_max_num:
        @retry(tries=retry_times)
        def start_ping(proxy_name):
            url_fr = 'http://127.0.0.1:'+api_port+'/proxies/'+proxy_name+'/delay?timeout='+ctime_out+'&url='+test_url
            rp = requests.get(url=url_fr,timeout=timeout)
            response = json.loads(rp.text)
            delay = response['delay']
            proxy_ping.update({proxy_name:delay}) 
        try:
            start_ping(proxy_name)
        except:
            proxy_ping.update({proxy_name:-1})

