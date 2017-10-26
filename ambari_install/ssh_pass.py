# -*- coding: utf-8 -*-
"""
@author: zhangwenping
Created on 2017-10-05 16:58
"""

import conf
import os

from fabric.api import run, cd, settings, env
from fabric import operations


def ssh_gen_rsa_key():
    os.mkdir(env.host_string)

    run('mkdir -p /root/.ssh')
    with cd('/root/.ssh'):
        prompts = {
            'Enter file in which to save the key (/root/.ssh/id_rsa): ': '',
            'Enter passphrase (empty for no passphrase): ': '',
            'Enter same passphrase again: ': '',
            'Overwrite (y/n)? ': 'y'
        }
        with settings(prompts=prompts):
            run('ssh-keygen -t rsa')

        run('cat id_rsa.pub > authorized_keys')
        operations.get('/root/.ssh/authorized_keys', env.host_string)


def upload_authorized_keys():
    """
    1) 将合并后的authorized_keys上传到所有host的/root/.ssh/目录下
    2) 修改其访问权为600
    """
    run('mkdir -p /root/.ssh/')
    operations.put('%s/authorized_keys' % conf.ambari_server, '/root/.ssh/')
    run('chmod 600 /root/.ssh/authorized_keys')


def reconfig_sshd():
    """
    ssh在第一次访问其他host时，总是需要用户确认，下面的修改可以关闭该功能
    注意：会有一定的安全隐患。
    """
    with cd('/root/.ssh/'):
        run('echo "StrictHostKeyChecking no" > config')
        run('echo "UserKnownHostsFile /dev/null" >> config')


def ssh_no_password():
    if not os.path.exists('%s/authorized_keys' % conf.ambari_server):
        print 'Error: please run `fab ssh_gen_rsa_key` first'
        return

    upload_authorized_keys()
    reconfig_sshd()


def ssh_no_password_add_node():
    if not os.path.exists('%s/authorized_keys' % conf.ambari_server):
        print 'Error: please run `fab ssh_no_password` first'
        return

    upload_authorized_keys()
    reconfig_sshd()
