# -*- coding: utf-8 -*-
"""
@author: zhangwenping
Created on 2017-10-05 16:58
"""
from fabric.api import run, settings
from fabric import operations
import conf

SUBNET = ''  # 192.168.1.0
NETMASK = ''  # 255.255.255.0
START_IP = ''  # 192.168.1.201
END_IP = ''  # 192.168.1.220


TFTP_TEMP = """service tftp
{
        socket_type             = dgram
        protocol                = udp
        wait                    = yes
        user                    = root
        server                  = /usr/sbin/in.tftpd
        server_args             = -s /tftpboot
        disable                 = no
        per_source              = 11
        cps                     = 100 2
        flags                   = IPv4
}
"""

DHCP_TEMP = """
allow booting;
allow bootp;
log-facility local4;

subnet %(subnet)s netmask %(netmask)s {
    range %(startip)s %(endip)s;
    filename "pxelinux.0";
    default-lease-time 86400;
    max-lease-time 172800;
}
"""

DEFAULT_TEMP = """default vesamenu.c32
timeout 600

display boot.msg

# Clear the screen when exiting the menu, instead of leaving the menu displayed.
# For vesamenu, this means the graphical background is still displayed without
# the menu itself for as long as the screen remains in graphics mode.
menu clear
menu background splash.png
menu title CentOS Linux 7
menu vshift 8
menu rows 18
menu margin 8
#menu hidden
menu helpmsgrow 15
menu tabmsgrow 13

# Border Area
menu color border * #00000000 #00000000 none

# Selected item
menu color sel 0 #ffffffff #00000000 none

# Title bar
menu color title 0 #ff7ba3d0 #00000000 none

# Press [Tab] message
menu color tabmsg 0 #ff3a6496 #00000000 none

# Unselected menu item
menu color unsel 0 #84b8ffff #00000000 none

# Selected hotkey
menu color hotsel 0 #84b8ffff #00000000 none

# Unselected hotkey
menu color hotkey 0 #ffffffff #00000000 none

# Help text
menu color help 0 #ffffffff #00000000 none

# A scrollbar of some type? Not sure.
menu color scrollbar 0 #ffffffff #ff355594 none

# Timeout msg
menu color timeout 0 #ffffffff #00000000 none
menu color timeout_msg 0 #ffffffff #00000000 none

# Command prompt text
menu color cmdmark 0 #84b8ffff #00000000 none
menu color cmdline 0 #ffffffff #00000000 none

# Do not display the actual menu unless the user presses a key. All that is displayed is a timeout message.

menu tabmsg Press Tab for full configuration options on menu items.

menu separator # insert an empty line
menu separator # insert an empty line

label linux
  menu label ^Install CentOS Linux 7
  kernel vmlinuz
  append initrd=initrd.img method=http://%(repo_server)s/iso devfs=nomount
"""


def setup_pxe():
    if '' in (SUBNET, NETMASK, START_IP, END_IP):
        print('Please setup SUBNET, NETMASK, START_IP, END_IP first')
        return

    with settings(warn_only=True):
        run('yum install -y tftp-server syslinux dhcp')

    run('mkdir -p /tftpboot')

    with open('tftp', 'w') as fp:
        fp.write(TFTP_TEMP)

    operations.put('tftp', '/etc/xinetd.d/tftp')
    run('service xinetd restart')

    run('cp /usr/share/syslinux/pxelinux.0 /tftpboot/')

    with open('dhcpd.conf', 'w') as fp:
        params = dict(subnet=SUBNET, netmask=NETMASK,
                      startip=START_IP, endip=END_IP)
        content = DHCP_TEMP % params
        fp.write(content)

    operations.put('dhcpd.conf', '/etc/dhcp/')
    run('service dhcpd restart')

    # 复制文件到/tftpboot
    run('cp /root/repo/iso/images/pxeboot/vmlinuz /tftpboot/')
    run('cp /root/repo/iso/images/pxeboot/initrd.img /tftpboot/')
    run('mkdir -p /tftpboot/pxelinux.cfg')
    with open('default', 'w') as fp:
        content = DEFAULT_TEMP % {'repo_server': conf.repo_server}
        fp.write(content)

    operations.put('default', '/tftpboot/pxelinux.cfg/default')
    run('cp /root/repo/iso/isolinux/{vesamenu.c32,boot.msg,splash.png} '
        '/tftpboot/')
