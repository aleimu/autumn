通俗的讲就是能否通过&操作符找到对应的内存地址。array/slice的元素是可寻址的（可以通过&arr[index]找到对应元素的内存地址），
所以可以直接操作元素的值；map的值是不可寻址的（无法通过&map[key]找到key对应的value的内存地址，但如果v:=map[key]; &v就是可寻址的，因为所有变量都是可寻址的），所以不可以直接操作值里面的值；如果想实现修改的目的，把map的值换成指针即可，要是还不能理解，
就这么想，编译器找不到map[key]对应value的内存地址，那么我们就让value本身就是一个地址（指针）好了，按照题主的代码，即
//map
b := map[int]*test{1: &test{1}, 2: &test{2}, 3: &test{3}}
b[1].a = 33 // ok
fmt.Println(b[1])


# 链接：https://www.jianshu.com/p/21db18e2c1e3

调大uwsgi配置中 listen=1024的数目是提高并发能力最有效的办法。第二种方法是调大processes数目

（1）首先，uwsgi观察到上面的负载不均衡，第7个线程负责的请求数远大于其他的。调整使之均衡
（2）再机器能力足够的情况下，增加线程数目
（3）建立uwsgi集群，在另外一台机器上也部署此服务，并让nginx转发部分到此


1.Linux默认参数的一些优化
    sysctl net.core.somaxconn=1024 #此参数默认为128，不更改uwsgi的监听队列不能大于这个值
2. swap空间使用
    阿里云镜像默认是没有开swap分区的，偶尔峰值的时候就会出现out of memory的错误，增加swap分区能有效的避免这个情况，并设置swap分区的使用前提
    sysctl vm.swappiness=10 #物理内存还剩10%的时候开始使用虚拟内存
    网上普遍开辟虚拟空间的做法
    dd if=/dev/zero of=swapfile bs=1024 count=400000 
    在一篇网管日志中看到还可以这样，速度比上面的方式要快很多很多哦
    fallocate -l 4G /swapfile

3. uwsgi协程支持
    在有频繁IO的情况下，uwsgi的性能会打折扣，threads参数可以增加并发，但是性能开销很大,使用gevent可以在不修改代码的情况下大大增强并发，（道听途说：stackoverflow上说threads开到1000,基本吃空内存，gevent则表现很好）
    使用协程示例，在高并发下推荐使用
    uwsgi --http :8001 --module ugtest.wsgi --gevent 40 --gevent-monkey-patch

    使用线程示例，并发不高可以使用，高并发不适用
    uwsgi --http :8001 --module ugtest.wsgi --enable-threads --threads 40

4. nginx访问控制
    由于服务器并不强大，在高峰期间遭到恶意访问时会造成listen队列被填满，正常用户无法访问，在nginx.conf中添加
    limit_req_status 599; #定义被限制的返回码，便于和正常的区分
        limit_req_zone $binary_remote_addr zone=allips:2m rate=100r/s; #nginx每秒仅接受100个请求
        geo $limited { #设定不受限制的IP
            default 1;
            182.92.117.23 0;
        }
    在应用的config中的location / 段添加，个人感觉这段和uwsgi的listen做的事差不多，只是在nginx层做效率应该比uwsgi层效率要高。
    location / {
            ...
            limit_req zone=allips burst=60 nodelay; #达到限速后，允许等待的请求数
    }
    

# uwsgitop监控uwsgi 性能
一、安装 uwsgitop:
    pip install uwsgitop
二、uwsgi 命令 加参数
    --stats /tmp/stats.socket
三、调用uwsgitop
    uwsgitop /tmp/stats.socket


ab -r -n 100 -c 100 "http://camel_dev.yoohoor.com:5009/api/lines/char?token=5595f26c-e7cf-11e8-86d3-00163e06%E4%B8%AD%E6%96%87%E8%B4%A6%E5%8F%B7&page_index=1&page_size=10&line_name=&line_no="

root@iZ282hpfj1mZ:~/new_test_01/servers/sub_operation/backend_oper# cat op_test.ini 
[uwsgi]
module = wsgi

master = true
processes = 4
threads = 3
socket = op_test_01.sock
chmod-socket = 660
vacuum = true
plugins = python
die-on-term = true


# uwsgi --ini op_test.ini --daemonize /root/new_test_01/servers/logs/op_test.log --stats /tmp/stats.socket

# uwsgitop /tmp/stats.socket

# 测试命令与结果
root@(none):~# ab -n 10 -c 10 "http://camel_dev.yoohoor.com:5009/api/lines/char?token=5595f26c-e7cf-11e8-86d3-00163e06%E4%B8%AD%E6%96%87%E8%B4%A6%E5%8F%B7&page_index=1&page_size=10&line_name=&line_no="
This is ApacheBench, Version 2.3 <$Revision: 1528965 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking appdrivert1.yoohoor.com (be patient)...
..done


Server Software:        nginx/1.4.6
Server Hostname:        appdrivert1.yoohoor.com
Server Port:            5007
SSL/TLS Protocol:       TLSv1.2,ECDHE-RSA-AES128-GCM-SHA256,2048,128

Document Path:          /v1/report/generate?token=3fcfe52a-dcab-11e8-86d3-00163e050a03&username=00999999&start_time=2018-10-24+14%3A55&end_time=2018-10-31+09%3A31&comt_type=1&role=2&fk_location_code=999999&operator=%E6%80%BB%E8%B0%83   ###请求的资源
Document Length:        42 bytes     ###文档返回的长度，不包括相应头

Concurrency Level:      10  ###并发个数
Time taken for tests:   22.301 seconds  ###总请求时间
Complete requests:      10  ###总请求数
Failed requests:        0   ###失败的请求数
Total transferred:      4590 bytes
HTML transferred:       420 bytes
Requests per second:    0.45 [#/sec] (mean) ###平均每秒的请求数
Time per request:       22300.902 [ms] (mean)   ###平均每个请求消耗的时间
Time per request:       2230.090 [ms] (mean, across all concurrent requests)    ###上面的请求除以并发数
Transfer rate:          0.20 [Kbytes/sec] received  ###传输速率



# window下ab工具的安装
https://blog.csdn.net/qq_26525215/article/details/79182674




