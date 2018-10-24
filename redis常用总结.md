http://redisdoc.com/index.html  # Redis 命令参考大全 非常完整的api稳定，强烈推荐

https://www.cnblogs.com/renpingsheng/category/1317158.html # 总结的很完整的博客
https://www.cnblogs.com/renpingsheng/p/9783834.html
https://www.cnblogs.com/anpengapple/p/7027979.html  # 订阅与发布

https://www.jianshu.com/p/2639549bedc8  # 使用python来操作redis用法详解
https://www.cnblogs.com/zongfa/p/8029782.html   # Python操作Redis数据库

http://www.redis.cn/download.html   # 下载最新版本
https://blog.csdn.net/zgf19930504/article/details/51850594  # 安装步骤


tar xzf redis-4.0.11.tar.gz
cd redis-4.0.11
make install

cp /usr/local/bin/redis-server /usr/bin/redis-server
cp /usr/local/bin/redis-cli /usr/bin/redis-cli

# 配置 /etc/redis/redis.conf
daemonize yes
protected-mode no
bind 0.0.0.0

redis-server /etc/redis/redis.conf  # 启动

# Redis内部使用单线程架构。
SET key value [EX seconds] [PX milliseconds] [NX|XX]
EX second ：设置键的过期时间为 second 秒。 SET key value EX second 效果等同于 SETEX key second value 。
PX millisecond ：设置键的过期时间为 millisecond 毫秒。 SET key value PX millisecond 效果等同于 PSETEX key millisecond value 。
NX ：只在键不存在时，才对键进行设置操作。 SET key value NX 效果等同于 SETNX key value 。
XX ：只在键已经存在时，才对键进行设置操作。

help command        查看命令帮助
keys *              遍历所有key         # 在生产环境中，使用keys命令取出所有key并没有什么意义，而且Redis是单线程应用，如果Redis中存的key很多，使用keys命令会阻塞其他命令执行，所以keys命令一般不在生产环境中使用
keys [pattern]      遍历模式下所有的key
dbsize              计算Redis中所有key的总数
exists key              判断一个key是否存在
del key [key...]        删除指定的key-value
expire key seconds      设置key的过期时间，多少seconds后过期
ttl key                 查看key剩余的过期时间    # -2表示key已经不存在了 -1表示key存在，并且没有过期时间
persist key             去掉key的过期时间
type key            返回key的类型               # type的返回结果有6种：string,hash,list,set,zset,none


一次只运行一条命令
拒绝长(慢)命令 keys、flushall、flushdb、slow lua script、mutil/exec、operate
可以考虑使用scan迭代数据库
SCAN 命令用于迭代当前数据库中的数据库键。
SSCAN 命令用于迭代集合键中的元素。
HSCAN 命令用于迭代哈希键中的键值对。
ZSCAN 命令用于迭代有序集合中的元素（包括元素成员和元素分值）。

### redis 用setbit(bitmap)统计活跃用户

前提是了解bitmap的原理
bitmap是string类型，单个值最大可以使用的内存容量为512MB
Redis的 setbit(key, offset, value)操作对指定的key(偏移offset的位置)的value(1或0)，时间复杂度是O(1)。

针对每日统计当天登录的用户数,每一位标识一个用户ID。当某个用户访问我们的网页或执行了某个操作，就在bitmap中把标识此用户的位置为1。
在Redis中获取此bitmap的key值是通过用户执行操作的类型和时间戳获得的

简单的例子: 每次用户登录时会执行一次redis.setbit(daily_active_users, user_id, 1)。将bitmap中对应位置的位置为1，时间复杂度是O(1)。
统计bitmap结果显示有今天有9个用户登录。Bitmap的key是daily_active_users，它的值是1011110100100101也就是9个1.

针对统计日活跃用户数可以这样设置key-value: Redis.setbit(play:yyyy-mm-dd, user_id, 1)

#### bitop operation destkey key1 key2 key3 ......
对一个或多个保存二进制位的字符串 key 进行位元操作，并将结果保存到 destkey 上。
其中operation可以是AND（逻辑并）,OR(逻辑或),NOT(逻辑异或)，XOR(逻辑异或)

bitpos key targetBit [start] [end]  计算位图指定范围(start到end,单位为字节，如果不指定就是获取全部)第一个偏移量对应的值等于targetBit的位置


#### 数据
每天登录的用户(例如[1,3,5,8]代表，用户1,3,5,8登录过):

