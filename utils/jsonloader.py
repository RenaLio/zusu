import json

def user_loader():
    try:
        with open('./logs/master.json', 'r',encoding="utf-8") as fp:
            json_data = json.load(fp)
        return json_data
    except:
        json_data = {}       
        return json_data

def user_reloader(userdict:dict):
    '''
    master.json只负责写入,不重新读取,每次启动时都会先 `user_loader`
    '''
    with open('./logs/master.json', 'w',encoding="utf-8") as f:
        data = json.dump(userdict,f,ensure_ascii=False)

def task_loader():
    try:
        with open('./logs/task_name.json', 'r',encoding="utf-8") as fp:
            json_data = json.load(fp)
        return json_data
    except:
        json_data = {}       
        return json_data

def task_reloader(taskdict:dict):
    '''
    master.json只负责写入,不重新读取,每次启动时都会先 `task_loader`
    '''
    with open('./logs/task_name.json', 'w',encoding="utf-8") as f:
        data = json.dump(taskdict,f,ensure_ascii=False)

def user_list(userdict:dict):
    user_list = []
    for k in userdict:
        user_list.append(k)
    return user_list

def get_list(taskdict:dict):
    name_list = []
    url_list = []
    for k,v in taskdict.items():
        user_list.append(k)
        url_list.append(v)
    return name_list,url_list

