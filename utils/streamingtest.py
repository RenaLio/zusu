import time
import subprocess
import async_timeout
from pyrogram.errors import RPCError
import re
import collector
import cleaner
import export
import proxys
from .Preprocessing import yaml_collect
from .typechange import chg_type
from .export_result import ExportResult
from retry import retry

sub_path = "./temp/temp.yaml"


async def testurl(client,task_queue,configs):
    taskname = task_queue.top()['task_name']
    msgchat_id = task_queue.top()['msgchat_id']
    msg_id = task_queue.top()['msg_id']
    bakmsg_id  = task_queue.top()['bakmsg_id']
    clash_path = configs['path_clash']
    port = configs['mixed-port']
    api_port = configs['external-controller']
    subcvt = configs['api']
    color = configs['color']
    front = configs['front']
    print('进入函数')
    try:
        s1 = time.time()
        chat_id = msgchat_id
        info = {}  # Netflix Youtube 等等
        # 获取订阅地址
        url =task_queue.top()['url']

        print("获取订阅链接："+url)

        # 启动下载配置文件
        suburl = url
        print("下载订阅：")
        sub = yaml_collect(suburl,subcvt,api_port,port)
        down = await sub.downyaml()
        print("下载完成：")
        print(down)
        # sub = collector.SubCollector(suburl=suburl)
        # config = await sub.getSubConfig()
        if not down:
            await client.edit_message_text(
                chat_id=chat_id,
                message_id=bakmsg_id,
                text="ERROR: 无法获取到订阅文件"
            )
            return
        # 启动订阅清洗
        nodename,nodetype,node_sever,proxy_group = await sub.get_yaml()   #返回结果
        print(nodename)
        if not nodename:
            await client.edit_message_text(
                chat_id=chat_id,
                message_id=bakmsg_id,
                text="ERROR: 无法获取到订阅文件"
            )
            return
        newnode_type = chg_type(nodetype)
        # 启动clash进程
        print('启动clash')
        command = fr"{clash_path} -f {sub_path}"
        subp = subprocess.Popen(command.split(), encoding="utf-8")
        time.sleep(2)
        # 进入循环，直到所有任务完成
        ninfo = []  # 存放所测节点Netflix的解锁信息
        youtube_info = []
        disneyinfo = []
        gpinginfo = []
        proxy_ping = {}
        fnode = []
        # 获取有延迟的node
        info_list = []
        progress = 0
        for n in nodename:
            resp = proxys.switchProxy(proxyName=n, proxyGroup=proxy_group,clashPort=api_port)
            cl = collector.Collector(n)
            print("切换节点:  ",n)
            nodeinfo  = await cl.start(n,api_port,proxy="http://127.0.0.1:{}".format(port))
            nodeinfo['类型'] = newnode_type[progress]
            info_list.append(nodeinfo)
            p_text = "%.2f" % (progress / len(nodename) * 100)
            progress += 1
            if progress %5 == 0:
                await client.edit_message_text(
                    chat_id=chat_id,
                    message_id=bakmsg_id,
                    text="╰(*°▽°*)╯流媒体测试进行中...\n\n" +
                         "当前进度:  " + p_text + " %  [ "+str(progress) +"/"+ str(len(nodename)) +"]"
                    )  # 实时反馈进度
        # 关闭进程
        subp.kill()
        progress = 0
        new_y = []
        # 过滤None值
        for info in info_list:
            print(info)
            if info['netflix1'] =='解锁':
                if info['Netflix2'] =='解锁':
                    info['Netflix'] = '解锁'
                else:
                    info['Netflix'] = '自制'
            else:
                info['Netflix'] = '失败'
        new_data = sorted(info_list, key=lambda i: i["HTTPS Ping"])
        nodename = [i['节点名称'] for i in new_data]
        nodetype = [i['类型'] for i in new_data]
        nodeping1 = [i['CLASH CHECK'] for i in new_data]
        nodeping2 = [i['HTTPS Ping'] for i in new_data]

        nodedalay1 = []
        for i in nodeping1:
            if i == 9999:
                i = -1
            delay = str(i) + 'ms'
            nodedalay1.append(delay)
        nodedalay2 = []
        usf_node = len(nodename)
        for i in nodeping2:
            if i == 9999:
                i = -1
                usf_node = usf_node-1
            delay = str(i) + 'ms'
            nodedalay2.append(delay)
        yt = [i['YouTube'] for i in new_data]
        nfx = [i['Netflix'] for i in new_data]
        disney = [i['Disney'] for i in new_data]
        info = {}
        info.update({'类型': nodetype})
        info.update({'CLASH CHECK': nodedalay1})
        info.update({'HTTPS Ping': nodedalay2})
        info.update({'Youtube': yt})
        info.update({'Netflix': nfx})
        info.update({'Disney': disney})
        wtime = "%.1f" % float(time.time() - s1)
        alive = str(usf_node) + '/' + str(len(nodename))
        book_dict = {}
        book_dict.update({'alive': alive})
        book_dict.update({'color': color})
        book_dict.update({'path_front': front})
        book_dict.update({'tasktime': wtime})
        book_dict.update({'taskname': "%s-可乐瓶子--流媒体测试"%taskname})
        book_dict.update({'thread_num': 8})
        book_dict.update({'timeout': 5})
        book_dict.update({'sort': 'Ping'})
        c1 = ExportResult(nodename, info, book_dict)
        export_time = c1.exportAsPng()
        # 计算测试消耗时间
        # 生成图片
        # 发送回TG
        with async_timeout.timeout(15):
            if len(nodename) > 35:
                await client.send_document(
                    chat_id=chat_id,
                    document=r"./results/result-{}.png".format(export_time),
                    caption="⏱️总共耗时: {}s".format(wtime)
                )
            else:
                await client.send_photo(
                    chat_id=chat_id,
                    photo=r"./results/result-{}.png".format(export_time),
                    caption="⏱️总共耗时: {}s".format(wtime)
                )
    except RPCError as r:
        print(r)
        await client.edit_message_text(
            chat_id=msgchat_id,
            message_id=bakmsg_id,
            text="出错啦"
        )
    except KeyboardInterrupt:
        await client.edit_message_text(
            chat_id=msgchat_id,
            message_id=bakmsg_id,
            text="程序已被强行中止"

        )
        subp.kill()
