from django.db import models
from django.utils import timezone
import datetime
# Create your models here.

# python manage.py makemigrations
# python manage.py migrate


class User(models.Model):#用户表名
    user_name = models.CharField(max_length=32, verbose_name="用户名")
    user_password = models.CharField(max_length=32, verbose_name="密码")
    user_identity_choices=(
        (0,'管理员'),(1,'学生')
    )
    user_identity=models.SmallIntegerField(choices=user_identity_choices,verbose_name='用户身份', default=1)
    avatar_file = models.ImageField(upload_to='static/', verbose_name='头像')
    user_create_time=models.DateField(auto_now_add=True,verbose_name='创建时间',null=True)

    def __str__(self):   #https://www.bilibili.com/video/BV1gV4y157ho?p=33&vd_source=81d62b71de3939c64a2d812ba8c4bd07 第33集18分钟
        return self.user_name
    #__str__()函数就可以帮助我们打印对象中具体的属性值，或者你想得到的东西。__str__()有返回值，就会打印其中的返回值。


class HubeiData(models.Model):#湖北疫情数据
    #城市名, 累计确诊, 治愈(较昨日), 累计死亡
    name=models.CharField(max_length=32, verbose_name="城市名")
    value=models.IntegerField(verbose_name='累计确诊')#hb_con_num
    hb_cure_num = models.IntegerField(verbose_name='治愈(较昨日)')
    hb_death_num = models.IntegerField(verbose_name='累计死亡')
    hb_time = models.DateField(auto_now_add=True, verbose_name="记录时间")

class ChinaData(models.Model):  # 中国疫情数据
    #省份名,累计确诊,现存确诊,死亡,治愈
    name = models.CharField(max_length=32, verbose_name="省份名")
    value = models.IntegerField(verbose_name='累计确诊') #ch_con_num
    ch_econ_num = models.IntegerField(verbose_name='现存确诊')
    ch_death_num = models.IntegerField(verbose_name='死亡')
    ch_cure_num = models.IntegerField(verbose_name='治愈')
    ch_time = models.DateField(auto_now_add=True, verbose_name="记录时间")

class WorldData(models.Model):  # 世界疫情数据
    #省份名,累计确诊,现存确诊,死亡,治愈
    name = models.CharField(max_length=32, verbose_name="国家名")#英文的
    value = models.IntegerField(verbose_name='累计确诊')  #wd_con_num
    wd_econ_num = models.IntegerField(verbose_name='现存确诊')
    wd_death_num = models.IntegerField(verbose_name='累计死亡')
    wd_cure_num = models.IntegerField(verbose_name='累计治愈')
    # wd_time = models.DateField(default=datetime.datetime.now().date().strftime('%Y-%m-%d'), verbose_name="记录时间")
    wd_time = models.DateField(auto_now_add=True, verbose_name="记录时间")
    wd_ch_name = models.CharField(max_length=32, verbose_name="国家名(汉语)")  # 汉语




class Admin_info(models.Model):#'管理员用户信息表'
    info_admin=models.ForeignKey(to='User',on_delete=models.SET_NULL,null=True,blank=True,verbose_name='用户名',related_name='info_admin',db_constraint=False)
    info_teacher = models.ForeignKey(to='Teacher', on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='教师', related_name='info_teacher', db_constraint=False)
    info_creatTime= models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    info_updateTime = models.DateTimeField(auto_now=True, verbose_name="更新时间")

class User_info(models.Model):#'普通用户信息表'
    u_admin=models.ForeignKey(to='User',on_delete=models.SET_NULL,null=True,blank=True,verbose_name='用户id',related_name='u_admin',db_constraint=False)
    u_student = models.ForeignKey(to='Student', on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='学生', related_name='u_student', db_constraint=False)
    u_creatTime= models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    u_updateTime = models.DateTimeField(auto_now=True, verbose_name="更新时间")

class Notice(models.Model):#疫情通告表名
    notice_name = models.CharField(max_length=32, verbose_name='标题')
    notice_content = models.TextField(max_length=64, null=True,verbose_name='内容')
    notice_writer = models.ForeignKey(to='User',to_field='id', on_delete=models.CASCADE,verbose_name='发起人')   # 连接user表的主键
    notice_publishTime= models.DateTimeField(default=timezone.now,verbose_name="发布时间")
    notice_create_time = models.DateField(auto_now_add=True, verbose_name='创建时间')
    # def __str__(self):
    #     return self.notice_writer

class College(models.Model):#学院表名
    college_name = models.CharField(max_length=32, verbose_name='学院名')
    college_creatTime= models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    college_updateTime = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    def __str__(self):   #https://www.bilibili.com/video/BV1gV4y157ho?p=33&vd_source=81d62b71de3939c64a2d812ba8c4bd07 第33集18分钟
        return self.college_name

class Class(models.Model):#班级表名
    class_name = models.CharField(max_length=32, verbose_name='班级名')
    class_remark = models.CharField(max_length=64, null=True,verbose_name='班级备注')
    class_college_name = models.ForeignKey(to='College',to_field='id', on_delete=models.CASCADE,verbose_name='班级所属学院')   # 连接College表的主键
    class_creatTime= models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    class_updateTime = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    def __str__(self):
        return self.class_name

