# -*- coding: utf-8 -*-
"""
@author: zhangwenping
Created on 2017-10-05 16:58

DNS Server 配置参考：
http://blog.csdn.net/chen1152/article/details/51115214
"""
from fabric.api import run
from fabric import operations

import utils
import conf
import time


rfc1912_template = """
zone "%s" IN {
\ttype master;
\tfile "%s";
\tallow-update { none; };
};
"""

zone_template = """$TTL 600
$ORIGIN %s.
@\tIN SOA \t%s. %s. (
\t\t\t\t\t%s
\t\t\t\t\t1H
\t\t\t\t\t5M
\t\t\t\t\t1W
\t\t\t\t\t10M )
\tIN NS\tdns
dns\tIN A\t%s
admin\tIN CNAME\tdns
"""


def dns_add_node(nodeip, short_dname):
    content = '%s\tIN A\t%s' % (short_dname, nodeip)
    run('echo %s >> %s' % (content, conf.zone_file))
    run('systemctl restart named.service')


def _create_zone_file(domains):
    zone = zone_template % (conf.domain_name, conf.dns_domain_name,
                            conf.admin_domain_name, time.strftime('%Y%m%d'),
                            conf.dns_server)
    for name, ip in domains.items():
        line = '%s\tIN A\t%s\n' % (name, ip)
        zone = zone + line

    with open(conf.zone_file, 'w') as fp:
        fp.write(zone)

    remote_file = '/var/named/'+conf.zone_file
    operations.put(conf.zone_file, remote_file)
    run("chown :named " + remote_file)
    run("chmod 640 " + remote_file)


def install_dns_server():
    # install bind
    run('yum install -y bind')
    run('yum install -y bind-utils')

    # modify /etc/named.conf
    utils.set_config_value(
        '/etc/named.conf',
        'listen-on port 53 { 127.0.0.1; };',
        'listen-on port 53 { 127.0.0.1; %s; };' % conf.dns_server)

    utils.set_config_value(
        '/etc/named.conf',
        'allow-query     { localhost; };',
        'allow-query     { localhost; any; };'
    )

    # modify rfc1912.zones
    rfc1912 = rfc1912_template % (conf.domain_name, conf.zone_file)
    utils.append_paragraph('/etc/named.rfc1912.zones',  rfc1912)

    # create zone file
    domains = {}
    for name, ip in conf.all_domain_nodes:
        domain = name + '.' + conf.domain_name
        domains[domain] = ip

    _create_zone_file(domains)

    # 检测配置文件有效性
    run('named-checkconf')
    run('named-checkzone "%s" /var/named/%s' % (conf.domain_name,
                                                conf.zone_file))

    # 启动服务
    run('systemctl enable named.service')
    run('systemctl start named.service')
