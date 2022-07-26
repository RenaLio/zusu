from PIL import Image,ImageDraw,ImageFont
import time
import logging
logger = logging.getLogger("Sub")
import warnings
warnings.filterwarnings('ignore')


__version__ = '2.2.0'
save_path  = './results'

class ExportResult:
    '''
    nodename:['HKcentre','JP_5']
    info:{
        "xx1":['1ms','99ms']
        "yt":['N/A','失败']
        ...
    }
    iconfig:{
        图片配置信息
        'version':
        'taskname'
        'timeout'
    }
    '''
    def __init__(self,nodename: list, info: dict,iconfig: dict):

        self.version = __version__
        self.nodename = nodename
        self.info = info
        self.iconfig = iconfig
        self.nodetype = info['类型']
        self.nodenum = len(nodename)
        self.front = iconfig['path_front']
        self.front_size = 30
        self.__font = ImageFont.truetype(self.front,self.front_size)
        self.color = iconfig['color']
        self.tasktime = iconfig['tasktime']
        self.taskname = iconfig['taskname']
        self.thread_num = iconfig['thread_num']
        self.timeout = iconfig['timeout']
        self.sort = iconfig['sort']
        self.alive = iconfig['alive']
    
    def get_height(self):
        nodenum = self.nodenum+4
        img_height = nodenum * 40
        return img_height


    def get_key(self):  #得到测试项名称
        key_list = []
        for i in self.info:
            key_list.append(i)
        return key_list
    

    def key_value(self):            #比较测试项名称和测试项结果的长度
        key_list = self.get_key()   #得到每个测试项绘图的大小[100,80]
        width_list = []
        max_width = 0
        for i in key_list:
            max_width = self.text_width(i)
            max_width2 = self.text_maxwidth(self.info[i])
            max_width = max(max_width,max_width2)
            max_width = max_width+15
            width_list.append(max_width)
        return width_list           #测试项列的大小

    def text_width(self, text):         #得到字符串在图片中的绘图长度
        font = self.__font
        draw = ImageDraw.Draw(Image.new("RGB",(1,1),(255,255,255)))
        textSize = draw.textsize(text, font=font)[0]
        return textSize
    
    def text_maxwidth(self,strlist):    #得到列表中最长字符串的绘图长度
        font = self.__font
        draw = ImageDraw.Draw(Image.new("RGB",(1,1),(255,255,255)))
        max_width = 0
        for i in strlist:
            max_width = max(max_width,draw.textsize(i,font=font)[0])
        return max_width

    def get_width(self):        # image_width
        img_width = 100         #序号
        nodename_width=self.text_maxwidth(self.nodename)
        name_wodth = self.text_width('节点名称')
        nodename_width = max(nodename_width,name_wodth,500)
        nodename_width = nodename_width+40
        infolist_width = self.key_value()
        info_width = 0
        for i in infolist_width:
            info_width = info_width+i
        img_width =img_width +nodename_width+info_width
        return img_width,nodename_width,infolist_width

    def get_mid(self,start,end,str_name):
        mid_xpath = (end-start)/2
        strname_width = self.text_width(str_name)
        xpath = mid_xpath-strname_width/2
        xpath = xpath +start
        # print(xpath)
        return xpath
    

    def exportAsPng(self): 
        fnt = ImageFont.truetype(self.front, self.front_size)
        image_width,nodename_width,info_list = self.get_width()
        print('image_width:%s'%image_width)
        image_height = self.get_height()
        key_list = self.get_key()
        img = Image.new("RGB", (image_width, image_height), (255, 255, 255))
        # pilmoji = Pilmoji(img)  # emoji表情修复
        # 绘制色块
        bkg = Image.new('RGB', (image_width, 80), (234, 234, 234))  # 首尾部填充
        img.paste(bkg,(0,0))
        img.paste(bkg,(0,image_height-80))
        idraw = ImageDraw.Draw(img)
        '''
        :绘制标题栏与结尾栏
        '''
        idraw.text((self.get_mid(0,image_width,self.taskname), 5), self.taskname, font=fnt, fill=(0, 0, 0))
        # idraw.text((self.getBasePos(image_width, self.taskname), 4),self.taskname,font=fnt,fill=(0,0,0))
        export_time = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())  # 输出图片的时间
        export_time1 = time.strftime("%Y-%m-%dT%H-%M-%S", time.localtime())  # 文件动态命名
        list2 = ["版本:%s 耗时:%ss 线程:%s 时长:%s 概要:%s 排序:%s "
                %(self.version,self.tasktime,self.thread_num,self.timeout,self.alive,self.sort),
                "测试时间: %s  测试结果仅供参考,以实际情况为准"%export_time]
        idraw.text((10, image_height-75), text=list2[0], font=fnt, fill=(0, 0, 0))  # 版本信息
        idraw.text((10, image_height-35), text=list2[1], font=fnt, fill=(0, 0, 0))  # 测试时间
        '''
        :绘制标签
        '''
        idraw.text((20, 40), '序号', font=fnt, fill=(0, 0, 0))  # 序号
        idraw.text((self.get_mid(100,nodename_width+100,'节点名称'),40), '节点名称', font=fnt, fill=(0, 0, 0))  # 节点名称
        start_x = 100+nodename_width
        m = 0
        for i in info_list:
            x = start_x
            end =start_x+i
            # print(x,end)
            idraw.text((self.get_mid(x,end,key_list[m]), 40), key_list[m], font=fnt, fill=(0, 0, 0))
            # print(self.get_mid(x,end,key_list[m]))
            start_x =end
            m = m+1
        '''
        :内容填充
        '''
        k =0
        for t in range(len(self.nodename)):
            # 序号
            idraw.text((self.get_mid(0,100,str(t+1)),(t+2)*40),str(t+1),
                    font=fnt, fill=(0, 0, 0))
            # 节点名称
            idraw.text((105,(t+2)*40),self.nodename[t],
                    font=fnt, fill=(0, 0, 0))
            width = 100+nodename_width
            i = 0
            k =k+1
            for tt in key_list:
                idraw.rectangle([(width,(t+2)*40+3),(width+info_list[i],(t+3)*40)],self.get_color(tt,self.info[tt][t])
                )
                idraw.text((self.get_mid(width,width+info_list[i],self.info[tt][t]),(t+2)*40),self.info[tt][t],
                    font=fnt, fill=(0, 0, 0))
                width = width+info_list[i]
                i =i+1
        '''
        :添加横竖线条
        '''
        # 绘制横线
        for t in range(self.nodenum+3):
            idraw.line([(0, 40 * (t + 1)), (image_width, 40 * (t + 1))], fill=(0, 0, 0),width=2)
        # 绘制竖线
        idraw.line([(100, 80), (100, image_height-80)], fill=(0, 0, 0),width=2)
        start_x = 100+nodename_width
        for i in info_list:
            x = start_x
            end = start_x+i
            idraw.line([(x, 80), (x, image_height-80)], fill=(0, 0, 0),width=2)
            start_x =end
        print(export_time1)
        img.save(r'./results/result-{0}.png'.format(export_time1))
        return export_time1

    def get_color(self,key_text: str,value_text: str):
        if 'Ping' in key_text:
            value_text = value_text.strip('ms')
            if int(value_text)>0 and int(value_text)<150:
                cR = self.color['ping']['s1'][0]
                cG = self.color['ping']['s1'][1]
                cB = self.color['ping']['s1'][2]
            elif int(value_text)>=150 and int(value_text)<350:
                cR = self.color['ping']['s2'][0]
                cG = self.color['ping']['s2'][1]
                cB = self.color['ping']['s2'][2]
            elif int(value_text)>=350 and int(value_text)<600:
                cR = self.color['ping']['s3'][0]
                cG = self.color['ping']['s3'][1]
                cB = self.color['ping']['s3'][2]
            elif int(value_text)>=600 and int(value_text)<1500:
                cR = self.color['ping']['s4'][0]
                cG = self.color['ping']['s4'][1]
                cB = self.color['ping']['s4'][2]
            else:
                cR = self.color['ping']['s5'][0]
                cG = self.color['ping']['s5'][1]
                cB = self.color['ping']['s5'][2]
        # elif 'speed' in key_text:
        else:
            if '解锁' in value_text:
                cR = self.color['youtube']['s1'][0]
                cG = self.color['youtube']['s1'][1]
                cB = self.color['youtube']['s1'][2]
            elif 'N/A' in value_text:
                cR = self.color['youtube']['s2'][0]
                cG = self.color['youtube']['s2'][1]
                cB = self.color['youtube']['s2'][2]
            elif '失败' in value_text:
                cR = self.color['youtube']['s3'][0]
                cG = self.color['youtube']['s3'][1]
                cB = self.color['youtube']['s3'][2]
            elif '自制' in value_text:
                cR = self.color['youtube']['s4'][0]
                cG = self.color['youtube']['s4'][1]
                cB = self.color['youtube']['s4'][2]
            else:
                cR = 255
                cG = 255
                cB = 255
        try:
            return (cR,cG,cB)
        except:
            return (255,255,255)