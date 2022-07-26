import time
import yaml
from utils.Preprocessing import yaml_collect as collect
# from config import configs



# url
# suburl
# taskneme

# self.url = url
# self.api = api
# self.port = port
# self.api_port = api_port

'''
下载文件
修改port
'''

# version = configs['version']
# print(version)
def tasK_test(config,url,taskname):
    '''
    下载文件
    修改port
    '''
    Subcvt = config['api']
    api_port = config['api_port']
    port = config['port']
    c= collect(url,Subcvt,api_port,port)
    nodename,nodetype,node_sever,groupname = c.get_yaml()
    if 
    return c
    nodename,nodetype,node_sever,groupname = c.get_yaml()




