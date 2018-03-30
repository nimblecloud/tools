# -*- coding: utf-8 -*-
"""
@author: zhangwenping
Created on 2017-10-05 16:58
"""

from fabric.api import execute, env
from fabric.api import runs_once, task, hosts
from utils import parallel

import conf
import repo
import pxe
import ssh_pass
import hostinit
import dns
import ntp
import psql
import ambari

env.user = conf.username
env.password = conf.password
# env.passwords = conf.passwords

"""
执行步骤：
1、准备工作
选一个节点作为repo_server，然后：

1）上传脚本和res到repo_server，复制并修改conf文件，根据集群规划修改
2）执行
cd res; sh install_fabric.sh
cd ..; fab install


单步执行：
0、sh install_fabric.sh
1、配置repo
fab setup_ambari_repo

2、配置免密
fab setup_ssh_no_password

3、配置host
fab setup_host

4、配置dns
fab install_dns_server

5、配置ntp
fab setup_ntp


6、配置postgresql
fab install_postgresql_server

7、安装ambari-server
fab setup_ambari_server

8、登录Web控制台

新加节点流程：
1、配置免密
fab ssh_no_password_addnode
2、配置host
fab host_addnode:short_dname
3、配置dns
fab dns_addnode:short_dname
4、配置ntp
fab ntp_addnode
5、登录web控制台


问题解决：
首先最好通过界面来进行服务的启动、停止。

1）手动启动webhcat（端口：50111）
/usr/hdp/2.6.2.0-205/hive-hcatalog/sbin/webhcat_server.sh start

2）手动启动falcon（端口：15000）
/usr/hdp/2.6.2.0-205/falcon/bin/falcon-start

3）15000端口访问报503
HTTP 503 response from http://node1.bigdata.yourcompany.com:15000 in 0.000s (HTTP Error 503: Service Unavailable)

查看日志：/var/log/falcon/falcon.application.log
Permission denied: user=root, access=WRITE, inode="/apps/falcon/extensions":hdfs:hdfs:drwxr-xr-x
看起来像依赖HDFS

4）手动启动hbase（端口16000）
目录：/usr/hdp/2.6.2.0-205/hbase/bin
启动master命令：sh hbase master start
hbase似乎依赖hdfs：Permission denied: user=root, access=WRITE, inode="/apps/hbase/data/.tmp":hbase:hdfs:drwxr-xr-x

另外：/var/log/hbase/hbase-hbase-master-ambari.bigdata.yourcompany.com.log
master.HMaster: Namespace manager failed to start.

先解决HDFS报警。

5）手动启动grafana-server（端口3000）
/usr/sbin/ambari-metrics-grafana start
"""


# ----------------- repo -------------------------
@task
@runs_once
def create_ambari_repo_file():
    repo.create_repo_file()


@task
@hosts(tuple(conf.all_hosts))
@parallel
def upload_ambari_repo_file():
    repo.upload_ambari_repo_file()


@task
def repo_addnode():
    repo.upload_ambari_repo_file()


@task
@hosts((conf.repo_server))
def run_http_server_on_repo_node():
    repo.setup_simple_http_server()


@task
@runs_once
def setup_ambari_repo():
    execute(create_ambari_repo_file)
    execute(upload_ambari_repo_file)
    execute(run_http_server_on_repo_node)


# ----------------- pxe install ---------------------
@task
@hosts((conf.repo_server))
def setup_pxe():
    pxe.setup_pxe()


# ----------------- ssh key -------------------------
@task
@hosts((conf.ambari_server,))
def ssh_gen_key():
    ssh_pass.ssh_gen_rsa_key()


@task
@hosts(tuple(conf.all_hosts))
@parallel
def ssh_no_password():
    ssh_pass.ssh_no_password()


@task
def ssh_no_password_addnode():
    ssh_pass.ssh_no_password_add_node()


@task
@runs_once
def setup_ssh_no_password():
    execute(ssh_gen_key)
    execute(ssh_no_password)


# ----------------- host init -------------------------
def _setup_host(hostname=None):
    hostinit.local_setup()
    hostinit.disable_networkmanager()
    hostinit.stop_firewalld()
    hostinit.disable_selinux()
    hostinit.dns_setup()
    hostinit.set_hostname(hostname)
    hostinit.swap_config()
    hostinit.uninstall_some_package()


@task
@hosts(tuple(conf.all_hosts))
@parallel
def setup_host():
    _setup_host()


@task
def host_addnode(short_dname):
    hostname = short_dname + '.' + conf.domain_name
    _setup_host(hostname)


# ----------------- dns -------------------------
@task
@hosts((conf.dns_server,))
def install_dns_server():
    dns.install_dns_server()


@task
@hosts((conf.dns_server))
def dns_addnode(short_dname):
    dns.dns_add_node(env.host_string, short_dname)


# ----------------- ntp -------------------------
@task
@hosts((conf.ntp_server))
def ntp_install_server():
    ntp.install_ntp_server()


@task
@hosts(tuple(conf.all_hosts))
@parallel
def ntp_install_client():
    ntp.install_ntp_client()


@task
@runs_once
def setup_ntp():
    execute(ntp_install_server)
    execute(ntp_install_client)


@task
def ntp_addnode():
    ntp.install_ntp_client()


# ----------------- postgresql -------------------------
@task
@hosts((conf.db_server))
def install_postgresql_server():
    psql.install_postgresql_server()
    psql.create_ambari_postgres_db()
    psql.create_hive_postgres_db()
    psql.create_oozie_postgres_db()


# ----------------- ambari server -------------------------
@task
@hosts((conf.ambari_server))
def ambari_server_install():
    ambari.install_ambari_server()


@task
@hosts((conf.db_server))
def ambari_db_init():
    ambari.init_ambari_db()


@task
@hosts((conf.ambari_server))
def ambari_server_init():
    ambari.init_ambari_server()


@task
@runs_once
def setup_ambari_server():
    execute(ambari_server_install)
    execute(ambari_db_init)
    execute(ambari_server_init)


@task
@runs_once
def install(skipssh=''):
    if not skipssh:
        execute(setup_ssh_no_password)
    execute(setup_ambari_repo)
    execute(setup_host)
    execute(install_dns_server)
    execute(setup_ntp)
    execute(install_postgresql_server)
    execute(setup_ambari_server)


@task
@hosts((conf.db_server))
def re_init_db():
    psql.create_ambari_postgres_db()
    psql.create_hive_postgres_db()
    psql.create_oozie_postgres_db()
