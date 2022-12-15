### a wheel of GAutomator：
https://github.com/Tencent/GAutomator

### 使用参考：hello_world.py

#
#### 主要改动：
##### 1.支持多进程控制多个设备
##### 2.优化了UI元素的搜索方式
##### 3.加入夜神模拟器的适配
##### 4.删除了不常用的功能，只支持本地运行
#
##### 分辨率适配方法：手动填入偏移量（从左往右），GA的sdk返回的是app的坐标，这个坐标与实际设备坐标不匹配，可以通过查看设备app窗口大小来映射坐标，实际上还是不够精准（需要研究设备屏幕原理），不如填入偏移量简单直接
#
#### 主要模块：
<img src="packages.png" alt="Drawing" width="900px" />


#### 详细：
<img src="classes.png" alt="Drawing" width="900px" />


#
#### 未完成的问题：
##### 1.手机开机后有一段时间不能获得activity
##### 2.多进程会造成初始化时候开启连接失效，需要在进程的函数里连接一次
