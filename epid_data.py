import requests,json,os,time,datetime
from translate import Translator
def getData(time):
    #模拟请求头
    url = 'https://gwpre.sina.cn/interface/fymap2020_data.json?_={}'.format(time)  # 1584449791690是时间戳   所有数据
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
        print("数据获取失败")
    else:
        str_data = result.encode('utf-8').decode('unicode_escape')  # unicode转换为字符串
        data = json.loads(str_data, strict=False)['data']  # 将字符串转换为相应对象(相应对象指数据像什么类型就转换为什么类型) 后面的是去键对应的值
    return data

time=int(round(time.time()*1000))
# print(getData(time))

def getDomestic():#当前记录时间:2023-03-03 20:30:43 国内累计确诊人数9481608 国内死亡人数31432 现存疑似人数3 累计治愈人数464712 现存确诊人数8985464 现存重症人数44
    data=getData(time)

    res=[]
    ls=[data['cachetime'],data['gntotal'],data['deathtotal'],data['sustotal'],data['curetotal'],data['econNum'],data['heconNum']]
    lz=['当前记录时间','国内累计确诊人数','国内死亡人数','现存疑似人数','累计治愈人数','现存确诊人数','现存重症人数']
    print(ls,lz)
    for i in range(len(ls)):
        dict = {}
        dict['name']=lz[i]
        dict['value']=ls[i]
        res.append(dict)
    del res[0]
    return res
print("当前记录时间:{} 国内累计确诊人数{} 国内死亡人数{} 现存疑似人数{} 累计治愈人数{} 现存确诊人数{} 现存重症人数{}".format(getData(time)['cachetime'],getData(time)['gntotal'],getData(time)['deathtotal'],getData(time)['sustotal'],getData(time)['curetotal'],getData(time)['econNum'],getData(time)['heconNum']))




def getHuBei():
    ls=[]
    data=getData(time)
    for i in data['list']:
        if i['name']=='湖北':
            for j in i['city']:
                if j['name']!='境外输入':
                    city_data = [j['name'], j['conNum'], j['cureNum'], j['deathNum']]  # 城市名,累计确诊,治愈(较昨日),累计死亡
                    ls.append(city_data)
    return ls

def getChina():
    ls=[]
    data=getData(time)
    for i in data['list']:
        province_data = [i['name'], i['value'], i['econNum'], i['deathNum'], i['cureNum']]  # 省份名,累计确诊,现存确诊,死亡,治愈
        ls.append(province_data)
    return ls



