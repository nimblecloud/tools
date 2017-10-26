# -*- coding: utf-8 -*-
"""
@author: zhangwenping
Created on 2015-06-02 16:58
"""
import os
import sys
import ConfigParser
from functools import wraps

import conf
from fabric.api import run
from fabric import operations


def support_parallel():
    if sys.platform == 'win32':
        return False
    return True


def get_domain_name_by_ip(ip):
    for dname, nodeip in conf.all_domain_nodes:
        if nodeip == ip:
            return dname + '.' + conf.domain_name


def run_mysql(str_sql):
    run('mysql -uroot -p%s -e "%s"' % (conf.mysql_root_password, str_sql))


def set_config_value(conf_file, search, replace):
    run("sed -i 's/.*%s.*/%s/g' %s" % (search, replace, conf_file))


def insert_after(conf_file, search, value):
    run("sed -i '/%s/a %s' %s" % (search, value, conf_file))


def append_paragraph(conf_file, p):
    with open('temp.conf', 'w') as fp:
        fp.write(p)

    operations.put('temp.conf', '/var/tmp/')
    run('cat /var/tmp/temp.conf >> ' + conf_file)


def backup_config_file(conf_file):
    run('mv %s %s.orig' % (conf_file, conf_file))


def write_conf_file(confs, conf_file, insert=True):
    """
    {
        "SectionName1": {key: value,},
        "SectionName2": {key: value,},
    }
    """
    config = ConfigParser.RawConfigParser()
    if os.path.exists(conf_file) and insert:
        config.read(conf_file)

    for section, values in confs.iteritems():
        if section != 'DEFAULT' and not config.has_section(section):
            config.add_section(section)
        for key, value in values.iteritems():
            config.set(section, key, value)

    config.set('DEFAULT', 'fabric', 'true')

    with open(conf_file, 'wb') as fp:
        config.write(fp)


def prepare_conf_file(conf_file):
    paths = operations.get(conf_file)
    path = paths[0]
    config = ConfigParser.RawConfigParser()
    config.read(path)

    fabric = True if config.has_option('DEFAULT', 'fabric') else False
    return path, fabric


def modify_configurations(conf_file, confs):
    local_path, fabric = prepare_conf_file(conf_file)

    # fabric 表示配置文件是我们生成的，因此需要改此配置时只能插入新配置
    confs['DEFAULT'].update({'fabric': 'true'})
    write_conf_file(confs, local_path, fabric)

    if not fabric:
        backup_config_file(conf_file)
    operations.put(local_path, conf_file)


def noop_parallel(func):
    # NOTE: 不支持pool_size参数，该函数主要是为了规避win32不支持并行的bug
    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    return inner

if support_parallel():
    from fabric.api import parallel
else:
    parallel = noop_parallel