星期一[1,3,5,8]
星期一[1,3,5,7]
星期一[1,3,5]
星期一[1,2,3,4,5]
星期一[1,3,4,5]
星期一[1,3,5]
星期一[1,3,4,5,7]

#### 操作
{
127.0.0.1:6379> setbit mon 1 1
(integer) 0
127.0.0.1:6379> setbit mon 3 1
(integer) 0
127.0.0.1:6379> setbit mon 5 1
(integer) 0
127.0.0.1:6379> setbit mon 8 1
(integer) 0
127.0.0.1:6379> setbit tues 1 1
(integer) 0
127.0.0.1:6379> setbit tues 3 1
(integer) 0
127.0.0.1:6379> setbit tues 5 1
(integer) 0
127.0.0.1:6379> setbit tues 7 1
(integer) 0
127.0.0.1:6379> setbit wed 1 1
(integer) 0
127.0.0.1:6379> setbit wed 3 1
(integer) 0
127.0.0.1:6379> setbit wed 5 1
(integer) 0
127.0.0.1:6379> setbit thur 1 1
(integer) 0
127.0.0.1:6379> setbit thur 2 1
(integer) 0
127.0.0.1:6379> setbit thur 3 1
(integer) 0
127.0.0.1:6379> setbit thur 4 1
(integer) 0
127.0.0.1:6379> setbit thur 5 1
(integer) 0
127.0.0.1:6379> setbit fri 1 1
(integer) 0
127.0.0.1:6379> setbit fri 3 1
(integer) 0
127.0.0.1:6379> setbit fri 4 1
(integer) 0
127.0.0.1:6379> setbit fri 5 1
(integer) 0
127.0.0.1:6379> setbit sat 1 1
(integer) 0
127.0.0.1:6379> setbit sat 3 1
(integer) 0
127.0.0.1:6379> setbit sat 5 1
(integer) 0
127.0.0.1:6379> setbit sun 1 1
(integer) 0
127.0.0.1:6379> setbit sun 3 1
(integer) 0
127.0.0.1:6379> setbit sun 4 1
(integer) 0
127.0.0.1:6379> setbit sun 5 1
(integer) 0
127.0.0.1:6379> setbit sun 7 1
(integer) 0
127.0.0.1:6379> bitop and result  mon tues wed thur fri sat sun
(integer) 2
127.0.0.1:6379> BITCOUNT result
(integer) 3

}
从上次操作中，我们可以看出，连续登录一周的人数有3位。


https://blog.csdn.net/firenemymaster/article/details/77247649
hyperloglog算法: HLL的基本思想是利用集合中数字的比特串第一个1出现位置的最大值来预估整体基数，但是这种预估方法存在较大误差，为了改善误差情况，HLL中使用了分桶平均和调和平均数的概念。


http://redisdoc.com/topic/persistence.html  # 持久化

AOF 文件有序地保存了对数据库执行的所有写入操作， 这些写入操作以 Redis 协议的格式保存， 因此 AOF 文件的内容非常容易被人读懂， 对文件进行分析（parse）也很轻松。 导出（export） AOF 文件也非常简单： 举个例子， 如果你不小心执行了 FLUSHALL 命令， 但只要 AOF 文件未被重写， 那么只要停止服务器， 移除 AOF 文件末尾的 FLUSHALL 命令， 并重启 Redis ， 就可以将数据集恢复到 FLUSHALL 执行之前的状态。

appendonly yes

主从复制高可用的作用

1.为master提供备份，当master宕机时，slave有完整的备份数据
2.对master实现分流，实现读写分离
但是主从架构有一个问题
1.如果master宕机，故障转移需要手动完成或者由别的工具来完成，从slave中选择一个slave做为新的master
写能力和存储能力受限只能在一个节点是写入数据，所有数据只能保存在一个节点上


Redis Sentinel的功能：对Redis节点进行监控，故障判断，故障转移，故障通知
http://redisdoc.com/topic/sentinel.html

对于 redis-sentinel 程序， 你可以用以下命令来启动 Sentinel 系统：
redis-sentinel /path/to/sentinel.conf

对于 redis-server 程序， 你可以用以下命令来启动一个运行在 Sentinel 模式下的 Redis 服务器：
redis-server /path/to/sentinel.conf --sentinel


Sentinel 的状态会被持久化在 Sentinel 配置文件里面。
每当 Sentinel 接收到一个新的配置， 或者当领头 Sentinel 为主服务器创建一个新的配置时， 这个配置会与配置纪元一起被保存到磁盘里面。
这意味着停止和重启 Sentinel 进程都是安全的。


