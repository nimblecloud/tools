# -*- coding: utf-8 -*-

username = 'root'
password = '111111'

# NET Work，注意这里最好单独一个网段
# netmask只能是8/16/24段，一般用24就够用，即：255.255.255.0
subnet = ''
netmask = '255.255.255.0'

# node ip conf
ambari_server = '192.168.10.100'
dns_server = '192.168.10.100'
db_server = '192.168.10.100'
ntp_server = '192.168.10.100'
repo_server = '192.168.10.100'

all_hosts = ['1.1.1.1']


# dns config
domain_name = 'bigdata.yourcompany.com'

zone_file = domain_name + '.zone'

dns_domain_name = 'dns.' + domain_name
admin_domain_name = 'admin.' + domain_name
ntp_domain_name = 'ntp.' + domain_name
db_domain_name = 'db.' + domain_name

# 除了dns server之外的其他节点的域名和IP映射关系
# 注意：域名用缩写，即不用带后面的主域名。
# 如果一个IP对应很多角色，则将最重要的或者相对抽象的名字往前方，
# 该名字将作为此节点的hostname
# 必须配置的域名：ambari、ntp
all_domain_nodes = [
    ('ambari', '192.168.10.100'),
    ('ntp', '192.168.10.100'),
    ('db', '192.168.10.100'),
    ('node1', '192.168.10.11'),
    ('node2', '192.168.10.12'),
]


# postgresql config
ambari_username = 'ambari'
ambari_password = 'ambari'
hive_username = 'hive'
hive_password = 'hive'
oozie_username = 'oozie'
oozie_password = 'oozie'

psql_admin_password = 'bigdata'

# setup centos iso local repo
setup_iso = False

# check
if subnet == '':
    raise Exception("Sorry, you need modify the conf.py first.")

if setup_iso:
    import os
    if not os.path.exists('res/CentOS-7-x86_64-Everything-1611.iso'):
        raise Exception("Please upload iso file to `res` directory")
