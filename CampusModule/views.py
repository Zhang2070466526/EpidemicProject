import random, time,json,re,urllib,math,os,copy,openpyxl
from datetime import datetime,timedelta,date
import epid_data
import logging
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from django import forms
from django.shortcuts import render, redirect,HttpResponse
from CampusModule import models
from CampusModule.models import User,College,Class,HubeiData,ChinaData,WorldData,Notice,Teacher,Student,Filling,Itinerary,Admin_info
from django.views.decorators.csrf import csrf_exempt#用来免除csrf表单认证
from django.http import JsonResponse
from django.conf import settings

from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.cache import cache_page


logger =logging.getLogger('log')

# from rest_framework.views import APIView
# from rest_framework import serializers
# from rest_framework import status
# class AdminInfoSerializer(serializers.Serializer):
#     class Meta:
#         model = Teacher
#         fields = '__all__'
# class AdminInfoView(APIView):
#     def get(self, request):
#         # admin_info = Teacher.objects.all()
#         #     # .values_list(
#         # #     'info_admin__user_name',
#         # #     'info_teacher__teacher_user_name'
#         # # )
#         # print(admin_info)
#         admin_info={'message': 'Hello, Admin!'}
#         serializer = AdminInfoSerializers(instance=admin_info, many=True)
#         print(serializer.data)
#         return HttpResponse(serializer.data)







#orm
"""
A.objects.all();   #   select * from A
A.objects.get(id=1)  # select * from A where id=1
A.objects.filter(age__gte=20)  # select * from A where age>=20
A.objects.filter(id__in=[1,2,3]) # select * from A where id in (1,2,3)
A.objects.filter(name__icontains='A') # select * from A where name like '%A%'
A.objects.all()[:1]  # 
A.objects.all().order_by('-age') # select * from A order by age desc ;  
 
#查看执行的原生SQL
print(str(A.objects.filter(age__gte=20).order_by('-age').query))
 
 
# 返回新QuerySet API
A.objects.all().exclude(id=1)
A.objects.all().exclude(id=1).reverse()
A.objects.all().extra(select={"name":"nickname"})  # nickname as name 取别名
A.objects.all().only('nickname','age')   # 只查两个列
A.objects.all().select_related('B')    # 查询A时同时关联查询出B ,外键查询
A.objects.filter(age__lt=30).prefetch_related('C')  # 多对多关联查询
 

"""

path=r'C:\Users\1010000407\Desktop\毕设\EpidemicProject'
# nginx
def page_not_found(request):
    print("AAAAAAAAAAAAAAA",request.session.get("user_info"))
    if request.session.get("user_info"):
        return render(request, "index.html")
    else:
        print("=============")
        return redirect("campus/login/")


# avatar = User.objects.filter(id=1).values_list('avatar_file')
# avatar = avatar[0][0].split("static\\")[1]
# print(avatar)#头像


class UUFunc(object):
    def __init__(self):
       pass
    def UUget(self,request):
        self.id=request.session['info'].get('id')
        self.uu = User.objects.filter(id=self.id).values_list('user_name',flat=True).first()
        self.pwd=User.objects.filter(id=self.id).values_list('user_password',flat=True).first()
        avatar=User.objects.filter(id=self.id).values_list('avatar_file',flat=True).first()
        try:
            self.avatar = avatar.split("static\\")[1]
        except:
            self.avatar = 'img\\1.png'
        return_data={
            'uid':self.id,
            'uname':self.uu,
            'upwd':self.pwd,
            'avatar':self.avatar
        }
        return return_data  #个人信息组件



def base(request):
    # logger.info('This is an info message!!!!!!!!!!!!!!!!!!')
    # logger.warning('This is a warning message!')
    # logger.error('This is an error message!')

    # avatar=User.objects.filter(id=1).values_list('avatar_file')
    # avatar=avatar[0][0].split("static\\")[1]
    # global avatar
    # print(avatar)
    info = UUFunc().UUget(request)
    context={
        'uu': info['uname'],
        'avatar': info['avatar']
        # 'avatar':avatar,
        # 'permissions':'admin',权限
    }
    return render(request, 'base_zy.html',context)

class FatherModelForm(forms.ModelForm):#所有modelform的父类
    exclude_fields=[]#需要移除{'class':'form-control'}样式的字段
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for name,field in self.fields.items():#循环所有字段即fields=['notice_name','notice_content','notice_writer']#展示的字段
            if name in self.exclude_fields:
                continue
            if field.widget.attrs:#字段中原来有属性,保留原有属性
                field.widget.attrs['class']='form-control'
                field.widget.attrs['placeholder']=field.label
            else:#是覆盖原有属性,没有属性才增加
                field.widget.attrs={'class':'form-control','placeholder':field.label}

class DateInput(forms.DateInput):#自定义小部件
    input_type = 'date'

class Pagination(object):#分页组件
    def __init__(self,request,queryset,page_size=7,page_param='page_input'):
        query_dict = copy.deepcopy(request.GET)  # 虽然是拷贝，但是相当于新建了一个对象       拷贝的原因是不能对request.GET进行直接修改的
        query_dict._mutable = True  # True指请求可以被修改
        self.query_dict=query_dict
        self.page_param=page_param
        self.total_count=queryset.count()#总条数
        total_page_count,div=divmod(self.total_count,page_size)
        if div:
            total_page_count+=1
        self.total_page_count=total_page_count#总页码
        page=request.GET.get(self.page_param,'1')
        if page.isdecimal():#判断是否是十进制
            page=int(page)
            if int(page)>self.total_page_count:
                page=self.total_page_count
            elif page<=0:
                page=1
        else:
            page=1
        self.page=page#当前页码
        self.page_size=page_size
        self.start= (page - 1) * page_size
        self.end= page_size * page  # 0,7  7,14  14,21
        self.page_queryset=queryset[self.start:self.end]#分完页的数据

    def html(self):
        # page_prev_next = '''<a href='?{}' class ='g-actions-button g-actions-button-pager'> <i class ='fa fa-fw fa-caret-left right-4'></i>Prev</a>
        #               <a href='?{}' class='g-actions-button g-actions-button-pager g-table-list-pager'>Next<i class='fa fa-fw fa-caret-right left-4'></i></a>'''\
        #     .format(self.page - 1 if self.page - 1 >= 1 else self.page, self.page + 1 if self.page + 1 < self.total_page_count else self.total_page_count)  # 上一页=当前页+1
        # page_prev_next = mark_safe(page_prev_next)  # 从view向前端传递HTML字符串，mark_safe这个函数就是确认这段函数是安全的，不是恶意攻击的。
        self.query_dict.setlist(self.page_param, [self.page - 1 if self.page - 1 >= 1 else self.page])
        page_prev="<a href='?{}' class ='g-actions-button g-actions-button-pager'> <i class ='fa fa-fw fa-caret-left right-4'></i>Next</a>".format(self.query_dict.urlencode())

        self.query_dict.setlist(self.page_param, [self.page + 1 if self.page + 1 < self.total_page_count else self.total_page_count])
        page_next = "<a href='?{}' class ='g-actions-button g-actions-button-pager'> <i class ='fa fa-fw fa-caret-left right-4'></i>Prev</a>".format(
            self.query_dict.urlencode())

        page_prev_next = mark_safe(page_prev+page_next)  # 从view向前端传递HTML字符串，mark_safe这个函数就是确认这段函数是安全的，不是恶意攻击的。
        return page_prev_next

class AuthMiddleware(MiddlewareMixin):#登录验证中间件
    def process_request(self,request):
        #1.排除那些不需要登录就能访问的页面
        if request.path_info=='/campus/login/':#request.path_info 获取当前请求的url
            return
        info_dict=request.session.get('info')#获取当前访问用户的session信息，如果能读到，说明已经登录过(走过登录这一步)，如果没有登录，就没有session,info_dict为None
        if info_dict:  #2.info_dict不为空
            return   #返回None 继续向后走，就结束了
        return redirect('/campus/login/')        # 3. info_dict为空   没有登录过，非法进入系统，返回到登录界面



