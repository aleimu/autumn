# 动态地创建新类型动态创建新类型虽不是实用功能

>>> NewType = type("NewType", (object,), {"x": "hello"})
>>> n = NewType()
>>> n.x
"hello"
type的第一个参数就是类名,第二个参数是继承的父类,第三个参数是类的属性.它完全等同于:  
>>> class NewType(object):
>>>     x = "hello"
>>> n = NewType()
>>> n.x
"hello"

# 控制台不闪退
os.system('pause')

# 获取python安装路径
>>> from distutils.sysconfig import get_python_lib
>>> print get_python_lib
<function get_python_lib at 0x00000000024E0CF8>
>>> print get_python_lib()
D:\Python27\Lib\site-packages


进度条控制
{
链接：https://zhuanlan.zhihu.com/p/26459091

方案一

from __future__ import division
import sys,time
j = '#'
for i in range(1,61):
    j += '#'
    sys.stdout.write(str(int((i/60)*100))+'%  ||'+j+'->'+"\r")
    sys.stdout.flush()
    time.sleep(0.1)
方案二
import sys
import time
for i in range(1,61):
    sys.stdout.write('#'+'->'+"\b\b")
    sys.stdout.flush()
    time.sleep(0.5)
方案三
from progressbar import *
import time
import os
rows, columns = os.popen('stty size', 'r').read().split() #获取控制台size    
console_width=int(columns)
total = 10
progress = ProgressBar()

def test():
    '''
    进度条函数，记录进度
    '''
    for i in progress(range(total)):
        test2()

def test2():
    '''
    执行函数，输出结果
    '''
    content="nMask'Blog is http://thief.one"
    sys.stdout.write("\r"+content+" "*(console_width-len(content)))
    time.sleep(1)
    sys.stdout.flush()

test()
更多高级用法可以使用progressbar模块。
}

# 域名解析为ip

ip= socket.getaddrinfo(domain,'http')[0][4][0]
>>> ip= socket.getaddrinfo('www.baidu.com','http')[0][4][0]
>>> ip
'115.239.210.27'
>>> socket.getaddrinfo('www.baidu.com','http')
[(2, 1, 0, '', ('115.239.210.27', 80)), (2, 1, 0, '', ('115.239.211.112', 80))]

# isinstance(object, class-or-type-or-tuple) -> bool
>>> isinstance("123",(int,long,float,complex,str))
True


高级的历史粘贴版--快捷键 Ctrl+shift+v
双击shift即可召唤出来，超级搜索


