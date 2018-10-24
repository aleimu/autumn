https://www.cnblogs.com/wsjhk/p/8481280.html
https://www.cnblogs.com/kevingrace/p/5919021.html
https://www.cnblogs.com/yuhuLin/p/7018858.html
https://www.cnblogs.com/python-way/p/6110736.html

https://www.cnblogs.com/libin2015/p/8462567.html  # kibana6.2.2安装
https://blog.csdn.net/qq_28449663/article/details/79868334  # kibana界面汉化


input{  
    redis{  
        host=>"127.0.0.1"
        port=>6379
        type=>"redis-input"
        data_type=>"list"
        key=>"logstash:redis"
    }
}

output{
    stdout{}
    elasticsearch{
        host=>"127.0.0.1"
        port=>9200
        cluster=>"elasticsearch"
        codec=>"json"
        protocol=>"http"
    }  
}


echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" > /etc/apt/sources.list.d/webupd8team-java.list
echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu precise main" >> /etc/apt/sources.list.d/webupd8team-java.list
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886
apt-get update
apt-get install oracle-java8-installer


curl -i -X GET 'http://127.0.0.1:9200/_count?pretty' -d '{"query" {"match_all": {}}}'

filebeat监听数据源文件的新增内容经过logstash处理后上传到es里面
{

input {
    beats {
      port => "5044"
    }
}
output {
   elasticsearch {
   hosts => "172.16.220.248:9200"
  }
  stdout { codec => rubydebug }   # 这是将输出打印在屏幕上，可以注释掉
}



input {
    file {
        type => "example_nginx_access"
        path => ["/var/log/nginx/example.access.log"]
 
        start_position => "beginning"
        sincedb_path => "/dev/null"
    }
}

# 输出到redis
output {
    if [type] == "example_nginx_access" {
        redis {
            host => "127.0.0.1"
            port => "6379"
            data_type => "list"
            key => "logstash:example_nginx_access"
        }
      #  stdout {codec => rubydebug}
    }
}





input{
    file {
       type=>"nginx_access"
           path => "/var/log/nginx/access.log"
           start_position => "beginning"
       sincedb_path => "/data/info.txt"
  }
}

output{
    stdout{}
    if [type] == "nginx_access" {
        elasticsearch{
            host=>"127.0.0.1"
            port=>9200
            cluster=>"elasticsearch"
            codec=>"json"
            protocol=>"http"
            index => "nginx-access-%{+YYYY.MM.dd}"
        }  
    }
}


output {    
        elasticsearch {
        hosts => ["192.168.1.202:9200"]
        index => "system-%{+YYYY.MM.dd}"
        }
}

}

java -version
input来设置输入，output设置输出。stdin{} 是标准输入，elasticsearch { host => localhost }是输入到elasticsearch，stdout 是将内容输出到console， codec => rubydebug是以json形式输出。

/opt/logstash/bin/logstash -e "input {stdin{}} output{stdout{ codec=>"rubydebug"}}"  #检测环境  执行这个命令检测环境正常否，启动完成后控制台直接输入东西就会出现

./logstash agent --verbose -f conf/central.conf --log logs/stdout.log &

./logstash-1.5.4/bin/logstash agent --verbose -f ./conf/logstash_agent.conf &


http://172.16.4.120:5601


直接删除或备份Elasticsearch-a.b.c/lib目录下面的jna文件：
mv jna-4.4.0.jar jna-4.4.0.jar.bak
在lib目录下：
wget http://repo1.maven.org/maven2/net/java/dev/jna/jna/4.4.0/jna-4.4.0.jar
原文：https://blog.csdn.net/a_flying_bird/article/details/77657803?utm_source=copy 


# elk 版本较多，搭建的时候最好配套，不同组件版本可能出问题，语法也有差距
