from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import BotCommand
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,
                            InlineKeyboardButton)
from utils.url2name import url2name
import threading
import asyncio
import yaml
import time
from utils.jsonloader import (user_loader,user_reloader,
                             task_loader,task_reloader,user_list,get_list)
from utils.pyqueue import Queue
from utils.Preprocessing import yaml_collect
# from utils.testurl import testurl
from utils.streamingtest import testurl
from config import config


config = config
# 如果是在国内环境，则需要代理环境以供程序连接上TG
proxies = {
    "scheme": "socks5",  # "socks4", "socks5" and "http" are supported
    "hostname": "127.0.0.1",
    "port": config['proxyport']
}
version = config['version']
admin = config['admin']     #list
master = user_loader()      #dict
task_config = task_loader()  #dict
gLock = threading.Lock()    #操作文件锁
task_queue = Queue()    #[url,task_name,message.chat.id,back_message]
progress = 0
print(type(task_queue))
print(type(task_queue.array))
# 你需要一个TG的session后缀文件，以下是session文件的名字，应形如 my_bot.session 为后缀。这个文件小心保管，不要泄露。
if not admin:
    print('检测到未设置超级管理')

if not config['proxyport']:
    app = Client("my_bot")
    print("配置已加载")
    print("程序已启动!")
else:
    app = Client("my_bot", proxy=proxies)
    print("配置已加载")
    print("程序已启动!")

@app.on_message(filters.command("help"))
async def help_command(client, message):
    text = "This is the /help command"
    await app.send_message(message.chat.id,text)


@app.on_message(filters.command("testurl"))
async def start_command(client, message):
    global task_queue
    USER_TARGET= user_list(master)
    try:
        if (message.from_user.id not in admin and
            str(message.from_user.id) not in USER_TARGET) :  # 如果不在名单是不会有权限的
                back_message = await message.reply("⚠️对不起，你没有权限，请联系超管对你使用 /grant 授权")
                await asyncio.sleep(5)
                try:
                    await app.delete_messages(message.chat.id, back_message.id, revoke=True)
                except:
                    await app.delete_messages(message.chat.id, back_message.id)
                return
    except:
        if str((message.sender_chat.id) not in USER_TARGET):
            back_message = await message.reply("⚠️对不起，你没有权限，请联系超管对你使用 /grant 授权")
        await asyncio.sleep(5)
        try:
            await app.delete_messages(message.chat.id, back_message.id, revoke=True)
        except:
            await app.delete_messages(message.chat.id, back_message.id)
        return

    # 获取名字 检查订阅输入
    url,task_name = url2name(message.text)
    if  not url:
        text = "❌ 请输入正确的订阅地址 🔙"
        back_message = await message.reply(text)
        await asyncio.sleep(5)
        try:
            await app.delete_messages(message.chat.id, back_message.id, revoke=True)
        except:
            await app.delete_messages(message.chat.id, back_message.id)
        return
    # 当前队列任务大于32
    if task_queue.length() > 3:
        text = "❌ 当前队列过长，请在一段时间后再次尝试尝试 😇~"
        back_message = await message.reply(text)
        await asyncio.sleep(5)
        try:
            await app.delete_messages(message.chat.id, back_message.id, revoke=True)
        except:
            await app.delete_messages(message.chat.id, back_message.id)
        return
    text = "🎇 '%s'任务请求已接受,前方排队: %s,请耐心等待..." %(task_name,task_queue.length())
    back_message = await message.reply(text)
    msgchat_id = message.chat.id
    msg_id = message.id
    bakmsg_id = back_message.id
    task_dict ={}
    task_dict.update({"url":url})
    task_dict.update({"task_name":task_name})
    task_dict.update({"msgchat_id":msgchat_id})
    task_dict.update({"msg_id": msg_id})
    task_dict.update({"bakmsg_id":bakmsg_id})
    task_dict.update({"task_type": 'test'})
    # 添加队列
    gLock.acquire() #加锁
    task_queue.push(task_dict)
    gLock.release() #释放锁
    ####################
    # 开始队列操作，进入测试项
    # 线程锁将导致其他所有线程阻塞
    #分布式准备
    global progress
    if progress == 0:
        progress = 1
        await app.send_message(message.chat.id, 'progress %s' % progress)
        await app.send_message(message.chat.id, task_queue.length())
        while not task_queue.is_Empty():
            await testurl(client,task_queue,config)
            gLock.acquire()  # 加锁
            task_queue.pop()
            gLock.release()  # 释放锁
            await app.send_message(message.chat.id, '出对列后队列长度为%s' % task_queue.length())
        progress = 0
    else:
        pass

