from django.urls import path,re_path
from django.views.static import serve
from CampusModule import views
from django.conf import settings
from django.conf.urls.static import static

app_name='campus'
urlpatterns=[

    path('register/', views.register),  # 注册
    path('login/',views.login),#登录
    path('base_zy/', views.base),  # 母版
    path('base_zy/index/', views.index),  # 主页



    path('base_zy/info_edit/',views.info_edit),  #资料编辑
    path('base_zy/info_account/',views.info_account),#账户绑定
    path('base_zy/info_pwd/',views.info_pwd),#密码修改
    # path('base_zy/admin_info/',views.AdminInfoView.as_view()),
    # path('base_zy/admin_info/(\d+)',views.AdminInfoView.as_view()),




    path('base_zy/hubei_data/',views.hubei_data),#湖北省
    path('base_zy/china_data/',views.china_data),#中国
    path('base_zy/world_data/',views.world_data),#世界

    path('base_zy/college_list/', views.college_list),  # 学院管理
    path('base_zy/college_add/', views.college_add),  # 学院新增
    path('base_zy/college_delete/', views.college_delete),  # 学院删除
    path('base_zy/<int:coid>/college_edit/', views.college_edit),  # 学院编辑    http:127.0.0.1:8000/campus/base_zy/100/college_edit/

    path('base_zy/notice_ajax/', views.notice_ajax),  # 疫情通告
    path('base_zy/<int:cid>/notice_cont/', views.notice_cont),  # 通告查看

    path('base_zy/notice_list/', views.notice_list),  # 疫情通告
    path('base_zy/notice_add/', views.notice_add),  # 疫情通告新增
    path('base_zy/<int:cid>/notice_edit/', views.notice_edit),  # 通告编辑
    path('base_zy/<int:cid>/notice_delete/', views.notice_delete),  # 通告删除

    path('base_zy/class_list/', views.class_list),  # 班级管理
    path('base_zy/class_add/', views.class_add),  # 班级新增
    path('base_zy/<int:cid>/class_edit/', views.class_edit),  # 班级编辑
    path('base_zy/<int:cid>/class_delete/', views.class_delete),  # 班级删除

    path('base_zy/teacher_list/', views.teacher_list),  # 教师管理
    path('base_zy/teacher_add/', views.teacher_add),  # 教师新增
    path('base_zy/<int:cid>/teacher_edit/',views.teacher_edit),  # 教师编辑
    path('base_zy/<int:cid>/teacher_delete/', views.teacher_delete),  # 教师删除

    path('base_zy/student_list/', views.student_list),  # 学生管理
    path('base_zy/student_add/', views.student_add),  # 学生新增
    path('base_zy/<int:cid>/student_edit/',views.student_edit),  #学生编辑
    path('base_zy/<int:cid>/student_delete/', views.student_delete),  # 学生删除


    path('base_zy/filling_list/', views.filling_list),  # 健康打卡管理
    path('base_zy/filling_add/', views.filling_add),  # 健康打卡管理
    path('base_zy/<int:cid>/filling_edit/', views.filling_edit),  # 健康打卡编辑
    path('base_zy/<int:cid>/filling_delete/', views.filling_delete),  # 健康打卡删除

    path('base_zy/itinerary_list/', views.itinerary_list),  # 行程管理
    path('base_zy/itinerary_add/', views.itinerary_add),  # 行程新增
    path('base_zy/<int:cid>/itinerary_edit/', views.itinerary_edit),  # 行程编辑
    path('base_zy/<int:cid>/itinerary_delete/', views.itinerary_delete),  # 行程删除


    path('base_zy/ajax_test/', views.ajax_test),
    re_path(r'^media/(?P<path>.*)$',serve,{"document_root":settings.MEDIA_ROOT},name='media')




]

            # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