组包与解包：
{
组包：python解释器自动将多个数据组装到一个容器中
解包：将容器中的多个数据拆出来
组包: 解释器把1,2,3自动组包成一个元组,然后赋值给a,a的类型就是元组类型的
　　a = 1,2,3 # 相当于 a = (1,2,3)
　　print(a) # (1, 2, 3)
　　print(type(a)) # <class 'tuple'>

#解包: 解释器会自动对元组(1,2)进行 解包,然后把1赋值给m,把2赋值给n，把3赋值给3
　　m,n,k = (1,2,3) # m=1,n=2,k=3
　　print(m) # 1
　　print(n) # 2
　　print(k) # 3 

函数使用参数可以使函数变得更加通用，增加扩展性。参数的顺序有讲究，定义函数时，【形参顺序】
def func(位置参数，可变位置参数，默认参数，可变关键字参数）：
　　pass

解包：func(*args,**kwargs) 与 func(args,kwargs）返回的数据不同，* 或者**具有解包的作用，*用来将普通参数元组解开，**用来将关键字参数字典解开。**kwargs只能在调用函数时使用。

# py3中可以这样操作,py2不行.
a = range(8)
print(*a) # 解包 0 1 2 3 4 5 6 7
b = [1,2,3]
print(*b) #1 2 3


 
}

https://flask-socketio.readthedocs.io/en/latest/#emitting-from-an-external-process

WS/WSS协议{

什么是WS/WSS？
WebSocket (WS)是HTML5一种新的协议。它实现了浏览器与服务器全双工通信，能更好地节省服务器资源和带宽并达到实时通讯。WebSocket建立在TCP之上，同HTTP一样通过TCP来传输数据，但是它和HTTP最大不同是：
WebSocket是一种双向通信协议，在建立连接后，WebSocket服务器和Browser/Client Agent都能主动的向对方发送或接收数据，就像Socket一样；WebSocket需要类似TCP的客户端和服务器端通过握手连接，连接成功后才能相互通信。
WSS（Web Socket Secure）是WebSocket的加密版本。

http -> new WebSocket('ws://xxx')
https -> new WebSocket('wss://xxx')
}
目前实时流媒体主流有三种实现方式：WebRTC、HLS、RTMP

业务上所谓的唯一往往都是不靠谱的，经不起时间的考研的。所以需要单独设置一个和业务无关的主键，专业术语叫做代理主键（surrogate key）。
{
https://www.cnblogs.com/davidwang456/p/10183183.html # 参考

# 数据库自增长序列或字段
最常见的方式。利用数据库，全数据库唯一。
优点：
1）简单，代码方便，性能可以接受。
2）数字ID天然排序，对分页或者需要排序的结果很有帮助。
 
缺点：
1）不同数据库语法和实现不同，数据库迁移的时候或多数据库版本支持的时候需要处理。
2）在单个数据库或读写分离或一主多从的情况下，只有一个主库可以生成。有单点故障的风险。
3）在性能达不到要求的情况下，比较难于扩展。
4）如果遇见多个系统需要合并或者涉及到数据迁移会相当痛苦。
5）分表分库的时候会有麻烦。
优化方案：
1）针对主库单点，如果有多个Master库，则每个Master库设置的起始数字不一样，步长一样，可以是Master的个数。比如：Master1 生成的是 1，4，7，10，Master2生成的是2,5,8,11 Master3生成的是 3,6,9,12。这样就可以有效生成集群中的唯一ID，也可以大大降低ID生成数据库操作的负载。

# UUID
常见的方式。可以利用数据库也可以利用程序生成，一般来说全球唯一。
优点：
1）简单，代码方便。
2）生成ID性能非常好，基本不会有性能问题。
3）全球唯一，在遇见数据迁移，系统数据合并，或者数据库变更等情况下，可以从容应对。
 
缺点：
1）没有排序，无法保证趋势递增。
2）UUID往往是使用字符串存储，查询的效率比较低。
3）存储空间比较大，如果是海量数据库，就需要考虑存储量的问题。
4）传输数据量大
5）不可读。

# Redis生成ID
当使用数据库来生成ID性能不够要求的时候，我们可以尝试使用Redis来生成ID。这主要依赖于Redis是单线程的，所以也可以用生成全局唯一的ID。可以用Redis的原子操作 INCR和INCRBY来实现。
可以使用Redis集群来获取更高的吞吐量。假如一个集群中有5台Redis。可以初始化每台Redis的值分别是1,2,3,4,5，然后步长都是5。各个Redis生成的ID为：
A：1,6,11,16,21
B：2,7,12,17,22
C：3,8,13,18,23
D：4,9,14,19,24
E：5,10,15,20,25
这个，随便负载到哪个机确定好，未来很难做修改。但是3-5台服务器基本能够满足器上，都可以获得不同的ID。但是步长和初始值一定需要事先需要了。使用Redis集群也可以方式单点故障的问题。
另外，比较适合使用Redis来生成每天从0开始的流水号。比如订单号=日期+当日自增长号。可以每天在Redis中生成一个Key，使用INCR进行累加。
 
优点：
1）不依赖于数据库，灵活方便，且性能优于数据库。
2）数字ID天然排序，对分页或者需要排序的结果很有帮助。
缺点：
1）如果系统中没有Redis，还需要引入新的组件，增加系统复杂度。
2）需要编码和配置的工作量比较大。


# 分布式唯一ID需要满足以下条件：
高可用性：不能有单点故障。
全局唯一性：不能出现重复的ID号，既然是唯一标识，这是最基本的要求。
趋势递增：在MySQL InnoDB引擎中使用的是聚集索引，由于多数RDBMS使用B-tree的数据结构来存储索引数据，在主键的选择上面我们应该尽量使用有序的主键保证写入性能。
时间有序：以时间为序，或者ID里包含时间。这样一是可以少一个索引，二是冷热数据容易分离。
分片支持：可以控制ShardingId。比如某一个用户的文章要放在同一个分片内，这样查询效率高，修改也容易。
单调递增：保证下一个ID一定大于上一个ID，例如事务版本号、IM增量消息、排序等特殊需求。
长度适中：不要太长，最好64bit。使用long比较好操作，如果是96bit，那就要各种移位相当的不方便，还有可能有些组件不能支持这么大的ID。
信息安全：如果ID是连续的，恶意用户的扒取工作就非常容易做了，直接按照顺序下载指定URL即可；如果是订单号就更危险了，竞争对手可以直接知道我们一天的单量。所以在一些应用场景下，会需要ID无规则、不规则。

}


再学 tornado的异步
{


tornado 是单线程的,部署服务应该通过Nginx代理多个tornado服务起的多个port.参考 http://demo.pythoner.com/itt2zh/ch8.html

tornado如何实现异步websocket推送？
在实现一个websocket的推送，主要就是后端推送pub/sub了redis的信息到前端。然而自己实现的推送开了两个chrome tab就有一个一直pending，可我明明在redis阻塞的部分用了gen.coroutine，一直不明白。想请问一下如何改进？

最近一直在研究Tornado异步操作，然而一番研究后发现要使一个函数异步化的最好方法就是采用相关异步库，但目前很多功能强大的库都不在此列。经过一番查找文档和搜索示范，终于发现了ThreadPoolExecutor模块和run_on_executor装饰器。用法就是建立线程池，用run_on_executor装饰的函数即运行在其中线程中，从而从主线程中分离出来，达到异步的目的。

gen.coroutine的意义，这个装饰器其实并不能让阻塞代码变成非阻塞，而是将本身需要异步回调的代码写成同步风格。它并不能改变什么，而是让你可以换一种代码风格增强代码可读性。整个tornado生态是基于它IOLoop的，所以不是拿到任何异步库都能直接使用，我们都知道异步是基于事件的，而事件的通知管理则是依靠事件轮询设施eventloop的它通常构建于select、epoll、kq，这个IOloop就是事件轮询设施，一切不能被它接纳的异步库都是无法集成到tornado的。所以如果你想把redis集成到tornado就必须是IOLoop能够接纳的非阻塞redis https://pypi.org/project/tornado-redis/2.4.2/

it.next() 仍然是阻塞的，Tornado 的异步模型应该是在你的 while True 里面 item = yield 一个future 才对，虽然你 yield 了一个 Task，但是这个 Task 本身不是异步的（等待的时候不能被打断，不能将控制权交给IOLoop）。

如果后端有查询实在是太慢，无法绕过，Tornaod的建议是将这些查询在后端封装独立封装成为HTTP接口，然后使用Tornado内置的异步HTTP客户端进行调用。



Tornado提供支持WebSocket的模块是tornado.websocket，其中提供了一个WebSocketHandler类用来处理通讯。
{

WebSocketHandler.open()
当一个WebSocket连接建立后被调用。

WebSocketHandler.on_message(message)
当客户端发送消息message过来时被调用，注意此方法必须被重写。

WebSocketHandler.on_close()
当WebSocket连接关闭后被调用。

WebSocketHandler.write_message(message, binary=False)
向客户端发送消息messagea，message可以是字符串或字典（字典会被转为json字符串）。若binary为False，则message以utf8编码发送；二进制模式（binary=True）时，可发送任何字节码。

WebSocketHandler.close()
关闭WebSocket连接。

WebSocketHandler.check_origin(origin)
判断源origin，对于符合条件（返回判断结果为True）的请求源origin允许其连接，否则返回403。可以重写此方法来解决WebSocket的跨域请求（如始终return True）。
}

链接：
https://tornado-zh.readthedocs.io/zh/latest/guide/intro.html
http://demo.pythoner.com/itt2zh/index.html
https://www.jianshu.com/p/3d20a092588d
https://www.zhihu.com/question/50043659/answer/119095429
https://www.zhihu.com/question/50043659/answer/119156752
https://github.com/leporo/tornado-redis/tree/master/demos # 对于不知道怎么异步调用那些异步库的可以参考这里
}


出现错误  TypeError: initialize() got an unexpected keyword argument 'io_loop'
原因：python环境中，默认tornado版本是最新的5.0，在4.0之后就废弃了io_loop参数。

解决方法：
    1、pip uninstall tornado
    2、pip install tornado==4.1





