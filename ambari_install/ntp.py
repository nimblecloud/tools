# -*- coding: utf-8 -*-
"""
@author: zhangwenping
Created on 2017-10-05 16:58
"""

from fabric.api import run, settings, env

import utils
import conf


def _install_ntp_service():
    with settings(warn_only=True):
        run("yum install -y ntp ntpdate")

    run("systemctl start ntpd.service")
    run("systemctl enable ntpd.service")


def _restart_ntp_service():
    run('systemctl restart ntpd.service')


def install_ntp_server():
    _install_ntp_service()
    restrict = 'restrict %s mask %s nomodify notrap' % (conf.subnet,
                                                        conf.netmask)
    utils.insert_after('/etc/ntp.conf', 
                       '# Hosts on local network are less restricted.',
                       restrict)
    _restart_ntp_service()


def install_ntp_client():
    if env.host_string == conf.ntp_server:
        return
    _install_ntp_service()
    run('timedatectl set-ntp yes')

    search = '# Please consider joining the pool (http:\/\/www.pool.ntp.org\/join.html).'

    value = 'server %s prefer' % conf.ntp_domain_name
    utils.insert_after('/etc/ntp.conf', search, value)

    _restart_ntp_service()

    ntp_dname = 'ntp.'+conf.domain_name

    retry = 3
    while retry:
        with settings(warn_only=True):
            out = run('ntpdate -u ' + ntp_dname)
            if out.failed:
                print out
                print 'retry: ', retry
                retry -= 1
            else:
                break
