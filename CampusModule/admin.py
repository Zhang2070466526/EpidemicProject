from django.contrib import admin

# Register your models here.


from CampusModule.models import *
admin.site.register([User,College,Class,HubeiData,ChinaData,WorldData,Notice,Teacher,Student,Filling,Itinerary,Admin_info])



#python manage.py createsuperuser  #创建用户名和密码

'''
admin
zy177177
'''