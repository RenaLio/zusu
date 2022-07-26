import asyncio
import time
import aiohttp
import async_timeout
import json
import urllib
from aiohttp.client_exceptions import ClientConnectorError, ClientResponseError

proxies = "http://127.0.0.1:7890"


class BaseCollector:
    def __init__(self):
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/102.0.5005.63 Safari/537.36'}

    async def status(self, url, proxy=None):
        with async_timeout.timeout(10):
            async with aiohttp.ClientSession(headers=self._headers) as session:
                async with session.get(url, proxy=proxy) as response:
                    return response.status

    async def fetch(self, url, proxy=None):
        with async_timeout.timeout(10):
            async with aiohttp.ClientSession(headers=self._headers) as session:
                async with session.get(url, proxy=proxy) as response:
                    return await response.text()


class SubCollector(BaseCollector):
    """
    订阅采集器，默认采集clash配置文件
    """

    def __init__(self, suburl: str):
        super().__init__()
        self.text = None
        self._headers = {'User-Agent': 'clash'}  # 这个请求头是获取流量信息的关键
        self.url = suburl

    async def start(self, proxy=None):
        try:
            with async_timeout.timeout(20):
                async with aiohttp.ClientSession(headers=self._headers) as session:
                    async with session.get(self.url, proxy=proxy) as response:
                        return response
        except Exception as e:
            print(e)

    async def getSubTraffic(self, proxy=None):
        """
        获取订阅内的流量
        :return: str
        """
        return await self.start(proxy=proxy)

    async def getSubConfig(self, proxy=proxies):
        """
        获取订阅配置文件
        :param proxy:
        :return: 获得一个文件: sub.yaml, bool : True or False
        """
        _headers = {'User-Agent': 'clash'}
        try:
            async with aiohttp.ClientSession(headers=_headers) as session:
                async with session.get(self.url, proxy=proxy, timeout=10) as response:
                    if response.status == 200:
                        with open('./temp/temp.yaml', 'wb+') as fd:
                            while True:
                                chunk = await response.content.read()
                                if not chunk:
                                    print("获取订阅成功")
                                    break
                                fd.write(chunk)
                            return True
        except ClientConnectorError as c:
            print(c)
            return False


class Collector:
    def __init__(self,proxyname):
        self.session = None

        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/102.0.5005.63 Safari/537.36'}
        self.netflixurl1 = "https://www.netflix.com/title/70242311"
        self.netflixurl2 = "https://www.netflix.com/title/70143836"
        self.ipurl = "https://api.ip.sb/geoip"
        self.youtubeurl = "https://music.youtube.com"
        self.info = {}
        self.info['节点名称'] = proxyname
        self.disneyurl1 = "https://www.disneyplus.com/"
        self.disneyurl2 = "https://global.edge.bamgrid.com/token"


    async def httpping(self,session: aiohttp.ClientSession,api_ports = 40000,time_out = 5):
        proxy_name = node_name =  urllib.parse.quote(self.info['节点名称'], safe='')
        timeout = str(time_out*1000)
        test_url = 'http://www.gstatic.com/generate_204'
        apiports = str(api_ports)
        url_fr = 'http://127.0.0.1:' + apiports + '/proxies/' + proxy_name + '/delay?timeout=' + timeout + '&url=' + test_url
        try:
            async with session.get(url_fr, timeout=time_out) as rp:
                if rp.status == 200:
                    response = await rp.text()
                    response = json.loads(response)
                    delay1 = response['delay']
                    print('Clash延迟：%sms' %delay1)
                    self.info['CLASH CHECK'] = delay1
                else:
                    delay1 = 9999
                    print('Clash延迟：%sms' % delay1)
                    self.info['CLASH CHECK'] = delay1
        except asyncio.exceptions.TimeoutError as e:
            delay1 = 9999
            print('Clash延迟：%sms' % delay1)
            self.info['CLASH CHECK'] = delay1
            print(e)
        except ClientConnectorError as c:
            delay1 = 9999
            print('Clash延迟：%sms' % delay1)
            self.info['CLASH CHECK'] = delay1
            print(c)
        except Exception as e:
            print("?", e)


    async def httpsping(self, session: aiohttp.ClientSession, proxy=None):
        """
        访问google的延迟
        :param session:
        :param proxy:
        :return: float: 一个浮点数值，毫秒为单位
        """
        try:
            s1 = time.time()
            a1 = await session.get("https://www.gstatic.com/generate_204", proxy=proxy, timeout=5)
            if a1.status == 204:
                delay = (time.time() - s1) * 1000
                delay = int(delay)
            else:
                delay = 9999
            print("延迟:", "%.0fms" % delay)
            self.info['HTTPS Ping'] = delay
        except asyncio.exceptions.TimeoutError as e:
            delay = 9999
            self.info['HTTPS Ping'] = delay
            print(e)
        except ClientConnectorError as c:
            delay = 9999
            self.info['HTTPS Ping'] = delay
            print(c)
        except Exception as e:
            print("?", e)

    async def fetch_ip(self, session: aiohttp.ClientSession, proxy=None):
        """
        ip查询
        :param session:
        :param proxy:
        :return:
        """
        try:
            res = await session.get(self.ipurl, proxy=proxy, timeout=5)
            print("ip查询状态：", res.status)
            if res.status != 200:
                self.info['CLASH CHECK'] = 9999
                self.info['HTTPS Ping'] = 9999
                self.info['ip'] = ''
                self.info['netflix1'] = 'N/A'
                self.info['netflix2'] = 'N/A'
                self.info['YouTube'] = 'N/A'
                self.info['Disney'] = "N/A"
                print("无法查询到代理ip")
                return self.info
            else:
                self.info['ip'] = await res.json()
        except asyncio.exceptions.TimeoutError as e:
            self.info['CLASH CHECK'] = 9999
            self.info['HTTPS Ping'] = 9999
            self.info['ip'] = ''
            self.info['netflix1'] = 'N/A'
            self.info['netflix2'] = 'N/A'
            self.info['YouTube'] = 'N/A'
            self.info['Disney'] = "N/A"
            print("?", e)
            return self.info
        except ClientConnectorError as c:
            self.info['CLASH CHECK'] = 9999
            self.info['HTTPS Ping'] = 9999
            self.info['ip'] = ''
            self.info['netflix1'] = 'N/A'
            self.info['netflix2'] = 'N/A'
            self.info['YouTube'] = 'N/A'
            self.info['Disney'] = "N/A"
            print("?", c)
            return self.info
        except Exception as e:
            print("?", e)

    async def fetch_ninfo1(self, session: aiohttp.ClientSession, proxy=None,reconnection=1):
        """
        自制剧检测
        :param session:
        :param proxy:
        :return:
        """
        try:
            n1 = await session.get(self.netflixurl1, proxy=proxy, timeout=5)
            if n1.status == 200:
                self.info['netflix1'] = '解锁'
            else:
                self.info['netflix1'] = '失败'
            print("Netflix1   正常检测")
        except ClientConnectorError as e:
            print("Netflix1请求发生错误:", e)
            if reconnection != 0:
                await self.fetch_ninfo1(session=session, proxy=proxy, reconnection=reconnection - 1)
            else:
                self.info['netflix1'] = '失败'
        except asyncio.exceptions.TimeoutError as c:
            print("Netflix2请求超时，正在重新发送请求......")
            if reconnection != 0:
                await self.fetch_ninfo2(session=session, proxy=proxy, reconnection=reconnection - 1)
            else:
                self.info['netflix2'] = '失败'

    async def fetch_ninfo2(self, session: aiohttp.ClientSession, proxy=None,reconnection=1):
        """
        非自制剧检测
        :param session:
        :param proxy:
        :return:
        """
        try:
            n2 = await session.get(self.netflixurl2, proxy=proxy, timeout=5)
            if n2.status == 200:
                self.info['netflix2'] = '解锁'
            else:
                self.info['netflix2'] = '失败'
            print("Netflix2   正常检测")
        except ClientConnectorError as e:
            print("Netflix2请求发生错误:", e)
            if reconnection != 0:
                await self.fetch_ninfo2(session=session, proxy=proxy, reconnection=reconnection - 1)
            else:
                self.info['netflix2'] = '失败'
        except asyncio.exceptions.TimeoutError as c:
            print("Netflix2请求超时，正在重新发送请求......")
            if reconnection != 0:
                await self.fetch_ninfo2(session=session, proxy=proxy, reconnection=reconnection - 1)
            else:
                self.info['netflix2'] = '失败'

    async def fetch_youtube(self, session: aiohttp.ClientSession, proxy=None):
        """
        Youtube解锁检测
        :param session:
        :param proxy:
        :return:
        """
        try:
            youtube = await session.get(self.youtubeurl, proxy=proxy, timeout=5)
            if youtube.status == 200 :
                self.info['YouTube'] = '解锁'
            else:
                self.info['YouTube'] = '失败'
            print("YouTube   正常检测")
        except asyncio.exceptions.TimeoutError as e:
            self.info['YouTube'] = '失败'
            print(e)
        except ClientConnectorError as c:
            self.info['YouTube'] = '失败'
            print(c)

    async def fetch_dis(self, session: aiohttp.ClientSession, proxy=None):
        """
        Disney+ 解锁检测
        :param session:
        :param proxy:
        :return:
        """
        try:
            dis1 = await session.get(self.disneyurl1, proxy=proxy, timeout=5)
            dis2 = await session.get(self.disneyurl2, proxy=proxy, timeout=5)
            if dis1.status == 200 and dis2.status != 403:
                self.info['Disney'] = "解锁"
            else:
                self.info['Disney'] = "失败"
            print("Disney+ 正常检测")
        except asyncio.exceptions.TimeoutError as e:
            self.info['Disney'] = '失败'
            print(e)
        except ClientConnectorError as c:
            self.info['Disney'] = "失败"
            print(c)

    async def start(self, proxy_name,api_ports,session: aiohttp.ClientSession = None, proxy=None):
        """
        启动采集器，采用并发操作
        :param session:
        :param proxy: using proxy
        :return: all content
        """

        try:
            if session is None:
                session = aiohttp.ClientSession(headers=self._headers)
                tasks = []
                task1 = asyncio.create_task(self.fetch_ip(session=session, proxy=proxy))
                tasks.append(task1)
                task2 = asyncio.create_task(self.fetch_ninfo1(session, proxy=proxy))
                tasks.append(task2)
                task3 = asyncio.create_task(self.fetch_ninfo2(session, proxy=proxy))
                tasks.append(task3)
                task4 = asyncio.create_task(self.fetch_youtube(session, proxy=proxy))
                tasks.append(task4)
                task5 = asyncio.create_task(self.fetch_dis(session, proxy=proxy))
                tasks.append(task5)
                task6 = asyncio.create_task(self.httpping(session,api_ports))
                tasks.append(task6)
                task7 = asyncio.create_task(self.httpsping(session, proxy=proxy))
                tasks.append(task7)
                done, pending = await asyncio.wait(tasks)
                print("任务已完成")
                if pending is None:
                    print("任务已完成11111111111111111111111")
                    await session.close()
                else:
                    await asyncio.sleep(1)
                    await session.close()
            return self.info
        except Exception as e:
            print(e)
            self.info['CLASH CHECK'] = 9999
            self.info['HTTPS Ping'] = 9999
            self.info['ip'] = ''
            self.info['netflix1'] = 'N/A'
            self.info['netflix2'] = 'N/A'
            self.info['YouTube'] = 'N/A'
            self.info['Disney'] = "N/A"
            return self.info


