import urllib
import re
import random
def url2name(message_text):
    pattern = re.compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")  # 匹配订阅地址
    # 获取订阅地址
    try:
        url = pattern.findall(message_text)[0]
        s = get_domain_by_urllib(url).split('.')
        num = len(s)
        taskname = ''
        for i in range(num-1):
            taskname = taskname+'*.'
        taskname = taskname+s[-1]
        taskname = taskname +'-'+str(random.randint(1001, 9999))
        return url,taskname
    except:
        url = ''
        taskname = ''
        return url,taskname


def get_domain_by_urllib(u):
    return urllib.parse.urlparse(u).netloc
