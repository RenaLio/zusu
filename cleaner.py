import sys
import time

import yaml
from bs4 import BeautifulSoup


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
            return ""

    def changeClashPort(self, port: str or int = 1122):
        """
        改变配置文件端口
        """
        if 'mixed-port' in self.yaml:
            self.yaml['mixed-port'] = int(port)
            print("配置端口已被改变为：", self.yaml['mixed-port'])
        elif 'port' in self.yaml:
            self.yaml['port'] = int(port)
            print("配置端口已被改变为：", self.yaml['port'])

    def changeClashEC(self, ec: str = '1123'):
        """
        改变external-controller地址与端口
        """
        ec = '127.0.0.1:'+str(ec)
        self.yaml['external-controller'] = ec
        print("外部控制地址已被修改为", self.yaml['external-controller'])

    def changeClashMode(self, mode: str = "global"):
        """
        改变clash模式
        """
        self.yaml['mode'] = mode
        print("Clash 模式已被修改为:", self.yaml['mode'])

    def save(self, savePath: str = "./sub.yaml"):
        with open(savePath, "w", encoding="UTF-8") as fp:
            yaml.dump(self.yaml, fp)


class ReCleaner:
    def __init__(self, data: dict):
        self.data = data
        self._sum = 0
        self._netflix_info = []

    def getnetflixinfo(self):
        """

        :return: list: [netflix_ip, proxy_ip, netflix_info: "解锁"，“自制”，“失败”，“N/A”]
        """
        try:
            # print(self.data['ip'])
            if self.data['ip'] is None or self.data['ip'] == "N/A":
                return ["N/A", "N/A", "N/A"]
            if self.data['netflix1'] is None:
                return ["N/A", "N/A", "N/A"]
            if self.data['netflix2'] is None:
                return ["N/A", "N/A", "N/A"]
            r1 = self.data['netflix1']
            status_code = self.data['ne_status_code1']
            if status_code == 200:
                self._sum += 1
                soup = BeautifulSoup(r1, "html.parser")
                netflix_ip_str = str(soup.find_all("script"))
                p1 = netflix_ip_str.find("requestIpAddress")
                netflix_ip_r = netflix_ip_str[p1 + 19:p1 + 60]
                p2 = netflix_ip_r.find(",")
                netflix_ip = netflix_ip_r[0:p2]
                self._netflix_info.append(netflix_ip)  # 奈飞ip
            r2 = self.data['ne_status_code2']
            if r2 == 200:
                self._sum += 1

            self._netflix_info.append(self.data['ip']['ip'])  # 请求ip

            if self._sum == 0:
                ntype = "失败"
                self._netflix_info.append(ntype)  # 类型有四种，分别是无、仅自制剧、原生解锁（大概率）、 DNS解锁
                print("当前节点情况: ", self._netflix_info)
                return self._netflix_info
            elif self._sum == 1:
                ntype = "自制"
                self._netflix_info.append(ntype)
                print("当前节点情况: ", self._netflix_info)
                return self._netflix_info
            elif self.data['ip']['ip'] == self._netflix_info[0]:
                ntype = "解锁"
                self._netflix_info.append(ntype)
                print("当前节点情况: ", self._netflix_info)
                return self._netflix_info
            else:
                ntype = "解锁"
                self._netflix_info.append(ntype)
                print("当前节点情况: ", self._netflix_info)
                return self._netflix_info
        except Exception as e:
            print(e)
            return ["N/A", "N/A", "N/A"]

    def getyoutubeinfo(self):
        """

                :return: str :解锁信息: (解锁、失败、N/A)
                """
        try:
            if 'youtube' not in self.data:
                print("采集器内无数据")
                return "N/A"
            else:
                if "is not available" in self.data['youtube']:
                    return "失败"
                elif "YouTube Music 在您所在区域无法使用" in self.data['youtube']:
                    return "失败"
                elif self.data['youtube_status_code'] == 200:
                    return "解锁"
                else:
                    return "N/A"
        except Exception as e:
            print(e)
            return "N/A"

    def getDisneyinfo(self):
        """

        :return: 解锁信息: 解锁、失败、N/A
        """
        try:
            if self.data['disney'] is None:
                return "N/A"
            else:
                return self.data['disney']
        except Exception as e:
            print(e)
            return "N/A"

    def getGping(self):
        """
        获取Google ping的延迟
        :return: str: 字符串化的延迟，保留到个位数
        """
        if 'delay' in self.data:
            return "%.0fms" % self.data['delay']
        else:
            return "0ms"


