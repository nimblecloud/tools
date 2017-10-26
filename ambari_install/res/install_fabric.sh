mkdir -p /root/repo/
mv /etc/yum.repos.d /etc/yum.repos.d.bak
mkdir -p /etc/yum.repos.d

cp yum.tar.gz /var/cache/
mv /var/cache/yum /var/cache/yum.bak
cp local.repo /etc/yum.repos.d/

mv ambari-2.5.2.0-centos7.tar.gz /root/repo
mv CentOS-7-x86_64-Everything-1611.iso /root/repo

mkdir -p /root/repo/hdputils
mv HDP-2.6.2.0-centos7-rpm.tar.gz /root/repo
mv HDP-UTILS-1.1.0.21-centos7.tar.gz /root/repo/hdputils


cd /var/cache/
tar vxf yum.tar.gz

cd /root/repo
tar vxf HDP-2.6.2.0-centos7-rpm.tar.gz

cd /root/repo/hdputils
tar vxf HDP-UTILS-1.1.0.21-centos7.tar.gz

yum install -y fabric
