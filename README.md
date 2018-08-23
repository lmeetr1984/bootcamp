# bootcamp-chinese-learner

fork from https://github.com/vitorfs/bootcamp

这个项目是我学习Django的clone的第一个项目

### features:

1. 所有源代码都加了中文注释
2. 修改了Tag：
	- 之前的Tag是一对多的，所以Tag名字重复的话，会被创建多条记录；
	- 现在是多对多的，同一个Tag名字只会创建一条记录。
3. 增加了django_extensions支持: 便于在控制台调试模型。
4. 增加了clean脚本，这样Django建模的时候，出现错误可以快速的重置数据库，重新生成migrations。

### 安装：

1. (可选)创建vritual env:
	- 创建一个文件夹(注意不要在工程目录下创建), 进入
	- virtualenv bootcamp
	- source ./bootcamp/bin/active
2. 安装组件:
	- (可选)最好先配置好国内的pip阿里源
	- pip install -r requirements.txt
3. migrations:
	- cd bootcamp-chinese-learner-master
	- chmod 755 *.sh
	- ./clean.sh
	- ./manage.py reset_db
	- ./manage.py makemigrations
	- ./manage.py migrate
4. 运行
	- ./manage.py runserver

浏览器访问: http://localhost:8000/

### TODO:

1. add cache support
