import pymysql

DataBases=pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='8023',
    # charset='utf8mb4'
)

cursor=DataBases.cursor()                   #创建游标对象

sql1=' create database if not exists Epidemic_situation;' #sql语句
cursor.execute(sql1)                        #执行sql语句
#
# sql2='use Epidemic_situation;'
# cursor.execute(sql2)
#
# sql3 = """
#     create table if not exists user(
#         id  int comment '编号'  not null,
#         name varchar(20) comment '用户名' not null,
#         password varchar(18) comment '密码' not null
#     ) comment '用户';
# """
# cursor.execute(sql3)
#
# # 定义要执行的sql语句
# sql4 = 'insert into user(id,name,password) values(%s,%s,%s);'
# data = [
#     (1,'zy', '147'),
#     (2,'dzy', '258'),
#     (3,'dsd', '369')
# ]
# # 拼接并执行sql语句
# cursor.executemany(sql4, data)
# # 涉及写操作要注意提交
# DataBases.commit()
#
# sql5='drop table if exists user;'
# sql6=' drop database if exists Epidemic_situation;'
# cursor.execute(sql5)
# cursor.execute(sql6)

cursor.close()                              #关闭游标对象
DataBases.close()                           #关闭数据库的连接





