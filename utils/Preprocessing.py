import requests
import yaml
import time


'''
:url
:下载yaml
: 修改yaml
'''
class yaml_collect:

    def __init__(self, url: str, api: str, api_port:int, port: int):
        self.url = url
        self.api = api
        self.port = port
        self.api_port = api_port
    
    def url2sub(self):
        '''
        获取订阅转换地址
        '''
        sub_config = 'https%3A%2F%2Fraw.githubusercontent.com%2FACL4SSR%2FACL4SSR%2Fmaster%2FClash%2Fconfig%2FACL4SSR_Online_Full.ini'
        sub_url = 'https://'+self.api+'/sub?target=clash&url='+self.url+'&insert=false&config='+sub_config+'&emoji=true&expand=true&fdn=false&new_name=true'
        return sub_url

    def get_yaml(self):
        '''
        :写入yaml文件
        '''
        url = self.url2sub()
        _headers = {'User-Agent': 'ClashforWindows/0.18.1'}
        try:
            start_time = time.time()
            resp = requests.get(url, headers=_headers)
            print('下载时间%s'%(time.time() - start_time))
            node_yaml = yaml.load(resp.text,Loader=yaml.FullLoader) #node_yaml:dict
            print('yaml转换%s'%(time.time() - start_time))
            nodename,nodetype,node_sever,groupname = self.node_info(node_yaml)
            node_yaml['port'] = self.port
            node_yaml['socks-port'] = self.port+1
            node_yaml['external-controller'] = '127.0.0.1:%s'%self.api_port
            print('关键词修改%s'%(time.time() - start_time))
            with open('./temp/temp.yaml', 'w',encoding="utf-8") as f:
                    yaml.dump(node_yaml, f,allow_unicode=True,sort_keys=False) 
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
    