def hubei_data(request):
    info = UUFunc().UUget(request)
    #truncate table campusmodule_hubeidata; 删除表 ，并重新创建该表
    ls = epid_data.getHuBei()
    now=datetime.now().date().strftime('%Y-%m-%d')#今天
    try:
        if len(HubeiData.objects.filter(hb_time = now))==0 or now!=str(HubeiData.objects.filter(hb_time=now).first().hb_time)  :  #数据库中的日期没有今天就存
            for i in ls:
                HubeiData.objects.create(name=i[0], value=i[1],hb_cure_num=i[2], hb_death_num =i[3])  # 将表单的数据添加到数据库中
        else:
            pass
    except:
        print("没有该字段")
    # print(list(HubeiData.objects.filter(hb_time=now).values('hb_city_name', 'hb_con_num')))#返回今天的城市名和累计确诊,不返回其他属性了。
    ls_date = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(0, 7)] # 七天内的日期
    ls_date.reverse()
    topData = [[i.value for i in HubeiData.objects.filter(hb_time=date).order_by('-value')[:7]] for date in ls_date]
    [topData[i].extend(list(map(lambda x, y: x + y, topData[i - 1], [random.randint(1, 100) for i in range(7)]))) for i in range(len(topData)) if len(topData[i]) == 0]  # 数据伪造
    topCity = [i.name for i in HubeiData.objects.filter(hb_time=now).order_by('-value')[:7]]

    print(list(HubeiData.objects.filter(hb_time=now).values('name', 'value')))
    context={
        'hbData':list(HubeiData.objects.filter(hb_time=now).values('name', 'value')),
        'topData': [list(i) for i in zip(*topData)],
        'topCity': topCity,  # 数量最多的前7个城市名
        'ls_date': ls_date,  # 一周日期
        # 'nav_html': navigation(('首页','疫情数据','湖北省疫情数据')),  # 前端页码html
        'nav_html':[
                        {"title": "主页", "url": "/campus/base_zy/index/",'index':1},
                        {"title": "疫情数据", "url": "/campus/base_zy/hubei_data/",'index':2},
                        {"title": "湖北省疫情数据", "url": "/campus/base_zy/hubei_data/",'index':3},
                    ],
        'uu': info['uname'],
        'avatar': info['avatar']
    }
    # for i in context['nav_html']:
    #     print(i['url'],i['title'])
    return render(request,'hubei_data.html',context)

def china_data(request):
    info = UUFunc().UUget(request)
    ls = epid_data.getChina()
    now=datetime.now().date().strftime('%Y-%m-%d')#今天
    try:
        if len(ChinaData.objects.filter(ch_time = now))==0 or now!=str(ChinaData.objects.filter(ch_time=now).first().ch_time)  :  #数据库中的日期没有今天就存
            for i in ls:
                ChinaData.objects.create(name=i[0],value=i[1],ch_econ_num=i[2],ch_death_num =i[3],ch_cure_num=i[4])  # 将表单的数据添加到数据库中
        else:
            pass
    except:
        print("没有该字段")
    chData = list(ChinaData.objects.filter(ch_time =now).values('name', 'value'))#全部数据
    # print(chData)

    ls_date = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(0, 7)]#七天内的日期
    # TruetopData=[list(ChinaData.objects.filter(ch_time=i).order_by('-value').values('name','value')[:7]) for i in ls_date]# 一周内的日期根据value降序排列的7个省份
    topData=[[i.value for i in ChinaData.objects.filter(ch_time=date).order_by('-value')[:7]] for date in ls_date]
    topProvince=[i.name for i in ChinaData.objects.filter(ch_time=now).order_by('-value')[:7]]
    # for i in range(len(topData)):#有空列表伪造数据
    #     if len(topData[i])==0:
    #         a=topData[i-1]
    #         b=[random.randint(1,100) for i in range(7)]
    #         topData[i].extend(list(map(lambda x,y:x+y,a,b)))
    #         # topData[i].extend([random.randint(1,100) for i in range(7)])
    [topData[i].extend(list(map(lambda x,y:x+y,topData[i-1],[random.randint(1,100) for i in range(7)]))) for i in range(len(topData)) if len(topData[i])==0]#数据伪造
    domesticData = epid_data.getDomestic()#国内累计确诊人数9481608 国内死亡人数31432 现存疑似人数3 累计治愈人数464712 现存确诊人数8985464 现存重症人数44
    context={
        'topData': [list(i) for i in zip(*topData)],
        'topProvince':topProvince,#数量最多的前7个省份名
        'ls_date': ls_date,  # 一周日期
        'chData': chData,
        'domesticData':domesticData,
        'nav_html': [
            {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
            {"title": "疫情数据", "url": "/campus/base_zy/hubei_data/", 'index': 2},
            {"title": "全国数据", "url": "/campus/base_zy/china_data/", 'index': 3},
        ],
        'uu': info['uname'],
        'avatar': info['avatar']
    }
    return render(request,'china_data.html',context)

def world_data(request):
    info = UUFunc().UUget(request)
    ls = epid_data.getWorld()

    now=datetime.now().date().strftime('%Y-%m-%d')#今天
    try:
        if len(WorldData.objects.filter(wd_time = now))==0 or now!=str(WorldData.objects.filter(wd_time=now).first().wd_time)  :  #数据库中的日期没有今天就存
            for i in ls:
                WorldData.objects.create(name=i[5],wd_ch_name=i[0],value=i[2], wd_econ_num=i[4],wd_death_num =i[3],wd_cure_num =i[1])  # 将表单的数据添加到数据库中
        else:
            pass
    except:
        print("没有该字段")
    wdData = list(WorldData.objects.filter(wd_time =now).values('name', 'value'))
    context={
        'wdData': wdData,
        'nav_html': [
            {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
            {"title": "疫情数据", "url": "/campus/base_zy/hubei_data/", 'index': 2},
            {"title": "世界数据", "url": "/campus/base_zy/world_data/", 'index': 3},
        ],        'uu': info['uname'],
        'avatar': info['avatar']

    }
    return render(request,'world_data.html',context)




def index(request):
    info = UUFunc().UUget(request)
    def simplify_province(province_str):
        # 去掉“省”或“自治区”等后缀
        province_str = re.sub(r'(省|市|自治区)', '', province_str)
        # 如果是直辖市，则直接返回
        if province_str in ['北京', '上海', '天津', '重庆']:
            return province_str
        # 去掉“新疆维吾尔”，“广西壮族”，“宁夏回族”等前缀
        province_str = re.sub(r'(维吾尔|壮族|回族)', '', province_str)
        # 去掉“特别行政区”后缀
        province_str = re.sub(r'特别行政区', '', province_str)
        return province_str

    now=datetime.now().date().strftime('%Y-%m-%d')#今天

    prov_data=ChinaData.objects.filter(ch_time=now).values_list('name','value')
    prov_dict = {item[0]: item[1] for item in prov_data}
    # print(prov_dict)

    #伪造excel今日累计确诊数据
    filename = path+'\static\laglat.xlsx'

    wb = openpyxl.load_workbook(filename)  # 打开该文件
    sheet = wb.active  # 取第0个工作表
    for i in range(2,sheet.max_row+1):
        prov_name=sheet['B'+str(i)].value     # 获取省份  #带省或自治区
        prov_value=prov_dict[simplify_province(prov_name)]
        if prov_value<100:
            prov_value+=1000+random.uniform(1000,1500)-random.randint(100,200)
        elif prov_value<1000:
            prov_value+=1000+random.uniform(1500,2000)-random.randint(200,300)
        elif prov_value<10000:
            prov_value=prov_value/10+random.uniform(2100,2500)-random.randint(300,400)
        elif prov_value<100000:
            prov_value=prov_value/100+random.uniform(2500,2800)-random.randint(400,600)
        elif prov_value<1000000:
            prov_value=prov_value/1000+random.uniform(2800,3000)-random.randint(400,900)
        elif prov_value<10000000:
            prov_value=prov_value/10000+random.uniform(3500,4000)-random.randint(400,500)
        sheet['E' + str(i)]=prov_value
    wb.save(filename)  # 指定路径,保存文件
    with open(path+"/static/epid_json.json", 'r', encoding='utf-8') as load_f:  # 打开json文件
        load_dict = json.load(load_f)
    for i in load_dict['features']:
        # print(i)
        json_index = i['properties']['ranking']
        json_name=i["properties"]['city']
        # json_value=i['properties']['avg']
        if sheet['A'+str(json_index+1)].value==json_index and sheet['C'+str(json_index+1)].value==json_name:
            i['properties']['avg']=sheet['E'+str(json_index+1)].value
        # json_name=sheet['E'+str(i)]
        # print(json_name,json_value)
        # print(i)
    with open(path+'/static/epid_json.json', 'w') as file:#保存文件
        json.dump(load_dict, file)

    user_list = []
    student_list = []
    filling_list = []
    filling_abnormal_list = []
    itinerary_list = []
    notice_list = []
    today = date.today()  # 2023-04-02

    for i in range(7):
        today_false = today - timedelta(days=i)

        user_value = User.objects.filter(user_create_time=today_false).count()  # 该日创建的用户数
        student_value = Student.objects.filter(student_create_time=today_false).count()  # 该日学生创建人数
        filling_value = Filling.objects.filter(filling_create_time=today_false).count()  # 该日核酸人数
        filling_abnormal_value = Filling.objects.filter(filling_create_time=today_false,
                                                        filling_health__gt=1).count()  # 该日异常人数
        itinerary_value = Itinerary.objects.filter(itinerary_create_time=today_false).count()  # 该日返校人数
        notice_value = Notice.objects.filter(notice_create_time=today_false).count()  # 该日疫情通告数

        user_list.append(user_value)
        student_list.append(student_value)
        filling_list.append(filling_value)
        filling_abnormal_list.append(filling_abnormal_value)
        itinerary_list.append(itinerary_value)
        notice_list.append(notice_value)

    # print(user_list, student_list, filling_list, filling_abnormal_list, itinerary_list, notice_list)

    User_count = User.objects.all().count()
    Student_count=Student.objects.all().count()
    Filling_count=Filling.objects.filter(filling_time=now).count()
    Filling_abnormal_count=Filling.objects.filter(filling_health__gt = 1,filling_time=now).count()
    Itinerary_today_count=Itinerary.objects.filter(itinerary_time=date.today()).count()
    Notice_count=Notice.objects.all().count()
    content={
        'User_count':User_count,#用户总数
        'Student_count':Student_count,#学生总数
        'Filling_count':Filling_count,#今日核酸已检测人数
        'Filling_abnormal_count':Filling_abnormal_count,#今日出现异常人数
        'Itinerary_today_count':Itinerary_today_count,#今日返校人数
        'Notice_count':Notice_count,   #疫情通告

        'user_list':user_list,
        'student_list':student_list,
        'filling_list': filling_list,
        'filling_abnormal_list':filling_abnormal_list,
        'itinerary_list':itinerary_list,
        'notice_list':notice_list,
        'nav_html': [
            {"title": "主页", "url": "/campus/base_zy/index/",'index':1}
        ],
                'uu': info['uname'],
        'avatar': info['avatar']
    }



    # date_list = [today - timedelta(days=x) for x in range(7)]
    # date_str_list = [d.strftime('%Y-%m-%d') for d in date_list]
    # print(date_str_list)


    # return redirect('/campus/base_zy/index/')  # 管理员
    return render(request,'index.html',content)

@csrf_exempt
def login(request):#登录
    if request.method=='GET':
        error_msg='get请求'
        return render(request, 'login.html')
    if request.method=='POST':
        # data = request.body
        # res1=json.loads(data.decode('utf-8'))#字符串转换字典
        # userName=str(res1['username'])#表单中的数据
        # userPassword=str(res1['userpassword'])
        userName=request.POST.get('username')#表单中的数据
        userPassword=request.POST.get('userpassword')
        print("登录界面表单中的数据:",userName,userPassword)
        # user = User.objects.get(user_name=userName)
        # print(user,user.user_name)
        try:
            print("这里")
            user=User.objects.get(user_name=userName)#数据库中的数据user_name等于表单的数据userName
            print("登录界面数据库中的数据:",user.user_name,user.user_password,user.user_identity,"=-=")
            print("++++++++++")
            if user.user_identity==1 and userPassword==user.user_password:
                request.session['info']={
                    'id':user.id,'name':user.user_name
                }
                return redirect('/users/base_user/index/')#普通用户
            elif user.user_identity==0 and userPassword==user.user_password:
                print("object:",object)
                request.session['info']={
                    'id':user.id,'name':user.user_name
                }
                return redirect('/campus/base_zy/index/')#管理员
            else:
                error_msg='密码错误'
                return render(request, 'login.html', {'error_msg':error_msg})
        except:
            error_msg='用户名不存在'
            return render(request, 'login.html', {'error_msg':error_msg})

def register(request):#注册
    if request.method=='POST':
        userName=request.POST.get('username')  # 得到表单的数据
        userPassword=request.POST.get("userpassword")
        userPasswords=request.POST.get('userpasswords')
        print("注册页面表单的数据：",userName,userPassword,userPasswords)
        try:
            user=User.objects.get(user_name=userName)
            if user:
                msg='用户名已存在！'
                return render(request,'register.html',{'msg':msg})
        except:
            if userPassword!=userPasswords:
                msg='两次密码不一致'
                return render(request,'register.html',{'msg':msg})
            else:
                # user_obj_list = []
                # for i in range(10):
                #     user_obj_list.append(
                #         user(
                #             user_name=random.randint(1,100),
                #             user_password=random.randint(1,100)
                #         )
                #     )
                # User.objects.bulk_create(user_obj_list)

                User.objects.create(
                    user_name=userName,
                    user_password=userPassword
                )
                return redirect('/campus/login/')
    else:
        return render(request,'register.html')



class collegeModelForm(FatherModelForm):
    class Meta:
        model=College
        # fields='__all__'#
        fields = ['college_name']  # 展示的字段

@csrf_exempt
def college_list(request):
    info = UUFunc().UUget(request)
    # print("request",request.GET)#获取url请求的参数
    # query_dict=copy.deepcopy(request.GET)#虽然是拷贝，但是相当于新建了一个对象       拷贝的原因是不能对request.GET进行直接修改的
    # print("dict:",query_dict)
    # query_dict._mutable=True   #True指请求可以被修改
    # query_dict.setlist('search_input',['无敌学院'])
    # print(query_dict.urlencode())
    # request.GET.setlist("search_input",['无敌学院'])
    # print(request.GET.urlencode())#将GET请求获取的字典各键值对拼接在一起

    # info=request.session.get('info')
    # if not info:
    #     return redirect('/campus/login/')
    data_dict={}
    search_data=request.GET.get('search_input',"")
    if search_data and  search_data in [i.college_name for i in College.objects.all()] :
        data_dict['college_name'] = search_data  # data_dict={'college_name':search_data}  #输入框的数据不为空 才去搜索
    else:  # 输入框的数据为空 或者 输入的不在数据库中
        pass  # print(data_dict)#空字典就是啥条件没有,就是全部搜索出来

    form = collegeModelForm()
    queryset = College.objects.filter(**data_dict).order_by('id')
    page_object = Pagination(request,queryset)
    content={
        'search_data': search_data,
        'all':page_object.page_queryset,#分完页的数据
        'page_prev_next':page_object.html(), #前端页码html
        'count':page_object.total_count,
        'count_page':page_object.total_page_count,
        'title':'学院管理',
        'form':form,
        'nav_html': [
            {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
            {"title": "校园管理", "url": "/campus/base_zy/college_list/", 'index': 2},
            {"title": "学院管理", "url": "/campus/base_zy/college_list/", 'index': 3},
        ],        'uu': info['uname'],
        'avatar': info['avatar']
    }
    return render(request, 'college_list.html',content)
@csrf_exempt
def college_add(request):
    info = UUFunc().UUget(request)
    '''新建/order编辑订单'''
    form = collegeModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({"status": True})
    return HttpResponse(json.dumps({"status": False, "error": form.errors}))
def college_delete(request):#学院删除
    coid=request.GET.get('coid')#获取id
    College.objects.filter(id=coid).delete()#删除
    return redirect('/campus/base_zy/college_list/')
def college_edit(request,coid):#学院编辑      如果访问http:127.0.0.1:8000/campus/base_zy/100/college_edit/ 那么coid=100
    info = UUFunc().UUget(request)
    if request.method=='GET':
        row_object=College.objects.filter(id=coid).first()    #根据coid获取数据  first第一个即第一行数据
        # print("学院编辑的这一行数据:",row_object.id,row_object.college_name,row_object.college_creatTime,row_object.college_updateTime)
        context = {
            'row_object': row_object,
            'nav_html': [
                {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
                {"title": "校园管理", "url": "/campus/base_zy/college_list/", 'index': 2},
                {"title": "学院管理", "url": "/campus/base_zy/college_list/", 'index': 3},
                {"title": "学院编辑", "url": "/campus/base_zy/{}/college_edit/".format(coid), 'index': 4},
            ],        'uu': info['uname'],
        'avatar': info['avatar']
        }
        # for i in context['nav_html']:
        #     print(i['url'],i['title'])


        return render(request,'college_edit.html',context)
    col_name=request.POST.get('col_name')#获取提交表单的值
    print("col_name",col_name)

    College.objects.filter(id=coid).update(college_name=col_name)#根据coid找到数据库中的college_name字段数据并更新
    College.objects.filter(id=coid).update(college_updateTime=datetime.now())  # 修改更新时间

    return redirect('/campus/base_zy/college_list/')




class classModelForm(FatherModelForm):
    exclude_fields = ['class_college_name']
    class Meta:
        model=Class
        # fields='__all__'#
        exclude=['class_updateTime']#不展示的字段
        widgets = {
            'class_creatTime': DateInput(),
            'class_updateTime': DateInput(),
            'class_college_name': forms.Select(attrs={'class': 'form-select'})
        }
def class_list(request):#班级列表
    info = UUFunc().UUget(request)
    data_dict={}
    search_data=request.GET.get('search_input',"")
    if search_data and  search_data in [i.class_name for i in Class.objects.all()] :
        data_dict['class_name'] = search_data  # data_dict={'college_name':search_data}  #输入框的数据不为空 才去搜索
    else:  # 输入框的数据为空 或者 输入的不在数据库中
        pass  # print(data_dict)#空字典就是啥条件没有,就是全部搜索出来

    form = classModelForm()
    queryset = Class.objects.filter(**data_dict).order_by('id')
    page_object = Pagination(request,queryset)
    content={
        'search_data': search_data,
        'all':page_object.page_queryset,#分完页的数据
        'page_prev_next':page_object.html(), #前端页码html
        'count':page_object.total_count,
        'count_page':page_object.total_page_count,
        'title':'班级管理',
        'form':form,
        'add_href':'/campus/base_zy/class_add/',
        'edit_href':'class_edit',
        'delete_href':'class_delete',
        'nav_html': [
            {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
            {"title": "校园管理", "url": "/campus/base_zy/college_list/", 'index': 2},
            {"title": "班级管理", "url": "/campus/base_zy/class_list/", 'index': 3},
        ],        'uu': info['uname'],
        'avatar': info['avatar']
    }
    return render(request, 'class_list.html',content)
def class_add(request):  # 班级新增
    info = UUFunc().UUget(request)
    if request.method == "GET":
        form = classModelForm()
        context={
            "form": form, 'title': "班级新增",
            'nav_html': [
                {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
                {"title": "校园管理", "url": "/campus/base_zy/college_list/", 'index': 2},
                {"title": "班级管理", "url": "/campus/base_zy/class_list/", 'index': 3},
                {"title": "班级新增", "url": "/campus/base_zy/class_list/", 'index': 4},
            ],        'uu': info['uname'],
        'avatar': info['avatar']
        }
        return render(request, '_add.html',context)
    form =classModelForm(data=request.POST)
    if form.is_valid():  # 数据校验成功
        form.save()
        return redirect('/campus/base_zy/class_list/')
    return render(request, '_add.html', {"form": form, 'title': '班级新增'})
# def class_add(request):#班级新增
#     if request.method=='POST':
#         className=request.POST.get('cla_name')  # 得到表单的数据
#         classRemark= request.POST.get('cla_remark')
#         classcollegeName=request.POST.get('cla_college_name')
#         classCreatTime=request.POST.get("cla_cre_time")
#         classUpdateTime = request.POST.get("cla_upd_time")
#         print("新增页面表单的数据：",className,classRemark,classcollegeName,classCreatTime,classUpdateTime)
#
#         Class.objects.create(class_name=className,class_remark=classRemark,
#                              class_creatTime=classCreatTime,class_updateTime=classUpdateTime,
#                              class_college_name_id=classcollegeName)#将表单的数据添加到数据库中
#
#         return redirect('/campus/base_zy/class_list/')
#     else:
#         college_list = College.objects.all()  # 数据库中获取所有学院列表
#         # for co in college_list:
#         #     print("班级新增表单中所有学院数据",co.id,co.college_name)
#         return render(request, 'class_add.html',{'college_list':college_list})
def class_edit(request,cid):#班级编辑
    info = UUFunc().UUget(request)
    row_object = Class.objects.filter(id=cid).first()  # 根据cid获取数据  first第一个即第一行数据
    # print("通告编辑的这一行数据:", row_object.id, row_object.class_name)
    if request.method == "GET":
        form = classModelForm(instance=row_object)#instance=row_object是modelform默认将这一行的值在前端页面展示出来
        context={
            "form": form,
            'title': "班级编辑",
            'nav_html': [
                {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
                {"title": "校园管理", "url": "/campus/base_zy/college_list/", 'index': 2},
                {"title": "班级管理", "url": "/campus/base_zy/class_list/", 'index': 3},
                {"title": "班级编辑", "url": "/campus/base_zy/{}/class_edit/".format(cid), 'index': 4},
            ],        'uu': info['uname'],
        'avatar': info['avatar']
        }
        return render(request, '_edit.html',context)
    if request.method=="POST":
        form = classModelForm(data=request.POST,instance=row_object)#instance=row_object意味着不在是新增数据，而是将该行更新
        if form.is_valid():#数据校验成功
            form.save()#保存数据库
            Class.objects.filter(id=cid).update(class_updateTime=datetime.now())  # 修改更新时间
            return redirect('/campus/base_zy/class_list/')
        # else:#数据校验失败
        #     print("数据校验失败:",form.errors)
        return render(request, '_edit.html',{'form':form})
def class_delete(request,cid):#班级删除
    Class.objects.filter(id=cid).delete()
    return redirect('/campus/base_zy/class_list/')



class teacherModelForm(FatherModelForm):
    teacher_phone=forms.CharField(
        label = "手机号",
        validators = [RegexValidator(r'^1[3-9]\d{9}$', '手机号码输入有误')],
    )
    class Meta:
        model=Teacher
        fields='__all__'#取所有字段

        def clean_mobile(self):
            txt_mobile = self.cleaned_data["teacher_phone"]
            print(txt_mobile)
            exists = Teacher.objects.filter(teacher_phone=txt_mobile).exists()
            if exists:
            # 验证不通过
                raise ValidationError("号码已存在")

            # 验证通过
            return txt_mobile

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for name,field in self.fields.items():#循环所有字段即fields=['notice_name','notice_content','notice_writer']#展示的字段
            if name in ['teacher_user_name','teacher_gender','teacher_college_name'] :
                field.widget.attrs = {'class': 'form-select',
                                      'placeholder': field.label}
def teacher_list(request):
    info = UUFunc().UUget(request)
    data_dict={}
    search_data=request.GET.get('search_input',"")
    if search_data and  search_data in [i.teacher_name for i in Teacher.objects.all()] :
        data_dict['teacher_name'] = search_data  # data_dict={'college_name':search_data}  #输入框的数据不为空 才去搜索
    else:  # 输入框的数据为空 或者 输入的不在数据库中
        pass  # print(data_dict)#空字典就是啥条件没有,就是全部搜索出来

    form = teacherModelForm()
    queryset = Teacher.objects.filter(**data_dict).order_by('id')
    page_object = Pagination(request,queryset)
    content={
        'search_data': search_data,
        'all':page_object.page_queryset,#分完页的数据
        'page_prev_next':page_object.html(), #前端页码html
        'count':page_object.total_count,
        'count_page':page_object.total_page_count,
        'title':'辅导员管理',
        'form':form,
        'nav_html': [
            {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
            {"title": "校园管理", "url": "/campus/base_zy/college_list/", 'index': 2},
            {"title": "辅导员管理", "url": "/campus/base_zy/teacher_list/", 'index': 3},
        ],        'uu': info['uname'],
        'avatar': info['avatar']
    }
    return render(request, 'teacher_list.html',content)
    # count=Teacher.objects.all().count()#数据库数据一共有多少条
    # page_size=7#每页最多显示7条
    # count_page = math.ceil(count / page_size)  # 向上取整，一共有多少页
    # page=int(request.GET.get('page_input',1))#获取名字为page_input的标签值，没获取到返回1
    # if page>count_page:
    #     page=count_page
    # elif page<=0:
    #     page=1
    # else:
    #     page=page
    # start_page=(page-1)*page_size
    # end_page=page_size*page    #0,7  7,14  14,21
    # # page_prev_next='''<a href='?page_input={}' class ='g-actions-button g-actions-button-pager'> <i class ='fa fa-fw fa-caret-left right-4'></i>Prev</a>
    # #               <a href='?page_input={}' class='g-actions-button g-actions-button-pager g-table-list-pager'>Next<i class='fa fa-fw fa-caret-right left-4'></i></a>'''.format(page-1 if page-1>=1 else page,page+1 if page+1<count_page else count_page)  #上一页当前页+1
    # #
    # # page_prev_next=mark_safe(page_prev_next)  #从view向前端传递HTML字符串，mark_safe这个函数就是确认这段函数是安全的，不是恶意攻击的。
    #
    # data_dict={}
    # search_data=request.GET.get('search_input',"")
    # if search_data and  search_data in [i.teacher_name for i in Teacher.objects.all()]:
    #     data_dict['teacher_name']=search_data
    # else:#输入框的数据为空
    #     pass
    # query_dict=copy.deepcopy(request.GET)#虽然是拷贝，但是相当于新建了一个对象       拷贝的原因是不能对request.GET进行直接修改的
    #
    # query_dict._mutable=True   #True指请求可以被修改
    # page_param='page_input'
    # query_dict.setlist(page_param, [page - 1 if page - 1 >= 1 else page])
    # page_prev = "<a href='?{}' class ='g-actions-button g-actions-button-pager'> <i class ='fa fa-fw fa-caret-left right-4'></i>Prev</a>".format(
    #     query_dict.urlencode())
    #
    # query_dict.setlist(page_param,[page+1 if page+1<count_page else count_page])
    # page_next = "<a href='?{}' class ='g-actions-button g-actions-button-pager'> <i class ='fa fa-fw fa-caret-left right-4'></i>Prev</a>".format(
    #     query_dict.urlencode())
    #
    # page_prev_next = mark_safe(page_prev + page_next)  # 从view向前端传递HTML字符串，mark_safe这个函数就是确认这段函数是安全的，不是恶意攻击的。
    #
    #
    # allTeacher = Teacher.objects.filter(**data_dict).order_by('id')[start_page:end_page]
    # form = teacherModelForm()
    # return render(request,'teacher_list.html',{'all':allTeacher,'search_data':search_data,'count':count,'count_page':count_page,'page_prev_next':page_prev_next,'title':'辅导员管理','form':form})
def teacher_add(request):
    info = UUFunc().UUget(request)
    if request.method == "GET":
        form=teacherModelForm()
        context={
            "form": form, 'title': '辅导员新增',
            'nav_html': [
                {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
                {"title": "校园管理", "url": "/campus/base_zy/college_list/", 'index': 2},
                {"title": "辅导员管理", "url": "/campus/base_zy/teacher_list/", 'index': 3},
                {"title": "辅导员新增", "url": "/campus/base_zy/teacher_add/", 'index': 4},
            ],        'uu': info['uname'],
        'avatar': info['avatar']
        }
        return render(request, '_add.html',context)

    form = teacherModelForm(data=request.POST)
    if form.is_valid():  # 数据校验成功
        print(form.cleaned_data)
        form.save()
        return redirect('/campus/base_zy/teacher_list/')
    return render(request, '_add.html', {"form": form,'title':'辅导员新增'})
def teacher_edit(request,cid):#教师编辑
    info = UUFunc().UUget(request)
    row_object = Teacher.objects.filter(id=cid).first()  # 根据cid获取数据  first第一个即第一行数据
    if request.method == "GET":
        form = teacherModelForm(instance=row_object)#instance=row_object是modelform默认将这一行的值在前端页面展示出来
        context={
            "form": form,
            'title': "辅导员编辑",
            'nav_html': [
                {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
                {"title": "校园管理", "url": "/campus/base_zy/college_list/", 'index': 2},
                {"title": "辅导员管理", "url": "/campus/base_zy/teacher_list/", 'index': 3},
                {"title": "辅导员编辑", "url": "/campus/base_zy/{}/teacher_edit/".format(cid), 'index': 4},
            ],        'uu': info['uname'],
        'avatar': info['avatar']
        }
        return render(request, '_edit.html',context)
    if request.method=="POST":
        form = teacherModelForm(data=request.POST,instance=row_object)#instance=row_object意味着不在是新增数据，而是将该行更新
        if form.is_valid():#数据校验成功
            form.save()#保存数据库
            return redirect('/campus/base_zy/teacher_list/')
        return render(request, '_edit.html',{'form':form})
def teacher_delete(request,cid):#班级删除
    Teacher.objects.filter(id=cid).delete()
    return redirect('/campus/base_zy/teacher_list/')


class studentModelForm(FatherModelForm):
    exclude_fields = ['student_user_name','student_teacher_name','student_college_name','student_class_name']
    student_phone=forms.CharField(label='手机号',validators=[RegexValidator(r'^1[3-9]\d{9}$','手机号格式错误')])
    class Meta:
        model=Student
        fields='__all__'#取所有字段
        widgets={
            'student_user_name':forms.Select(attrs={'class':'form-select'}),
            'student_teacher_name': forms.Select(attrs={'class': 'form-select'}),
            'student_college_name': forms.Select(attrs={'class': 'form-select'}),
            'student_class_name': forms.Select(attrs={'class': 'form-select'})

        }
def student_list(request):
    info = UUFunc().UUget(request)
    data_dict={}
    search_data=request.GET.get('search_input',"")
    if search_data and  search_data in [i.student_name for i in Student.objects.all()] :
        data_dict['student_name'] = search_data  # data_dict={'college_name':search_data}  #输入框的数据不为空 才去搜索
    else:  # 输入框的数据为空 或者 输入的不在数据库中
        pass  # print(data_dict)#空字典就是啥条件没有,就是全部搜索出来

    form = studentModelForm()
    queryset = Student.objects.filter(**data_dict).order_by('id')
    page_object = Pagination(request,queryset)
    content={
        'search_data': search_data,
        'all':page_object.page_queryset,#分完页的数据
        'page_prev_next':page_object.html(), #前端页码html
        'count':page_object.total_count,
        'count_page':page_object.total_page_count,
        'title':'学生管理',
        'form':form,
        'nav_html': [
            {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
            {"title": "校园管理", "url": "/campus/base_zy/college_list/", 'index': 2},
            {"title": "学生管理", "url": "/campus/base_zy/student_list/", 'index': 3},
        ],        'uu': info['uname'],
        'avatar': info['avatar']
    }
    return render(request, 'student_list.html',content)
def student_add(request):
    info = UUFunc().UUget(request)
    if request.method == "GET":
        form = studentModelForm()
        context={
            "form": form, 'title': '学生新增',
            'nav_html': [
                {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
                {"title": "校园管理", "url": "/campus/base_zy/college_list/", 'index': 2},
                {"title": "学生管理", "url": "/campus/base_zy/student_list/", 'index': 3},
                {"title": "学生新增", "url": "/campus/base_zy/student_add/", 'index': 4},
            ],        'uu': info['uname'],
        'avatar': info['avatar']
        }
        return render(request, '_add.html', context)

    form = studentModelForm(data=request.POST)
    if form.is_valid():  # 数据校验成功
        print(form.cleaned_data)
        form.save()
        return redirect('/campus/base_zy/student_list/')
    return render(request, '_add.html', {"form": form,'title':'学生新增'})
def student_edit(request,cid):
    info = UUFunc().UUget(request)
    row_object = Student.objects.filter(id=cid).first()  # 根据cid获取数据  first第一个即第一行数据
    if request.method == "GET":
        form = studentModelForm(instance=row_object)  # instance=row_object是modelform默认将这一行的值在前端页面展示出来
        context={
            "form": form,
            'title': "学生编辑",
            'nav_html': [
                {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
                {"title": "校园管理", "url": "/campus/base_zy/college_list/", 'index': 2},
                {"title": "学生管理", "url": "/campus/base_zy/student_list/", 'index': 3},
                {"title": "学生编辑", "url": "/campus/base_zy/{}/student_edit/".format(cid), 'index': 4},
            ],        'uu': info['uname'],
        'avatar': info['avatar']
        }
        return render(request, '_edit.html', context)
    if request.method == "POST":
        form = studentModelForm(data=request.POST, instance=row_object)  # instance=row_object意味着不在是新增数据，而是将该行更新
        if form.is_valid():  # 数据校验成功
            form.save()  # 保存数据库
            return redirect('/campus/base_zy/student_list/')
        return render(request, '_edit.html', {'form': form})
def student_delete(request, cid):  # 班级删除
    Student.objects.filter(id=cid).delete()
    return redirect('/campus/base_zy/student_list/')


# <textarea name="notice_content" cols="40" rows="4" maxlength="64" required="" id="id_notice_content"></textarea>

class noticeModelForm(FatherModelForm):
    notice_name=forms.CharField(min_length=3 ,label="标题")#制定校验规则 最小长度为3
    class Meta:
        model=Notice
        # fields=['notice_name','notice_content','notice_writer']#展示的字段
        fields='__all__'#取所有字段
        widgets={
            'notice_content': forms.Textarea(attrs={'rows':'8'}),
            'notice_writer':forms.Select(attrs={'class':'form-select'}),
            'notice_publishTime': DateInput()
        }
@csrf_exempt
def notice_ajax(request):
    print("ajax")
    info=request.body
    a=info.decode('unicode_escape').encode('utf-8')
    print(a)
    print('noticeGET:', request.GET)
    print('noticeGET:', request.PUT)
    print('notice:', request)
    return HttpResponse(request.body)

def notice_list(request):#疫情通告
    info = UUFunc().UUget(request)
    data_dict = {}
    search_data = request.GET.get('search_input', "")
    if search_data and search_data in [i.notice_name for i in Notice.objects.all()]:
        data_dict['notice_name'] = search_data  # data_dict={'college_name':search_data}  #输入框的数据不为空 才去搜索
    else:
        pass
    form = noticeModelForm()
    queryset = Notice.objects.filter(**data_dict).order_by('id')
    page_object = Pagination(request, queryset)
    context = {
        'search_data': search_data,
        'all': page_object.page_queryset,  # 分完页的数据
        'page_prev_next': page_object.html(),  # 前端页码html
        'count': page_object.total_count,
        'count_page': page_object.total_page_count,
        'title': '疫情通告管理',
        'form': form,
        'nav_html': [
            {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
            {"title": "疫情通告", "url": "/campus/base_zy/notice_list/", 'index': 2},
            {"title": "通告管理", "url": "/campus/base_zy/notice_list/", 'index': 3},
        ],        'uu': info['uname'],
        'avatar': info['avatar']
    }
    return render(request, 'notice_list.html', context)
@csrf_exempt

def notice_cont(request,cid):
    info = UUFunc().UUget(request)
    data_dict = {}
    search_data = request.GET.get('search_input', "")
    if search_data and search_data in [i.notice_name for i in Notice.objects.all()]:
        data_dict['notice_name'] = search_data  # data_dict={'college_name':search_data}  #输入框的数据不为空 才去搜索
    else:
        pass
    form = noticeModelForm()
    queryset = Notice.objects.filter(**data_dict).order_by('id')
    page_object = Pagination(request, queryset)

    content = Notice.objects.filter(id=cid).values_list('notice_content',flat=True).first()
    # print(list(content))

    context = {
        'search_data': search_data,
        'all': page_object.page_queryset,  # 分完页的数据
        'page_prev_next': page_object.html(),  # 前端页码html
        'count': page_object.total_count,
        'count_page': page_object.total_page_count,
        'title': '疫情通告管理',
        'form': form,
        'nav_html': [
            {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
            {"title": "疫情通告", "url": "/campus/base_zy/notice_list/", 'index': 2},
            {"title": "通告管理", "url": "/campus/base_zy/notice_list/", 'index': 3},
        ],        'uu': info['uname'],
        'avatar': info['avatar'],
        'content': content
    }
    return render(request, 'notice_list.html', context)





def notice_add(request):
    info = UUFunc().UUget(request)
    if request.method == "GET":
        form = noticeModelForm()
        context={
            "form": form, 'title': '疫情通告新增',
            'nav_html': [
                {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
                {"title": "疫情通告", "url": "/campus/base_zy/notice_list/", 'index': 2},
                {"title": "通告管理", "url": "/campus/base_zy/notice_list/", 'index': 3},
                {"title": "疫情通告新增", "url": "/campus/base_zy/notice_add/", 'index': 4},
            ],        'uu': info['uname'],
        'avatar': info['avatar']
        }
        return render(request, '_add.html', context)
    form = noticeModelForm(data=request.POST)
    if form.is_valid():  # 数据校验成功
        print(form.cleaned_data)
        form.save()
        return redirect('/campus/base_zy/notice_list/')
    return render(request, '_add.html', {"form": form, 'title': '疫情通告新增'})
def notice_edit(request,cid):#通告编辑
    info = UUFunc().UUget(request)
    row_object = Notice.objects.filter(id=cid).first()  # 根据cid获取数据  first第一个即第一行数据
    if request.method == "GET":

        form = noticeModelForm(instance=row_object)#instance=row_object是modelform默认将这一行的值在前端页面展示出来
        context={
            "form": form,
            'title': "通告编辑",
            'nav_html': [
                {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
                {"title": "疫情通告", "url": "/campus/base_zy/notice_list/", 'index': 2},
                {"title": "通告管理", "url": "/campus/base_zy/notice_list/", 'index': 3},
                {"title": "疫情通告编辑", "url": "/campus/base_zy/{}/notice_add/".format(cid), 'index': 4},
            ],        'uu': info['uname'],
        'avatar': info['avatar']
        }
        return render(request, '_edit.html',context)
    if request.method=="POST":
        form = noticeModelForm(data=request.POST,instance=row_object)#instance=row_object意味着不在是新增数据，而是将该行更新
        if form.is_valid():#数据校验成功
            form.save()#保存数据库
            return redirect('/campus/base_zy/notice_list/')
        return render(request, '_edit.html',{'form':form})
def notice_delete(request,cid):#通告删除
    Notice.objects.filter(id=cid).delete()
    return redirect('/campus/base_zy/notice_list/')
# def notice_list(request):  # 疫情通告
#     # ----------------------搜索----------------------------
#     # Notice.objects.filter(notice_name='法国的',id=33)
#     # xx={'notice_name':'法国的','id':33}
#     # Notice.objects.filter(**xx)
#     # Notice.objects.filter(id__gte=12) #id__gt大于 id__gte大于等于 id__lt小于 id__lte小于等于   notice_name__startswith="hss"以hss开头    __endswith以什么为结尾  __contains包含
#     #.exists()判断是否存在 .exclude(id=2)排除id等于2的
#     # allNotice = Notice.objects.all().order_by("-id") #    -是降序desc
#
#     #----------------------分页-----------------------
#     # Notice.objects.filter()[0:10]#符合filter搜索条件的前十条
#     count=Notice.objects.all().count()#数据库数据一共有多少条
#     page_size=7#每页最多显示7条
#     count_page = math.ceil(count / page_size)  # 向上取整，一共有多少页
#     page=int(request.GET.get('page_input',1))#获取名字为page_input的标签值，没获取到返回1
#
#     if page>count_page:
#         page=count_page
#     elif page<=0:
#         page=1
#     else:
#         page=page
#
#     start_page=(page-1)*page_size
#     end_page=page_size*page    #0,7  7,14  14,21
#     page_prev_next='''<a href='?page_input={}' class ='g-actions-button g-actions-button-pager'> <i class ='fa fa-fw fa-caret-left right-4'></i>Prev</a>
#                   <a href='?page_input={}' class='g-actions-button g-actions-button-pager g-table-list-pager'>Next<i class='fa fa-fw fa-caret-right left-4'></i></a>'''.format(page-1 if page-1>=1 else page,page+1 if page+1<count_page else count_page)  #上一页当前页+1
#
#     page_prev_next=mark_safe(page_prev_next)  #从view向前端传递HTML字符串，mark_safe这个函数就是确认这段函数是安全的，不是恶意攻击的。
#
#
#     data_dict={}
#     search_data=request.GET.get('search_input',"")
#     # print("输入框内的数据:",search_data,type(search_data))
#     if search_data:
#         # data_dict={'notice_name':search_data}  #输入框的数据不为空 才去搜索
#         data_dict['notice_name']=search_data
#     else:#输入框的数据为空
#         pass
#         # print(data_dict)#空字典就是啥条件没有,就是全部搜索出来
#
#     queryset2=Notice.objects.filter(**data_dict)
#     print("搜索到的:",queryset2)
#     # allNotice=Notice.objects.filter(**data_dict).order_by('id')#allNotice和queryset2结果是一样的，只是排了个序,当data_dict是空字典就是all()全部获取
#     allNotice = Notice.objects.filter(**data_dict).order_by('id')[start_page:end_page]
#     return render(request,'notice_list.html',{'allNotice':allNotice,'search_data':search_data,'count':count,'count_page':count_page,'page_prev_next':page_prev_next})
#
#
#
#
# def notice_add(request):#疫情通告新增  ModelForm版  新页面
#     if request.method == "GET":
#         form=noticeModelForm()
#         # for field in form:
#         #     print(field.label,field)#标题 <input type="text" name="notice_name" maxlength="32" required id="id_notice_name">
#         return render(request, 'notice_add.html',{"form":form})
#     #用户提交数据，数据校验 request.method == "POST":
#     form=noticeModelForm(data=request.POST)
#     if form.is_valid():#数据校验成功
#         print(form.cleaned_data)#{'notice_name': "s's's's's's's's", 'notice_content': 'sssssssssss', 'notice_writer': <User: admin>}
#         form.save()#自动保存到数据库中   --Meta类定义的model=models.Notice 数据库
#         return redirect('/campus/base_zy/notice_list/')
#     # else:#数据校验失败
#     #     print(form.errors)
#     return render(request, 'notice_add.html', {"form": form})#数据校验失败,在页面显示校验信息
#     #错误信息都在form.errors中,每一个字段信息都在   但是get请求的form和post的是不一样的，get是啥都没有的,post有用户提交的data=request.POST还有error
#
#
# def notice_edit(request,nocid):#疫情通告编辑
#     row_object = Notice.objects.filter(id=nocid).first()  # 根据ncoid获取数据  first第一个即第一行数据
#     print("通告编辑的这一行数据:", row_object.id, row_object.notice_content, row_object.notice_writer)
#     if request.method == "GET":
#         form = noticeModelForm(instance=row_object)#instance=row_object是modelform默认将这一行的值在前端页面展示出来
#         return render(request, 'notice_edit.html',{"form": form})
#     if request.method=="POST":
#         form = noticeModelForm(data=request.POST,instance=row_object)#instance=row_object意味着不在是新增数据，而是将该行更新
#         if form.is_valid():#数据校验成功
#             print("数据校验成功:",form.cleaned_data)
#             form.save()#保存数据库
#             return redirect('/campus/base_zy/notice_list/')
#         # else:#数据校验失败
#         #     print("数据校验失败:",form.errors)
#         return render(request, 'notice_edit.html',{'form':form})
#
# def notice_delete(request,nocid):#疫情通告删除
#     Notice.objects.filter(id=nocid).delete()
#     return redirect('/campus/base_zy/notice_list/'

class fillingModelForm(FatherModelForm):
    exclude_fields = ['filling_nucleic','filling_countVaccine','filling_name']
    class Meta:
        model=Filling
        fields='__all__'#取所有字段
        # exclude=['filling_nucleic']#不展示的字段
        widgets={
            'filling_remark': forms.Textarea(attrs={'rows':'1'}),
            'filling_countVaccine':forms.Select(attrs={'class':'form-select'}),
            'filling_name': forms.Select(attrs={'class': 'form-select'})
        }
# class fillingPage(Pagination):
#     def __init__(self,request,queryset,page_size=3,page_param='page_input'):
#         self.page_size=page_size
@csrf_exempt
def filling_list(request):
    info = UUFunc().UUget(request)
    data_dict = {}
    search_data = request.GET.get('search_input', "")
    if search_data and Student.objects.filter(student_name=search_data).first().id in [i.itinerary_name_id for i in Itinerary.objects.all()]:
        data_dict['filling_name_id'] = Student.objects.filter(student_name=search_data).first().id#获取search_data对应的id
    else:  # 输入框的数据为空 或者 输入的不在数据库中
        pass  # print(data_dict)#空字典就是啥条件没有,就是全部搜索出来
    form = fillingModelForm()
    queryset = Filling.objects.filter(**data_dict).order_by('id')
    page_object = Pagination(request, queryset,3)
    content = {
        'search_data': search_data,
        'all': page_object.page_queryset,  # 分完页的数据
        'page_prev_next': page_object.html(),  # 前端页码html
        'count': page_object.total_count,
        'count_page': page_object.total_page_count,
        'title': '健康打卡管理',
        'form': form,
        'nav_html': [
            {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
            {"title": "健康填报", "url": "/campus/base_zy/filling_list/", 'index': 2},
            {"title": "健康打卡管理", "url": "/campus/base_zy/filling_list/", 'index': 3},
        ],        'uu': info['uname'],
        'avatar': info['avatar']

    }
    return render(request, 'filling_list.html', content)
@csrf_exempt
def filling_add(request):
    info = UUFunc().UUget(request)
    if request.method == "GET":
        form = fillingModelForm()
        context={
            "form": form, 'title': '健康打卡新增',
            'nav_html': [
                {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
                {"title": "健康填报", "url": "/campus/base_zy/filling_list/", 'index': 2},
                {"title": "健康打卡管理", "url": "/campus/base_zy/filling_list/", 'index': 3},
                {"title": "健康打卡新增", "url": "/campus/base_zy/filling_add/", 'index': 4},
            ]  ,      'uu': info['uname'],
        'avatar': info['avatar']
        }
        return render(request, '_add.html', context)
    form = fillingModelForm(data=request.POST,files=request.FILES)

    if form.is_valid():  # 数据校验成功
        # print("成功:",form.cleaned_data)
        # #读取图片内容，写入到文件夹中并获取文件的路径
        # img_object=form.cleaned_data.get('filling_nucleic')
        # # img_path=os.path.join('CampusModule','static','img','upImg',img_object.name)#等价于 img_path='CampusModule/static/img/upImg/{}'.format(img_object.name)
        #
        # # media_path=os.path.join(settings.MEDIA_ROOT,img_object.name)#绝对路径E:\Source Code\Python\Django\EpidemicProject\media\012219-1643563339f065.jpg
        # media_path = os.path.join('media',img_object.name)  # 相对路径
        # f = open(media_path, mode='wb')
        # for chunk in img_object.chunks():
        #     f.write(chunk)
        # f.close()
        # print("路径:",media_path)
        #
        # Filling.objects.create(
        #     filling_name=form.cleaned_data['filling_name'],
        #     filling_temperature=form.cleaned_data['filling_temperature'],
        #     filling_nucleic=media_path,#将图片路径写入到数据库
        #     filling_health=form.cleaned_data['filling_health'],
        #     filling_countVaccine=form.cleaned_data['filling_countVaccine'],
        #     filling_remark =form.cleaned_data['filling_remark']
        # )
        form.save()#对于文件自动保存 将上传路径(models.py相应字段的upload_to参数)+文件名吸入到数据库
        return redirect('/campus/base_zy/filling_list/')
    return render(request, '_add.html', {"form": form,'title':'打卡新增'})
def filling_edit(request,cid):
    info = UUFunc().UUget(request)
    row_object = Filling.objects.filter(id=cid).first()  # 根据cid获取数据  first第一个即第一行数据
    if request.method == "GET":
        form = fillingModelForm(instance=row_object)  # instance=row_object是modelform默认将这一行的值在前端页面展示出来
        context={
            "form": form, 'title': '健康打卡新增',
            'nav_html': [
                {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
                {"title": "健康填报", "url": "/campus/base_zy/filling_list/", 'index': 2},
                {"title": "健康打卡管理", "url": "/campus/base_zy/filling_list/", 'index': 3},
                {"title": "健康打卡编辑", "url": "/campus/base_zy/{}/filling_edit/".format(cid), 'index': 4},
            ]   ,     'uu': info['uname'],
        'avatar': info['avatar']
        }
        return render(request, '_edit.html',context)
    if request.method == "POST":
        form = fillingModelForm(data=request.POST,files=request.FILES,instance=row_object)  # instance=row_object意味着不在是新增数据，而是将该行更新
        if form.is_valid():  # 数据校验成功
            form.save()  # 保存数据库
            return redirect('/campus/base_zy/filling_list/')
        return render(request, '_edit.html', {'form': form})
def filling_delete(request, cid):  # 填报删除
    Filling.objects.filter(id=cid).delete()
    return redirect('/campus/base_zy/filling_list/')





class itineraryModelForm(FatherModelForm):
    exclude_fields = ['itinerary_name', 'itinerary_college_name', 'itinerary_class_name']
    class Meta:
        model=Itinerary
        fields='__all__'#取所有字段
        widgets = {
            'itinerary_time' : DateInput(),
            'itinerary_remark': forms.Textarea(attrs={'rows': '2'}),
            'itinerary_name': forms.Select(attrs={'class': 'form-select'}),
            'itinerary_college_name': forms.Select(attrs={'class': 'form-select'}),
            'itinerary_class_name': forms.Select(attrs={'class': 'form-select'})
        }
@csrf_exempt
def itinerary_list(request):
    info = UUFunc().UUget(request)
    data_dict = {}
    search_data = request.GET.get('search_input', "")
    print("search_data:",search_data)

    if search_data and Student.objects.filter(student_name=search_data).first().id in [i.itinerary_name_id for i in Itinerary.objects.all()]:
        data_dict['itinerary_name_id'] = Student.objects.filter(student_name=search_data).first().id#获取search_data对应的id
    else:  # 输入框的数据为空 或者 输入的不在数据库中
        pass  # print(data_dict)#空字典就是啥条件没有,就是全部搜索出来
    form = itineraryModelForm()
    queryset = Itinerary.objects.filter(**data_dict).order_by('id')
    page_object = Pagination(request, queryset)
    content = {
        'search_data': search_data,
        'all': page_object.page_queryset,  # 分完页的数据
        'page_prev_next': page_object.html(),  # 前端页码html
        'count': page_object.total_count,
        'count_page': page_object.total_page_count,
        'title': '行程管理',
        'form': form,
        'nav_html': [
            {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
            {"title": "健康填报", "url": "/campus/base_zy/filling_list/", 'index': 2},
            {"title": "行程管理", "url": "/campus/base_zy/itinerary_list/", 'index': 3},
        ],        'uu': info['uname'],
        'avatar': info['avatar']
    }
    return render(request, 'itinerary_list.html', content)
def itinerary_add(request):
    info = UUFunc().UUget(request)
    if request.method == "GET":
        form = itineraryModelForm()
        context = {
            "form": form, 'title': '行程打卡新增',
            'nav_html': [
                {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
                {"title": "健康填报", "url": "/campus/base_zy/filling_list/", 'index': 2},
                {"title": "行程管理", "url": "/campus/base_zy/itinerary_list/", 'index': 3},
                {"title": "行程打卡新增", "url": "/campus/base_zy/itinerary_add/", 'index': 4},
            ],        'uu': info['uname'],
        'avatar': info['avatar']
        }
        return render(request, '_add.html', context)
    form = itineraryModelForm(data=request.POST)
    if form.is_valid():  # 数据校验成功
        form.save()
        return redirect('/campus/base_zy/itinerary_list/')
    return render(request, '_add.html', {"form": form, 'title': '行程打卡新增'})
def itinerary_edit(request,cid):
    info = UUFunc().UUget(request)
    row_object = Itinerary.objects.filter(id=cid).first()  # 根据cid获取数据  first第一个即第一行数据
    if request.method == "GET":
        form = itineraryModelForm(instance=row_object)  # instance=row_object是modelform默认将这一行的值在前端页面展示出来
        context = {
            "form": form, 'title': '行程编辑',
            'nav_html': [
                {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
                {"title": "健康填报", "url": "/campus/base_zy/filling_list/", 'index': 2},
                {"title": "行程管理", "url": "/campus/base_zy/itinerary_list/", 'index': 3},
                {"title": "行程编辑", "url": "/campus/base_zy/{}/itinerary_edit/".format(cid), 'index': 4},
            ],        'uu': info['uname'],
        'avatar': info['avatar']
        }
        return render(request, '_edit.html', context)
    if request.method == "POST":
        form = itineraryModelForm(data=request.POST, instance=row_object)  # instance=row_object意味着不在是新增数据，而是将该行更新
        if form.is_valid():  # 数据校验成功
            form.save()  # 保存数据库
            return redirect('/campus/base_zy/itinerary_list/')
        return render(request, '_edit.html', {'form': form})
def itinerary_delete(request, cid):  # 班级删除
    Itinerary.objects.filter(id=cid).delete()
    return redirect('/campus/base_zy/itinerary_list/')








@csrf_exempt
def ajax_test(request):
    if request.method=='GET':
        return render(request, 'ajax_test.html')
    print("post:",request.POST)
    print("files:",request.FILES)
    file_object=request.FILES.get('f1')
    print(file_object.name)#文件名
    f=open(file_object.name,mode='wb')
    for chunk in file_object.chunks():
        f.write(chunk)
    f.close()



    return HttpResponse("=========")




def  info_list(request):
    queryset=Admin_info.objects.filter(info_admin=1).values_list('info_admin__user_name','info_admin__user_password')
    print(queryset)

    #头像 昵称（用户名） 性别 男 地区 生日
    return HttpResponse(queryset)

# def info_account(request):
#     return render(request,'account_binding.html')
#



class accoutModelForm(FatherModelForm):
    # exclude_fields = ['info_creatTime','info_updateTime']
    class Meta:
        model=Admin_info
        fields='__all__'#取所有字段
        # exclude=['filling_nucleic']#不展示的字段
        exclude= ['info_creatTime', 'info_updateTime']
        # widgets={
        #     'filling_remark': forms.Textarea(attrs={'rows':'1'}),
        #     'filling_countVaccine':forms.Select(attrs={'class':'form-select'}),
        #     'filling_name': forms.Select(attrs={'class': 'form-select'})
        # }

@csrf_exempt
def info_account(request):  #用户绑定
    info = UUFunc().UUget(request)
    if request.method == "GET":
        form = accoutModelForm()
        context={
            "form": form, 'title': '用户绑定',
            'nav_html': [
                {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
                {"title": "个人中心", "url": "/campus/base_zy/info_account/", 'index': 2},
                {"title": "账户绑定", "url": "/campus/base_zy/info_account/", 'index': 3},
            ],        'uu': info['uname'],
        'avatar': info['avatar']
        }
        return render(request,'account_binding.html', context)
    form = accoutModelForm(data=request.POST)
    if form.is_valid():  # 数据校验成功
        form.save()#对于文件自动保存 将上传路径(models.py相应字段的upload_to参数)+文件名吸入到数据库
        # return render(request,'/campus/base_zy/index/')
        # return render(request,'user_index.html')
        return redirect('/campus/base_zy/index/')
    return render(request,'/campus/base_zy/info_account/')


def info_pwd(request):#修改密码
    info = UUFunc().UUget(request)
    context={
        'title': '密码修改',
        'nav_html': [
            {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
            {"title": "个人中心", "url": "/campus/base_zy/info_account/", 'index': 2},
            {"title": "密码修改", "url": "/campus/base_zy/info_pwd/", 'index': 3},
        ],
        'error_msg':"",
                'uu': info['uname'],
        'avatar': info['avatar']
    }
    if request.method=='GET':
        return render(request, 'info_pwd.html',context)
    userName=request.POST.get('Uname')#表单中的数据
    userPwd1=request.POST.get('Upwd1')
    userPwd2 = request.POST.get('Upwd2')
    flag=User.objects.filter(user_name=userName).exists()
    if flag:
        if userPwd2!=userPwd1:
            context['error_msg'] = '两次密码不一致'
            return render(request, 'info_pwd.html', context)
        else:
            User.objects.filter(user_name=userName).update(user_password=userPwd2)#根据coid找到数据库中的college_name字段数据并更新
            return redirect('/campus/base_zy/index/')#管理员
    else:
        context['error_msg']='用户名不存在'
        return render(request, 'info_pwd.html', context)

def info_edit(request):
    info = UUFunc().UUget(request)
    context={
        'title': '资料编辑',
        'nav_html': [
            {"title": "主页", "url": "/campus/base_zy/index/", 'index': 1},
            {"title": "个人中心", "url": "/campus/base_zy/info_account/", 'index': 2},
            {"title": "资料编辑", "url": "/campus/base_zy/info_edit/", 'index': 3},
        ],
        'error_msg':"",
        'uu': info['uname'],
        'avatar': info['avatar']
    }
    if request.method=='GET':
        return render(request,'info_edit.html',context)
    if request.method=="POST":
        oldName = request.POST.get('uname_old')
        userName = request.POST.get('uname')  # 表单中的数据
        Name=request.POST.get('name')
        Phone=request.POST.get('phone')
        gender=request.POST.get('inlineRadioOptions')
        file_object=request.FILES.get('avatar')
        media_path = os.path.join('static','img',file_object.name)  # 相对路径
        f = open(media_path, mode='wb')
        for chunk in file_object.chunks():
            f.write(chunk)
        f.close()  #保存上传的文件
        id = User.objects.filter(user_name=oldName).values_list('id', flat=True).first()
        Teacher.objects.filter(id=id).update(
            teacher_name=Name,
            teacher_gender=1 if gender=='男' else 2 ,
            teacher_phone=Phone,
        )
        User.objects.filter(user_name=oldName).update(user_name=userName,avatar_file=media_path)
        # return render(request, 'info_edit.html', context)
        return redirect('/campus/base_zy/index/')#管理员