class ConfigManager:
    """
    配置清洗
    """

    def __init__(self, configpath="./config.yaml"):
        """

        """
        self.yaml = {}
        with open(configpath, "r", encoding="UTF-8") as fp:
            self.config = yaml.load(fp, Loader=yaml.FullLoader)
        try:
            self.yaml.update(self.config)
        except Exception:
            print("加载配置出错")
        if self.config is None:
            di = {'loader': "True"}
            with open(configpath, "w+", encoding="UTF-8") as fp:
                yaml.dump(di, fp)

    def getAdmin(self):
        try:
            return self.config['admin']
        except KeyError:
            return None

    def getuser(self):
        try:
            return self.config['user']
        except KeyError:
            print("获取用户失败,将采用默认用户")
            return []  # 默认名单

    def get_proxy_port(self):
        try:
            return self.config['proxyport']
        except KeyError:
            print("获取代理端口失败，将采用默认7890端口")
            return 7890

    def add(self, data: dict, key):
        try:
            self.yaml[key] = data[key]
        except Exception as e:
            print("添加失败！")
            print(e)

    def add_admin(self, admin: list or str or int):
        """
        添加管理员
        """
        adminlist = []

        if admin is list:
            for li in admin:
                adminlist.append(li)
        else:
            adminlist.append(admin)
        try:
            old = self.config['admin']
            if old is not None:
                adminlist.extend(old)
                newadminlist = list(set(adminlist))  # 去重
                self.yaml['admin'] = newadminlist
                print("添加成功")
        except KeyError:
            newadminlist = list(set(adminlist))  # 去重
            self.yaml['admin'] = newadminlist
            print("添加成功")

    def del_admin(self, admin: list or str or int):
        """
        删除管理员
        """
        try:
            adminlist = self.config['admin']
            if adminlist is not None:
                if admin is list:
                    for li in admin:
                        adminlist.remove(li)
                else:
                    adminlist.remove(admin)
                self.yaml['admin'] = adminlist
        except TypeError as t:
            print("删除失败")
            print(t)

    def add_user(self, user: list or str or int):
        """
        添加授权用户
        """
        userlist = []

        if user is list:
            for li in user:
                userlist.append(li)
        else:
            userlist.append(user)
        try:
            old = self.config['user']
            if old is not None:
                userlist.extend(old)
            newuserlist = list(set(userlist))  # 去重
            self.yaml['user'] = newuserlist
            print("添加成功")
        except KeyError:
            newuserlist = list(set(userlist))  # 去重
            self.yaml['user'] = newuserlist
            print("添加成功")

    def del_user(self, user: list or str or int):
        """
        删除授权用户
        """
        try:
            userlist = self.config['user']
            if userlist is not None:
                if user is list:
                    for li in user:
                        userlist.remove(li)
                else:
                    userlist.remove(user)
                self.yaml['user'] = userlist
        except TypeError as t:
            print("删除失败")
            print(t)

    def save(self, savePath: str = "./config.yaml"):
        with open(savePath, "w+", encoding="UTF-8") as fp:
            try:
                yaml.dump(self.yaml, fp)
            except Exception as e:
                print(e)

    def reload(self, configpath="./config.yaml"):
        with open(configpath, "r", encoding="UTF-8") as fp:
            self.config = yaml.load(fp, Loader=yaml.FullLoader)

    def newsub(self, suburl: dict):
        """添加订阅"""
        url = suburl
        try:
            old = self.config['suburl']
            if old is not None:
                url.update(old)
            self.yaml['suburl'] = url
        except KeyError:
            self.yaml['suburl'] = url

    def delsub(self, subname: str):
        try:
            suburl = self.config['suburl']
            if suburl is not None:
                if subname in suburl:
                    suburl.pop(subname)
        except TypeError as t:
            print("删除失败")
            print(t)
