'''
url='https://gwpre.sina.cn/interface/fymap2020_data.json?callback=_hbApi_data&=1584449791690' # 每天新增数据
data= getData(url)
s = data.encode('utf-8').decode('unicode_escape')#unicode码转中文
print(s)


'''



import requests,json,os,time
#定义一个获取数据的函数，参数为url
def getData(url):
    #模拟请求头
    headers={"user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)  Chrome/63.0.3239.132 Safari/537.36"}
    requests.packages.urllib3.disable_warnings()#跳过安全警告

    #使用requests库的get方法，获得消息对象r
    r = requests.get(url,headers=headers)
    try:
        #设置消息对象的编码方式为原网页的显式编码
        r.encoding= r.apparent_encoding
        #提取消息对象中的text文本内容，就是想要的数据
        result=r.text
    except:
        print("error")
    return result
timeStamp=time.time()#10位的时间戳
timeStamps=int(round(timeStamp*1000))#13位的时间戳
url = 'https://gwpre.sina.cn/interface/fymap2020_data.json?_={}'.format(timeStamps)  #1584449791690是时间戳   所有数据

datas= getData(url)          #获得数据，不过是字符串形式的。
str_data=datas.encode('utf-8').decode('unicode_escape')#unicode转换为字符串
data = json.loads(str_data, strict=False)['data']#将字符串转换为相应对象(相应对象指数据像什么类型就转换为什么类型) 后面的是去键对应的值
'''
    方法二
    data_dict=json.loads(datas)  #将字符串转换为字典对象
    d = data_dict['data']   #打印键为data的内容
'''


# print(data)
print("当前记录时间:{} 国内累计确诊人数{} 国内死亡人数{} 现存疑似人数{} 累计治愈人数{} 现存确诊人数{} 现存重症人数{}".format(data['cachetime'],data['gntotal'],data['deathtotal'],data['sustotal'],data['curetotal'],data['econNum'],data['heconNum']))
#当前记录时间:2023-01-23 17:37:42 国内累计确诊人数9481608 国内死亡人数31432 现存疑似人数3 累计治愈人数464712 现存确诊人数8985464 现存重症人数44


# print(data['add_daily'])#国内每天新增

#各省当前统计
# print(len(data['list']))
for i in data['list']:
    province_data=[i['name'],i['value'],i['econNum'],i['deathNum'],i['cureNum']]#省份名,累计确诊,现存确诊,死亡,治愈
    print(province_data)
    # for j in i['city']:
    #     city_data=[j['name'],j['conNum'],j['cureNum'],j['deathNum']]#城市名,累计确诊,治愈(较昨日),累计死亡
        # print(city_data)
    # print()

#国外各国累计
# print(data['othertotal'],len(data['othertotal']))
abroadTotal=[data['othertotal']['certain'],data['othertotal']['die'],data['othertotal']['recure'],]#国外累计数据   累计确诊,累计死亡,累计治愈

#国外各国统计
# print(data['otherlist'],len(data['otherlist']))
for i in data['otherlist']:
    abroad_data=[i['name'],i['conNum'],i['deathNum'],i['cureNum'],i['conadd']]#国家名,累计确诊,死亡,治愈,新增

#国外历史统计
# print(data['otherhistorylist'],len(data['otherhistorylist']))#国外历史统计
# for i in data['otherhistorylist']:
    # print(i)

#国内历史统计
# print(data['historylist'],len(data['historylist']))#国外历史统计
# for i in data['historylist']:
#     print(i)

print("++++++++++++++++++++++++++++++++++++++++++++")
#全世界统计(含中国)
print(data['worldconNum'],i['deathNum'],i['econNum'])#国家，累计治愈,累计确诊,累计死亡,现存确诊list'],len(data['worldlist']))
# for i in data['worldlist']:
#     if i['name']=='中国':
#         print(i['name'],i['cureNum'],i['value'],i['deathNum'],i['econNum'])#国家，累计治愈,累计确诊,累计死亡,现存确诊
#     else:
#         print(i['name'],i['cureNum'],i['