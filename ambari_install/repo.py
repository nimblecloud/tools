# -*- coding: utf-8 -*-
"""
@author: zhangwenping
Created on 2017-10-05 16:58
"""

import conf
import utils

from fabric.api import run, cd, settings
from fabric import operations
from fabric.contrib.files import exists

REPO = """[ambari]
name=ambari
baseurl=http://%s/ambari/centos7/
enabled=1
gpgcheck=0
"""

HTTP_TEMP = """[iso]
name=iso
baseurl=http://%(repo_server)s/iso
enabled=1
gpgcheck=0
"""


def create_local_http_file():
    if not conf.setup_iso:
        return

    repo_content = HTTP_TEMP % {'repo_server': conf.repo_server}
    with open('res/local_http.repo', 'w') as fp:
        fp.write(repo_content)


def create_ambari_repo_file():
    repo_content = REPO % conf.repo_server
    with open('res/ambari.repo', 'w') as fp:
        fp.write(repo_content)


def create_repo_file():
    create_local_http_file()
    create_ambari_repo_file()


def setup_iso():
    if not conf.setup_iso:
        return

    if not exists('/root/repo/CentOS-7-x86_64-Everything-1611.iso'):
        operations.put('res/CentOS-7-x86_64-Everything-1611.iso', '/root/repo')

    run('mkdir -p /root/repo/iso')
    fstab = ("/root/repo/CentOS-7-x86_64-Everything-1611.iso /root/repo/iso"
             " iso9660 defaults,ro,loop 0 0")
    run('echo "%s" >> /etc/fstab' % fstab)
    run('mount -a')


def setup_simple_http_server():
    if not exists('/root/repo/ambari-2.5.2.0-centos7.tar.gz'):
        operations.put('res/ambari-2.5.2.0-centos7.tar.gz', '/root/repo')
    if not exists('/root/repo/yum.tar.gz'):
        operations.put('res/yum.tar.gz', '/root/repo')

    setup_iso()

    run('chown apache:apache /root/repo')

    with cd('/root/repo'):
        run('tar vxf ambari-2.5.2.0-centos7.tar.gz')

    operations.put('res/repo_http.conf', '/etc/httpd/conf.d')
    utils.set_config_value('/etc/httpd/conf/httpd.conf',
                           'IncludeOptional conf.d\/\*.conf',
                           'IncludeOptional conf.d\/repo_http.conf')

    run('chmod +x /root')

    with settings(warn_only=True):
        run('systemctl enable httpd')
        run('systemctl restart httpd')


def upload_ambari_repo_file():
    if not exists('/etc/yum.repos.d.bak'):
        run('mv /etc/yum.repos.d /etc/yum.repos.d.bak')
        run('mkdir -p /etc/yum.repos.d')
    operations.put('res/ambari.repo', '/etc/yum.repos.d')
    if conf.setup_iso:
        operations.put('res/local_http.repo', '/etc/yum.repos.d')
    if not exists('/var/cache/yum.tar.gz'):
        operations.put('res/yum.tar.gz', '/var/cache/')
        with cd('/var/cache'):
            run('tar vxf yum.tar.gz')
    operations.put('res/local.repo', '/etc/yum.repos.d')
