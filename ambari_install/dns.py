# -*- coding: utf-8 -*-
"""
@author: zhangwenping
Created on 2017-10-05 16:58

DNS Server 配置参考：
http://blog.csdn.net/chen1152/article/details/51115214
"""
from fabric.api import run, cd
from fabric import operations

import utils
import conf
import time


rfc1912_template = """
zone "%(dname)s" IN {
\ttype master;
\tfile "%(zonefile)s";
\tallow-update { none; };
};

zone "%(subnet)s.in-addr.arpa" IN {
\ttype master;
\tfile "%(subnet)s.in-addr.arpa.zone";
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

reverse_zone_temp = """$TTL 600
$ORIGIN %(subnet)s.in-addr.arpa.
@ IN SOA dns.%(dname)s. admin.%(dname)s. (
\t\t\t\t\t%(date)s
\t\t\t\t\t1H
\t\t\t\t\t5M
\t\t\t\t\t1W
\t\t\t\t\t10M )
\tIN NS dns.%(dname)s.
%(dns_ip)s \tIN PTR dns.%(dname)s.
"""


def _get_sub_net(subnet, netmask):
    n = netmask.split('.').count('255')
    split = subnet.split('.')
    return '.'.join([split[n-x-1] for x in range(n)])


def _get_sub_ip(ip, netmask):
    n = 4 - netmask.split('.').count('255')
    split = ip.split('.')
    return '.'.join([split[3-x] for x in range(n)])


def dns_add_node(nodeip, short_dname):
    substr = _get_sub_net(conf.subnet, conf.netmask)
    subip = _get_sub_ip(nodeip, conf.netmask)
    dname = '.'.join(short_dname, conf.domain_name)
    reverse_file = "%s.in-addr.arpa.zone" % substr

    ns = '%s\tIN A\t%s' % (short_dname, nodeip)
    reverse = '%s\tIN PTR %s.' % (subip, dname)

    with cd('/var/named/'):
        run('echo %s >> %s' % (ns, conf.zone_file))
        run('echo %s >> %s' % (reverse, reverse_file))

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


def _create_reverse_file(domains):
    substr = _get_sub_net(conf.subnet, conf.netmask)
    info = {
        'subnet': substr,
        'dname': conf.domain_name,
        'dns_ip': _get_sub_ip(conf.dns_server, conf.netmask),
        'date': time.strftime('%Y%m%d')
    }
    reverse = reverse_zone_temp % info
    reverse_file = "%s.in-addr.arpa.zone" % substr

    for name, ip in domains.items():
        subip = _get_sub_ip(ip, conf.netmask)
        line = '%s\tIN PTR %s.\n' % (subip, name)
        reverse = reverse + line

    with open(reverse_file, 'w') as fp:
        fp.write(reverse)

    remote_file = '/var/named/'+reverse_file
    operations.put(reverse_file, remote_file)
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
    netstr = _get_sub_net(conf.subnet, conf.netmask)
    info = {
        'dname': conf.domain_name,
        'zonefile': conf.zone_file,
        'subnet': netstr
    }
    rfc1912 = rfc1912_template % info
    utils.append_paragraph('/etc/named.rfc1912.zones',  rfc1912)

    # create zone file
    domains = {}
    for name, ip in conf.all_domain_nodes:
        domain = name + '.' + conf.domain_name
        domains[domain] = ip

    _create_zone_file(domains)
    _create_reverse_file(domains)

    # 检测配置文件有效性
    run('named-checkconf')
    run('named-checkzone "%s" /var/named/%s' % (conf.domain_name,
                                                conf.zone_file))

    substr = _get_sub_net(conf.subnet, conf.netmask)
    reverse = "%s.in-addr.arpa" % substr
    reverse_file = "/var/named/%s.in-addr.arpa.zone" % substr
    run('named-checkzone "%s" %s' % (reverse, reverse_file))

    # 启动服务
    run('systemctl enable named.service')
    run('systemctl start named.service')