def getWorld():
    ls=[]
    english_name = ['China', 'Denmark', 'Israel', 'Iraq', 'Russia', 'Croatia', 'Iceland', 'Canada', 'Ireland',
                    'North Macedonia', 'Botswana', 'India', 'Ecuador', 'Colombia', 'San Marino', 'Egypt', 'Mexico',
                    'Austria', 'Nigeria', 'Nepal', 'Pakistan', 'Bahrain', 'Brazil', 'Greece', 'Germany', 'Norway',
                    'Monaco', 'Sri Lanka', 'New Zealand', 'Cambodia', 'Georgia', 'Belgium', 'France', 'Thailand',
                    'Australia', 'Estonia', 'Sweden', 'Switzerland', 'Belarus', 'Kuwait', "Cote d'Ivoire", 'Lithuania',
                    'Romania', 'Finland', 'United Kingdom', 'Netherlands', 'Philippines', 'Spain', 'Vietnam',
                    'Azerbaijan', 'Afghanistan', 'Algeria', 'Oman', 'United Arab Emirates', 'Malaysia', 'Lebanon',
                    'Korea', 'Iran', 'Italy', 'Singapore', 'Japan', 'Diamond Princess', 'United States', 'Czech Rep',
                    'Indonesia', 'Qatar', 'Dominica', 'Luxembourg', 'Portugal', 'Armenia', 'Jordan', 'Andorra',
                    'Senegal', 'Saudi Arabia', 'Tunisia', 'Latvia', 'Morocco', 'Ukraine', 'Argentina', 'Chile',
                    'Poland', 'Hungary', 'Slovenia', 'Bosnia and Herzegovina', 'South Africa', 'French Guiana',
                    'Palestine', 'Bhutan', 'Cameroon', 'The Vatican', 'Serbia', 'Slovakia', 'Peru', 'Togo',
                    'Principality of Liechtenstein', 'Costa Rica', 'Malta', 'Maldives', 'Paraguay', 'Moldova', 'Brunei',
                    'Bangladesh', 'Bulgaria', 'Albania', 'Cyprus', 'Burkina Faso', 'Mongolia', 'Panama', 'Turkey',
                    'Jamaica', 'Bolivia', 'Honduras', 'Guyana', 'Cuba', 'Ghana', 'Gabon', 'Trinidad and Tobago',
                    'Kenya', 'Kazakhstan', 'Ethiopia', 'Guinea', 'S. Sudan', 'Venezuela', 'Uruguay', 'Guatemala',
                    'Antigua and Barbuda', 'Suriname', 'Mauritania', 'Eswatini', 'Rwanda', 'Namibia',
                    'Eq Guinea', 'Seychelles', 'Central African Rep.', 'Uzbekistan', 'Congo',
                    'Dem. Rep. Congo', 'Bahamas', 'Liberia', 'Tanzania', 'Somalia', 'Benin', 'Libya',
                    'Montenegro', 'Gambia', 'Barbados', 'Kyrgyzstan', 'Zambia', 'Mauritius', 'Fiji', 'Nicaragua',
                    'El Salvador', 'Chad', 'Niger', 'Haiti', 'Cape Verde', 'Madagascar', 'Zimbabwe', 'Papua New Guinea',
                    'Timor-Leste', 'Uganda', 'Eritrea', 'Mozambique', 'Syria', 'Dominica', 'Ruby Princess', 'Myanmar',
                    'Belize', 'Lao PDR', 'Mali', 'Guinea-Bissau', 'Angola', 'Turks and Caicos Islands',
                    'Saint Kitts and Nevis', 'Montserrat', 'Anguilla', 'Saint Lucia', 'Grenada', 'New Caledonia',
                    'Aruba', 'French Polynesia', 'Gibraltar', 'Martinique', 'Sierra Leone', 'Burundi', 'Malawi',
                    'Djibouti', 'Sao Tome and Principe', 'Sudan', 'Yemen', 'Saint Vincent', 'W. Sahara',
                    'Comoros', 'Tajikistan', 'Lesotho', 'Puerto Rico', 'Samoa', 'Dem. Rep. Korea']
    count=0
    data=getData(time)
    # print(data)
    for i in data['worldlist']:
        if i['name'] == '中国' or count==0:
            ls.append([i['name'], i['cureNum'], i['value'], i['deathNum'], i['econNum'],english_name[count]])  # 国家，累计治愈,累计确诊,累计死亡,现存确诊
        elif count>len(english_name):
            break

        else:
            ls.append([i['name'], i['cureNum'], i['conNum'], i['deathNum'], i['econNum'],english_name[count]])  # 国家，累计治愈,累计确诊,累计死亡,现存确诊
        count += 1
    return ls


# print("world:",getWorld())

def covert(char):  #英汉转换函数
    t=Translator(from_lang="chinese",to_lang="english")
    return t.translate(char)
# print(covert('圣文森特岛'))

a=['中国', '丹麦', '以色列', '伊拉克', '俄罗斯', '克罗地亚', '冰岛', '加拿大', '爱尔兰', '北马其顿', '博茨瓦纳', '印度', '厄瓜多尔', '哥伦比亚', '圣马力诺', '埃及', '墨西哥', '奥地利', '尼日利亚', '尼泊尔', '巴基斯坦', '巴林', '巴西', '希腊', '德国', '挪威', '摩纳哥', '斯里兰卡', '新西兰', '柬埔寨', '格鲁吉亚', '比利时', '法国', '泰国', '澳大利亚', '爱沙尼亚', '瑞典', '瑞士', '白俄罗斯', '科威特', '科特迪瓦', '立陶宛', '罗马尼亚', '芬兰', '英国', '荷兰', '菲律宾', '西班牙', '越南', '阿塞拜疆', '阿富汗', '阿尔及利亚', '阿曼', '阿联酋', '马来西亚', '黎巴嫩', '韩国', '伊朗', '意大利', '新加坡', '日本', '钻石公主号', '美国', '捷克', '印度尼西亚', '卡塔尔', '多米尼加', '卢森堡', '葡萄牙', '亚美尼亚', '约旦', '安道尔', '塞内加尔', '沙特阿拉伯', '突尼斯', '拉脱维亚', '摩洛哥', '乌克兰', '阿根廷', '智利', '波兰', '匈牙利', '斯洛文尼亚', '波黑', '南非', '法属圭亚那', '巴勒斯坦', '不丹', '喀麦隆', '梵蒂冈', '塞尔维亚', '斯洛伐克', '秘鲁', '多哥', '列支敦士登公国', '哥斯达黎加', '马耳他', '马尔代夫', '巴拉圭', '摩尔多瓦', '文莱', '孟加拉国', '保加利亚', '阿尔巴尼亚', '塞浦路斯', '布基纳法索', '蒙古国', '巴拿马', '土耳其', '牙买加', '玻利维亚', '洪都拉斯', '圭亚那', '古巴', '加纳', '加蓬', '特立尼达和多巴哥', '肯尼亚', '哈萨克斯坦', '埃塞俄比亚', '几内亚', '苏丹', '委内瑞拉', '乌拉圭', '危地马拉', '安提瓜和巴布达', '苏里南', '毛里塔尼亚', '斯威士兰', '卢旺达', '纳米比亚', '赤道几内亚', '塞舌尔', '中非共和国', '乌兹别克斯坦', '刚果（布）', '刚果（金）', '巴哈马', '利比里亚', '坦桑尼亚', '索马里', '贝宁', '利比亚', '黑山', '冈比亚', '巴巴多斯', '吉尔吉斯斯坦', '赞比亚', '毛里求斯', '斐济', '尼加拉瓜', '萨尔瓦多', '乍得', '尼日尔', '海地', '佛得角', '马达加斯加', '津巴布韦', '巴布亚新几内亚', '东帝汶', '乌干达', '厄立特里亚', '莫桑比克', '叙利亚', '多米尼克', '红宝石公主号', '缅甸', '伯利兹', '老挝', '马里', '几内亚比绍', '安哥拉', '特克斯和凯科斯群岛', '圣基茨和尼维斯', '蒙特塞拉特岛', '安圭拉', '圣卢西亚', '格林纳达', '新喀里多尼亚', '阿鲁巴', '法属波利尼西亚', '直布罗陀', '马提尼克岛', '塞拉利昂', '布隆迪', '马拉维', '吉布提', '圣多美和普林西比', '南苏丹', '也门', '圣文森特岛', '西撒哈拉', '科摩罗', '塔吉克斯坦', '莱索托', '波多黎各', '萨摩亚', '朝鲜']