@app.on_message(filters.command("test"))
async def help_command(client, message):
    text = "This is the /help command"
    await app.send_message(message.chat.id,text)
    print("This is the /help command")
    print(type(message))

@app.on_message(filters.command("grant"))
async def grant_command(client, message):
    global master
    global admin
    # print(message)
    if message.from_user.id in admin:
        if message.reply_to_message is None:
            return
        try:
            ungrant_id = int(message.reply_to_message.from_user.id)
        except AttributeError:
            ungrant_id = int(message.reply_to_message.sender_chat.id)
        masterid = str(ungrant_id)
        master.update({masterid:''})
        user_reloader(master)
        text = '管理员添加成功 🥳~'
        back_message = await message.reply(text)
        await asyncio.sleep(3)
        try:
            await app.delete_messages(message.chat.id, back_message.id, revoke=True)
        except:
            await app.delete_messages(message.chat.id, back_message.id)
    else:
        text = '🚫对不起你没有权限，请检查配置文件并重启'
        back_message = await message.reply(text)
        await asyncio.sleep(1.5)
        try:
            await app.delete_messages(message.chat.id, back_message.id, revoke=True)
        except:
            await app.delete_messages(message.chat.id, back_message.id)
                   
@app.on_message(filters.command("ungrant"))
async def help_command(client, message):
    global master
    global admin
    if message.from_user.id in admin:
        if message.reply_to_message is None:
            return
        try:
            ungrant_id = int(message.reply_to_message.from_user.id)
        except AttributeError:
            ungrant_id = int(message.reply_to_message.sender_chat.id)
        masterid = str(ungrant_id)
        try:
            master.pop(masterid)
            user_reloader(master)
            text = '管理员删除成功 😿~'
            back_message = await message.reply(text)
        except KeyError as e:
            text = '使用对象非管理员 😿~'
            back_message = await message.reply(text)
        await asyncio.sleep(3)
        try:
            await app.delete_messages(message.chat.id, back_message.id, revoke=True)
        except:
            await app.delete_messages(message.chat.id, back_message.id)
    else:

        text = '🚫对不起你没有权限，请检查配置文件并重启'
        back_message = await message.reply(text)
        await asyncio.sleep(1.5)
        try:
            await app.delete_messages(message.chat.id, back_message.id, revoke=True)
        except:
            await app.delete_messages(message.chat.id, back_message.id)



@app.on_message(filters.command("invite"))
async def help_command(client, message):
    text = "This is the /help command"
    await app.send_message(message.chat.id,text)
    print("This is the /help command")


@app.on_message(filters.command("inviteme"))
async def help_command(client, message):
    text = "This is the /help command"
    await app.send_message(message.chat.id,text)
    print("This is the /help command")

@app.on_message(filters.command("msg"))
async def help_command(client, message):
    text = "This message id is the %s "%message.id
    back_message = await app.send_message(message.chat.id,text)
    await asyncio.sleep(5)
    await back_message.edit("This back_message id is the %s "%back_message.id)
    await asyncio.sleep(5)
    try:
        await app.delete_messages(message.chat.id, back_message.id, revoke=True)
    except:
        await app.delete_messages(message.chat.id, back_message.id)


# async def raw(client, update, users, chats):
#     print(update)

app.run()




