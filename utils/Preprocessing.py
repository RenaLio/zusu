import requests
import yaml
import time
import aiohttp
from aiohttp.client_exceptions import ClientConnectorError, ClientResponseError

'''
:url
:下载yaml
:修改yaml
'''
class yaml_collect:

    def __init__(self, url: str, api: str, api_port:int, port: int):
        self.url = url
        self.api = api
        self.port = port
        self.api_port = api_port
    
    async def url2sub(self):
        '''
        获取订阅转换地址
        '''
        sub_config = 'https%3A%2F%2Fraw.githubusercontent.com%2FACL4SSR%2FACL4SSR%2Fmaster%2FClash%2Fconfig%2FACL4SSR_Online_Full.ini'
        sub_url = self.api+'/sub?target=clash&url='+self.url+'&insert=false&config='+sub_config+'&emoji=false&expand=true&fdn=false&new_name=true'
        return sub_url

    async def downyaml(self):
        url = await self.url2sub()
        _headers = {'User-Agent': 'ClashforWindows/0.18.1'}
        try:
            async with aiohttp.ClientSession(headers=_headers) as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        with open('./temp/temp.yaml', 'w',encoding='utf-8') as fd:
                            fd.write(await response.text())
                            return True
                    else:
                        return False
        except TimeoutError as e:
            return False
        except ClientConnectorError as c:
            print(c)
            return False



    async def get_yaml(self):
        '''
        :写入yaml文件
        '''

        try:
            with open('./temp/temp.yaml','r', encoding="UTF-8") as f:
                yaml_data = yaml.load(f, Loader=yaml.FullLoader)
            start_time = time.time()
            nodename,nodetype,node_sever,groupname = self.node_info(yaml_data)
            yaml_data['port'] = self.port
            yaml_data['socks-port'] = self.port+1
            yaml_data['external-controller'] = '127.0.0.1:%s'%self.api_port
            print('关键词修改%s'%(time.time() - start_time))
            with open('./temp/temp.yaml', 'w',encoding="utf-8") as f:
                    yaml.dump(yaml_data, f,allow_unicode=True,sort_keys=False)
            print('最终时间%s'%(time.time() - start_time))           
            return (nodename,nodetype,node_sever,groupname)
        except:
            nodename = ''
            nodetype = ''
            node_sever  = ''
            groupname = ''
            return (nodename,nodetype,node_sever,groupname)
        
    def set_port(self):
        with open('./temp/temp.yaml',encoding="UTF-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        nodename = []
        for i in data['proxies']:
            nodename.append(i['name'])
        nodetype = []

        
        return data
    def node_info(self,node_yaml):
        """
        获取节点信息
        :return: list
        """
        nodename = []
        nodetype = []
        node_sever = []
        groupname = ''
        for i in node_yaml['proxies']:
            nodename.append(i['name'])
            nodetype.append(i['type'])
            node_sever.append(i['server'])
        for t in node_yaml['proxy-groups']:
                if t['type'] == 'select' and len(t['proxies']) >= len(nodename):
                    groupname = t['name']
                    break
                else:
                    pass
        return nodename,nodetype,node_sever,groupname
    



