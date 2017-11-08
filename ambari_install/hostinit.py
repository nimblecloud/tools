# -*- coding: utf-8 -*-
"""
@author: zhangwenping
Created on 2017-10-05 16:58
"""

import conf
import utils as ut
from fabric.api import run, settings, env


def local_setup():
    run('localectl set-locale LANG=en_US.utf8')
    run('timedatectl set-timezone Asia/Shanghai')
    run("echo 'export PATH=/usr/jdk64/jdk1.8.0_112/bin/:$PATH' >> ~/.bashrc")
    run("echo 'export BROKER_HOST=%s:6667' >> ~/.bashrc" % env.host_string)
    run("echo 'export CONNECT_HOST=%s' >> ~/.bashrc" % env.host_string)


def dns_setup():
    run("sed -i '1i\\nameserver %s' /etc/resolv.conf" % conf.dns_server)


def disable_networkmanager():
    run('systemctl stop NetworkManager.service')
    run('systemctl disable NetworkManager.service')


def stop_firewalld():
    run('systemctl stop firewalld.service')
    run('systemctl disable firewalld.service')


def disable_kernel_update():
    run('echo "exclude=kernel* redhat-release*" >> /etc/yum.conf')


def disable_selinux():
    with settings(warn_only=True):
        run('setenforce 0')
        ut.set_config_value("/etc/selinux/config", "SELINUX=enforcing",
                            "SELINUX=disabled")


def set_hostname(hostname=None):
    if not hostname:
        hostname = ut.get_domain_name_by_ip(env.host_string)
    run('hostnamectl set-hostname ' + hostname)


def swap_config():
    run('sysctl -w vm.swappiness=0')
    run('echo "vm.swappiness = 0" >> /etc/sysctl.conf')


def uninstall_some_package():
    with settings(warn_only=True):
        run('yum erase -y snappy.x86_64')
