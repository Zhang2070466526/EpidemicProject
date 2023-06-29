import json
import random
import requests
import openpyxl
import os

# url = "http://restapi.amap.com/v3/geocode/geo"
# data = {
#     'key': '72f6ca8cf3360e956e9eb66f9bac3b02', #需要替换为在高德地图开发者平台申请的key
#     'address': '恩施'
# }
# r = requests.post(url, data=data).json()
# # print(r['geocodes'][0]['location'],r['geocodes'][0]['city'])

def get_lat_lng(name):   #根据地名获取坐标
    url = "http://restapi.amap.com/v3/geocode/geo"
    data = {
    'key': '1dd8cb45548668a7f8245ebf99ed7ba3',  # 需要替换为在高德地图开发者平台申请的key
    'address': name
    }
    r = requests.post(url, data=data).json()
    return r
# print(get_lat_lng('襄阳市'))

with open("CampusModule/static/epid_json.json", 'r', encoding='utf-8') as load_f: #打开json文件
    load_dict = json.load(load_f)

filename = 'CampusModule/static/laglat.xlsx'
if not os.path.exists(filename):  #判断括号里的文件是否存在,不存在返回False
    wb = openpyxl.Workbook()  #创建一个excel文件
    wb.save(filename)  #指定路径,保存文件
wb = openpyxl.load_workbook(filename)  #打开该文件
sheet=wb.active#取第0个工作表
sheet.title="坐标"#工作表命名为表1
sheet.append(['序号','省份','地名', '经纬度','今日累计确诊'])#添加一行
for i in load_dict['features']:
    json_index=i['properties']['ranking']
    json_name=i["properties"]['prov']+i["properties"]['city']
    name=get_lat_lng(json_name)#经纬度
    print(json_index,name['geocodes'][0]['formatted_address'],name['geocodes'][0]['location'])
    sheet['A'+str(json_index+1)].value = json_index
    sheet['B'+str(json_index + 1)].value = i["properties"]['prov']#省份名
    sheet['C'+str(json_index+1)].value =i["properties"]['city'] #name['geocodes'][0]['formatted_address']#地名
    sheet['D'+str(json_index+1)].value = name['geocodes'][0]['location']#经纬度

wb.save(filename)   #指定路径,保存文件













a={
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [109.48699, 30.283114]
      },
      "properties": {
        "ranking": 1,
        "prov": "湖北省",
        "city": "恩施土家族苗族自治州",
        "mom": "-4.4%",
        "yoy": "-5.1%",
        "index": 2.367,
        "avg": 14.685,
        "lnglat": "109.48699,30.283114"
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [106.753669, 31.858809]
      },
      "properties": {
        "ranking": 2,
        "prov": "四川省",
        "city": "巴中市",
        "mom": "-2.9%",
        "yoy": "0.3%",
        "index": 2.113,
        "avg": 19.375,
        "lnglat": "106.753669,31.858809"
      }
    },
  ]
}

template= {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [106.753669, 31.858809]
      },
      "properties": {
        "ranking": 2,
        "prov": "四川省",
        "city": "巴中市",
        "mom": "-2.9%",
        "yoy": "0.3%",
        "index": 2.113,
        "avg": 19.375,
        "lnglat": "106.753669,31.858809"
      }
    },