bind 0.0.0.0
port 6379
daemonize yes
pidfile "/var/run/redis_6379.pid"
logfile "/var/log/redis/redis_6379.log"
dir /etc/redis/date/redis_6379
sentinel monitor mymaster 172.16.4.120 6379 2
sentinel down-after-milliseconds mymaster 60000
sentinel failover-timeout mymaster 180000
sentinel parallel-syncs mymaster 1

sentinel monitor resque 172.16.4.120 6380 2
sentinel down-after-milliseconds resque 10000
sentinel failover-timeout resque 180000
sentinel parallel-syncs resque 2




bind 0.0.0.0
port 6380
daemonize yes
pidfile "/var/run/redis_6380.pid"
logfile "/var/log/redis/redis_6380.log"
dir /etc/redis/date/redis_6380
slaveof 172.16.4.120 6379
sentinel monitor mymaster 172.16.4.120 6379 2
sentinel down-after-milliseconds mymaster 60000
sentinel failover-timeout mymaster 180000
sentinel parallel-syncs mymaster 1



bind 0.0.0.0
port 6381
daemonize yes
pidfile "/var/run/redis_6381.pid"
logfile "/var/log/redis/redis_6381.log"
dir /etc/redis/date/redis_6381
slaveof 172.16.4.120 6379
sentinel monitor mymaster 172.16.4.120 6379 2
sentinel down-after-milliseconds mymaster 60000
sentinel failover-timeout mymaster 180000
sentinel parallel-syncs mymaster 1

sentinel monitor resque 172.16.4.120 6380 2
sentinel down-after-milliseconds resque 10000
sentinel failover-timeout resque 180000
sentinel parallel-syncs resque 2




redis-server sentinel_6379.conf --sentinel


环境：
redis服务3个实例6379,6380,6381
sentinel服务3个监控： 16379,16380,16381

protected-mode no 
# redis_config

bind 0.0.0.0
protected-mode no 
port 6379
daemonize yes
pidfile "/var/run/redis_6379.pid"
logfile "/var/log/redis/redis_6379.log"
dir /etc/redis/date/redis_6379


bind 0.0.0.0
port 6380
daemonize no 
pidfile "/var/run/redis_6380.pid"
logfile "/var/log/redis/redis_6380.log"
dir /etc/redis/date/redis_6380
slaveof 172.16.4.120 6379


bind 0.0.0.0
port 6381
daemonize no 
pidfile "/var/run/redis_6381.pid"
logfile "/var/log/redis/redis_6381.log"
dir /etc/redis/date/redis_6381
slaveof 172.16.4.120 6379


# entinel_config


port 26379
pidfile "/var/run/redis_26379.pid"
logfile "/var/log/redis/redis_26379.log"
dir /etc/redis/date/redis_26379
daemonize yes
protected-mode no 
sentinel monitor mymaster 172.16.4.120 6379 2
sentinel down-after-milliseconds mymaster 15000
sentinel failover-timeout mymaster 120000
sentinel parallel-syncs mymaster 1
#发生切换之后执行的一个自定义脚本：如发邮件、vip切换等
#sentinel notification-script <master-name> <script-path>

port 26380
pidfile "/var/run/redis_26380.pid"
logfile "/var/log/redis/redis_26380.log"
dir /etc/redis/date/redis_26380
daemonize yes
protected-mode no 
sentinel monitor mymaster 172.16.4.120 6379 2
sentinel down-after-milliseconds mymaster 15000
sentinel failover-timeout mymaster 120000
sentinel parallel-syncs mymaster 1


port 26381
pidfile "/var/run/redis_26381.pid"
logfile "/var/log/redis/redis_26381.log"
dir /etc/redis/date/redis_26381
daemonize yes
protected-mode no 
sentinel monitor mymaster 172.16.4.120 6379 2
sentinel down-after-milliseconds mymaster 15000
sentinel failover-timeout mymaster 120000
sentinel parallel-syncs mymaster 1




ps -ef|grep redis|awk '{print $2}' | xargs kill -9

redis-server redis_6379.conf 
redis-server redis_6380.conf 
redis-server redis_6381.conf 
redis-sentinel sentinel/sentinel_6379.conf 
redis-sentinel sentinel/sentinel_6380.conf 
redis-sentinel sentinel/sentinel_6381.conf
ps -ef|grep redis
redis-cli -h node1 -p 26379 info sentinel
redis-cli -p 26379 SENTINEL master mymaster
redis-cli -p 26379 SENTINEL slaves mymaster
redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster

