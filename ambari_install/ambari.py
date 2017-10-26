# -*- coding: utf-8 -*-
"""
@author: zhangwenping
Created on 2017-10-05 16:58
"""
import sys

from fabric.api import run
from fabric import operations

import psql
import conf
import utils


def install_ambari_server(): 
    run('yum install ambari-server -y')

    # 复制DLL SQL脚本到DB节点
    run('scp /var/lib/ambari-server/resources/Ambari-DDL-Postgres-CREATE.sql'
        ' %s:/var/lib/pgsql/' % conf.db_server)

    operations.put('res/jdk-8u112-linux-x64.tar.gz',
                   '/var/lib/ambari-server/resources/')
    operations.put('res/jce_policy-8.zip',
                   '/var/lib/ambari-server/resources/')
    operations.put('res/postgresql-jdbc.jar',
                   '/var/lib/ambari-server/resources/')
    operations.put('res/je-5.0.73.jar',
                   '/var/lib/ambari-server/resources/')


# 在数据库服务器上执行
def init_ambari_db():
    psql.run_sql_file('/var/lib/pgsql/Ambari-DDL-Postgres-CREATE.sql',
                      'ambari', conf.ambari_username, conf.ambari_password)


def _print_all_hostname():
    for ip in conf.all_hosts:
        print utils.get_domain_name_by_ip(ip)


def _print_all_dname():
    for name, ip in conf.all_domain_nodes:
        print '.'.join([name, conf.domain_name])


def init_ambari_server():
    run('ambari-server setup --jdbc-db=postgres '
        '--jdbc-driver=/usr/lib/ambari-server/postgresql-9.3-1101-jdbc4.jar')        

    print('-----------------------------------------------------------------')
    print('--------------- OK! ambari server install success! --------------')
    print('-----------------------------------------------------------------')
    print('')
    print('- All hostnames you can use for web wizard:')
    _print_all_hostname()
    print('')

    print('- All domain names:')
    _print_all_dname()
    print('')

    print('- All repo you can use:')
    print('http://%s/HDP/centos7' % conf.repo_server)
    print('http://%s/hdputils' % conf.repo_server)
    print('')

    print('- Next todo:')
    print('1: check domain name is ok first.')
    print('2: manually run `ambari-server setup` on %s'
          % conf.ambari_server)
    print('-----------------------------------------------------------------')
    sys.exit(1)

    class mydict(dict):
        def __init__(self, *arg, **kw):
            super(mydict, self).__init__(*arg, **kw)
            self.choiced = False
            self.choice_prompt = 'Enter choice (1): '

        def __getitem__(self, name):
            if name == self.choice_prompt:
                if not self.choiced:
                    self.choiced = True
                    return ''

            return super().__getitem__(name)

    prompts = {
        'Customize user account for ambari-server daemon [y/n] (n)? ': 'n',
        'Enter choice (1): ': '4',
        'Enter advanced database configuration [y/n] (n)? ': 'y',
        'Hostname (localhost): ': conf.db_domain_name,
        'Port (5432): ': '',
        'Database name (ambari): ': '',
        'Postgres schema (ambari): ': '',
        'Username (ambari): ': conf.db_username,
        'Enter Database Password (bigdata): ': conf.db_password,
        'Re-enter password: ': conf.db_password,
        'Proceed with configuring remote database connection properties [y/n] (y)? ': 'y'
    }

    prompts = mydict(prompts)