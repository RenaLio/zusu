import yaml

class ClashCleaner:
    """
    yaml配置清洗
    """

    def __init__(self, config):
        """

        :param config: 传入一个文件对象，或者一个字符串,文件对象需指向 yaml/yml 后缀文件
        """
        self.yaml = yaml.load(config, Loader=yaml.FullLoader)

    def nodesCount(self):
        """
        获取节点数量
        :return: int
        """
        return len(self.yaml['proxies'])

    def nodesName(self):
        """
        获取节点名
        :return: list
        """
        lis = []
        for i in self.yaml['proxies']:
            lis.append(i['name'])
        return lis

    def nodesType(self):
        """
        获取节点类型
        :return: list
        """
        t = []
        for i in self.yaml['proxies']:
            t.append(i['type'])
        return t

    def node_server(self):
        """
        获取节点类型
        :return: list
        """
        tp = []
        for i in self.yaml['proxies']:
            tp.append(i['server'])
        return tp

    def proxyGroupName(self):
        """
        获取第一个"select"类型代理组的名字
        :return: str
        """
        try:
            for t in self.yaml['proxy-groups']:
                if t['type'] == 'select' and len(t['proxies']) >= self.nodesCount():
                    return t['name']
                else:
                    pass
        except Exception as e:
            print(e)