class Teacher(models.Model):#辅导员表名
    teacher_user_name = models.ForeignKey(to='User',to_field='id', on_delete=models.CASCADE,verbose_name='用户名')
    teacher_name = models.CharField(max_length=32, verbose_name='辅导员姓名')
    teacher_college_name = models.ForeignKey(to='College',to_field='id', on_delete=models.CASCADE,verbose_name='所属学院')#连接College表主键
    teacher_gender_choices=(
        (1,'男'),(2,'女'),
    )
    teacher_gender = models.SmallIntegerField(verbose_name='性别',choices=teacher_gender_choices,default=2)
    teacher_phone= models.CharField(max_length=11, verbose_name='手机号')
    def __str__(self):
        return self.teacher_name

class Student(models.Model):#学生表名
    student_user_name=models.ForeignKey(to='User',to_field='id', on_delete=models.CASCADE,verbose_name='用户名')
    student_name = models.CharField(max_length=32, verbose_name='学生姓名')
    student_gender_choices=(
        (1,'男'),(2,'女'),
    )
    student_gender = models.SmallIntegerField(verbose_name='性别',choices=student_gender_choices,default=1)
    student_phone= models.CharField(max_length=11,verbose_name='手机号')
    student_college_name = models.ForeignKey(to='College', to_field='id', on_delete=models.CASCADE,verbose_name='学院')     # 连接College表的主键
    student_class_name = models.ForeignKey(to='Class',to_field='id', on_delete=models.CASCADE,verbose_name='班级')          # 连接Class表的主键
    student_teacher_name = models.ForeignKey(to='Teacher',to_field='id', on_delete=models.CASCADE,verbose_name='辅导员')    # 连接Teacher表的主键
    student_create_time = models.DateField(auto_now_add=True, verbose_name='创建时间')
    def __str__(self):
        return self.student_name


# 我的健康   健康信息打卡    行程录入
class Filling(models.Model):#学生健康打卡报备
    filling_name=models.ForeignKey(to='Student',to_field='id', on_delete=models.CASCADE,verbose_name='报备者姓名')
    filling_temperature = models.CharField(max_length=32, verbose_name='报备者体温')
    filling_nucleic = models.ImageField(upload_to='nucleic/', verbose_name='核酸截图')
    filling_health_choices=(
        (1,'健康'),(2,'发烧/咳嗽'),(3,'其他'),
    )
    filling_health = models.SmallIntegerField(choices=filling_health_choices,default=1, verbose_name='报备者健康状况')#健康 发烧/咳嗽  其他
    filling_countVaccine_choices=(
        (1,0),(2,1),(3,2),(4,3),(5,4)
    )
    filling_countVaccine=models.SmallIntegerField(choices=filling_countVaccine_choices,default=1,verbose_name='疫苗针次')#0，1，2，3，4
    filling_remark = models.TextField(max_length=300,null=True, verbose_name='打卡备注')#是否在校等
    filling_time=models.DateField(auto_now=True,verbose_name='打卡时间')
    filling_create_time = models.DateField(auto_now_add=True, verbose_name='创建时间')


class Itinerary(models.Model):#行程录入
    itinerary_name=models.ForeignKey(to='Student',to_field='id', on_delete=models.CASCADE,verbose_name='姓名')
    itinerary_college_name = models.ForeignKey(to='College', to_field='id', on_delete=models.CASCADE,verbose_name='学院')  # 连接College表的主键
    itinerary_class_name = models.ForeignKey(to='Class', to_field='id', on_delete=models.CASCADE,verbose_name='班级')  # 连接Class表的主键
    itinerary_place = models.CharField(max_length=32, verbose_name='楼-宿舍号', default='13-2204')
    itinerary_time = models.DateField(default=datetime.datetime.now, verbose_name="返程时间")
    itinerary_trips = models.CharField(max_length=32, verbose_name='返程车次')
    itinerary_remark = models.TextField(max_length=300,null=True, verbose_name='打卡备注')#是否在校等
    itinerary_clock_time=models.DateField(auto_now=True,verbose_name='报备时间')
    itinerary_create_time = models.DateField(auto_now_add=True, verbose_name='创建时间')




#确诊管理     姓名 性别   学院  班级 宿舍楼号   确诊来源(食堂 外出 超市)  确诊时间





'''
1 用户列表 get 
2 用户新建 post 
3 用户详细 get 
4 删除用户 delete
5 修改用户 put
admin [1,2,3,4,5]
user  [1,2]
teacher [1,2,3]


'''



















'''
    类型
    AutoField:一个自动递增的整形字段，通常用于主键
    CharField：字符串字段，用于输入较短的字符，对应与HTML里面<input type='text'>
    TextField：文本字段，用于输入较多的字符，对应html标签 <input type = "textarea">；
    EmailField：邮箱字段，用于输入带有Email格式的字符
    DateFiled
    TimeFiled
    DateTimeField：日期字段，支持时间输入
    ImageField：用于上传图片并验证图片合法性，需定义upload_to参数，使用本字段需安装python pillow等图片库
    IntegerField：整数字段，用于保持整数信息
    
    属性
    primary_key：设置True or False，定义此字段是否为主键
    default：设置默认值，可以设置默认的文本、时间、图片、时间等
    null：设置True or False，是否允许数据库字段为Null，默认为False
    blank：设置True or False，定义是否运行用户不输入，默认为False；若为True，则用户可以不输入此字段
    max_length：设置默认长度，一般在CharField、TextField、EmailField等文本字段设置
    verbose_name：设置该字段的名称，所有字段都可以设置，在Web页面会显示出来（例如将英文显示为中文）
    choices：设置该字段的可选值，本字段的值是一个二维元素的元祖；元素的第1个值为实际存储的值，第2个值为HTML页面显示的值
    upload_to：设置上传路径，ImageField和FileField字段需要设置此参数,如果路径不存在，会自动创建
'''