# c=['China', 'Denmark', 'Israel', 'Iraq', 'Russia', 'Croatia', 'Iceland', 'Canada', 'Ireland', 'North Macedonia.', 'Botswana', 'India', 'Ecuador', 'Columbia', 'San Marino', 'Egypt', 'Mexico', 'Austria', 'Nigeria', 'Nepal', 'Pakistan', 'Bahrain', 'Brazil', 'Greece', 'Germany', 'Norway', 'Monaco', 'Sri Lanka', 'New Zealand', 'Cambodia', 'Georgia', 'Belgium', 'France', 'Thailand', 'Australia', 'Estonia', 'Sweden', 'Switzerland', 'Belarus', 'Kuwait', 'CotedIvoire', 'Lithuania', 'Romania', 'Finland', 'United Kingdom', 'Netherlands', 'Philippines', 'Spain', 'Vietnam', 'Azerbaijan', 'Afghanistan', 'Algeria', 'Oman', 'United Arab Emirates', 'Malaysia', 'Lebanon', 'South Korea', 'Iran', 'Italy', 'Singapore', 'Japan', 'Diamond Princess', 'USA', 'Czech Republic', 'Indonesia', 'Qatar', 'Dominica', 'Luxembourg', 'Portugal', 'Armenia', 'Jordan', 'Andorra', 'Senegal', 'Saudi Arabia', 'Tunisia', 'Latvia', 'Morocco', 'Ukraine', 'Argentina', 'Chili', 'Poland', 'Hungary', 'Slovenia', 'Bosnia and Herzegovina', 'South Africa', 'French Guiana', 'Palestine', 'Bhutan', 'Cameroon', 'The Vatican', 'Serbia', 'Slovakia', 'Peru', 'Togo', 'Principality of Liechtenstein', 'Costa Rica', 'Malta', 'Maldives', 'Paraguay', 'Moldova', 'Brunei', 'Bangladesh', 'Bulgaria', 'Albania', 'Cyprus', 'Burkina Faso', 'Mongolia', 'Panama', 'Turkey', 'Jamaica', 'Bolivia', 'Honduras', 'Guyana', 'Cuba', 'Ghana', 'Gabon', 'Trinidad and Tobago', 'Kenya', 'Kazakhstan', 'Ethiopia', 'Guinea', 'Sudan', 'Venezuela', 'Uruguay', 'Guatemala', 'Antigua and Barbuda', 'Suriname', 'Mauritania', 'Swaziland', 'Rwanda', 'Namibia', 'Equatorial Guinea Gabon', 'Seychelles', 'Central African Republic', 'Uzbekistan', 'Congo (Brazzaville)', 'Congo (Kinshasa)', 'Bahamas', 'Liberia', 'Tanzania', 'Somalia', 'Benin', 'Libya', 'Montenegro', 'Gambia', 'Barbados', 'Kyrgyzstan', 'Zambia', 'Mauritius', 'Fiji', 'Nicaragua', 'El Salvador', 'Chad', 'Niger', 'Haiti', 'Cape Verde', 'Madagascar', 'Zimbabwe', 'Papua New Guinea', 'East Timor', 'Uganda', 'Eritrea', 'Mozambique', 'Syria', 'Dominica','Ruby Princess''Myanmar', 'Belize', 'Laos', 'Mali', 'Guinea-Bissau', 'Angola', 'Turks and Caicos Islands', 'Saint Kitts and Nevis', 'Montserrat', 'Anguilla', 'Saint Lucia', 'Grenada', 'New Caledonia', 'Aruba','French Polynesia', 'Gibraltar', 'Martinique', 'Sierra Leone', 'Burundi', 'Malawi', 'Djibouti', 'Sao Tome and Principe', 'South Sudan', 'Yemen', 'Saint Vincent', 'Western Sahara', 'Comoros', 'Tajikistan', 'Lesotho', 'Puerto Rico', 'Samoa', 'North Korea']
d=['China', 'Denmark', 'Israel', 'Iraq', 'Russia', 'Croatia', 'Iceland', 'Canada', 'Ireland', 'North Macedonia', 'Botswana', 'India', 'Ecuador', 'Colombia', 'San Marino', 'Egypt', 'Mexico', 'Austria', 'Nigeria', 'Nepal', 'Pakistan', 'Bahrain', 'Brazil', 'Greece', 'Germany', 'Norway', 'Monaco', ' Sri Lanka', 'New Zealand', 'Cambodia', 'Georgia', 'Belgium', 'France', 'Thailand', 'Australia', 'Estonia', 'Sweden', 'Switzerland', 'Belarus', 'Kuwait', 'CôtedIvoire', 'Lithuania', 'Romania', 'Finland', 'United Kingdom', 'Netherlands', 'Philippines', 'Spain', 'Vietnam', 'Azerbaijan', 'Afghanistan', 'Algeria', 'Oman', 'United Arab Emirates', 'Malaysia', 'Lebanon', 'South Korea', 'Iran', 'Italy', 'Singapore', 'Japan', 'Diamond Princess', 'USA', 'Czech Republic', 'Indonesia', 'Qatar', 'Dominica', 'Luxembourg', 'Portugal', 'Armenia', 'Jordan', 'Andorra', 'Senegal', 'Saudi Arabia', 'Tunisia', 'Latvia', 'Morocco', 'Ukraine', 'Argentina', 'Chile', 'Poland', 'Hungary', 'Slovenia', 'Bosnia and Herzegovina', 'South Africa', 'French Guiana', 'Palestine', 'Bhutan', 'Cameroon', 'The Vatican', 'Serbia', 'Slovakia', 'Peru', 'Togo', 'Principality of Liechtenstein', 'Costa Rica', 'Malta', 'Maldives', 'Paraguay', 'Moldova', 'Brunei', 'Bangladesh', 'Bulgaria', 'Albania', 'Cyprus', 'Burkina Faso', 'Mongolia', 'Panama', 'Turkey', 'Jamaica', 'Bolivia', 'Honduras', 'Guyana', 'Cuba', 'Ghana', 'Gabon', 'Trinidad and Tobago', 'Kenya', 'Kazakhstan', 'Ethiopia', 'Guinea', 'Sudan', 'Venezuela', 'Uruguay', 'Guatemala', 'Antigua and Barbuda', 'Suriname', 'Mauritania', 'Eswatini', 'Rwanda', 'Namibia', 'Equatorial Guinea', 'Seychelles', 'Central African Republic', 'Uzbekistan', 'Congo', 'Democratic Republic of the Congo', 'Bahamas', 'Liberia', 'Tanzania', 'Somalia', 'Benin', 'Libya', 'Montenegro', 'Gambia', 'Barbados', 'Kyrgyzstan', 'Zambia', 'Mauritius', 'Fiji', 'Nicaragua', 'El Salvador', 'Chad', 'Niger', 'Haiti', 'Cape Verde', 'Madagascar', 'Zimbabwe', 'Papua New Guinea', 'Timor-Leste', 'Uganda', 'Eritrea', 'Mozambique', 'Syria', 'Dominica', 'Ruby Princess', 'Myanmar', 'Belize', 'Laos', 'Mali', 'Guinea-Bissau', 'Angola', 'Turks and Caicos Islands', 'Saint Kitts and Nevis', 'Montserrat', 'Anguilla', 'Saint Lucia', 'Grenada', 'New Caledonia', 'Aruba', 'French Polynesia', 'Gibraltar', 'Martinique', 'Sierra Leone', 'Burundi', 'Malawi', 'Djibouti', 'Sao Tome and Principe', 'South Sudan', 'Yemen', 'Saint Vincent', 'Western Sahara', 'Comoros', 'Tajikistan', 'Lesotho', 'Puerto Rico', 'Samoa', 'North Korea']



# for i in c:



# print(getWorld())
