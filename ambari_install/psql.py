# -*- coding: utf-8 -*-
"""
@author: zhangwenping
Created on 2015-06-02 16:58
"""
import re

import conf
from fabric.api import run, settings, cd, sudo
from fabric import operations


db_init_templ = """sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS %(dbname)s;
DROP USER IF EXISTS %(username)s;
CREATE DATABASE %(dbname)s;
CREATE USER %(username)s WITH PASSWORD '%(password)s';
GRANT ALL PRIVILEGES ON DATABASE %(dbname)s TO %(username)s;
\c %(dbname)s
CREATE SCHEMA %(dbname)s AUTHORIZATION %(username)s;
ALTER SCHEMA %(dbname)s OWNER TO %(username)s;
ALTER ROLE %(username)s SET search_path to '%(dbname)s', 'public';
EOF
"""


def escape_sql(str_sql):
    def callback(matchobj):
        c = matchobj.group(0)
        return "'\\'" + c.strip("'") + "\\''"

    return re.sub("'.*'", callback, str_sql)


def run_sql_file(filename, dbname, dbuser, password):
    sql = 'psql -U %s -d %s -f %s' % (dbuser, dbname, filename)
    prompts = {
        'Password for user username: ': password
    }
    with settings(prompts=prompts):
        run(sql)


def run_psql(str_sql, dbuser, password, dbname=None):
    str_sql = escape_sql(str_sql)
    sql = 'psql -U %s ' % dbuser
    if dbname:
        sql += '-d %s ' % dbname

    sql += '--command "%s"' % str_sql

    prompts = {
        'Password for user username: ': password
    }
    with settings(prompts=prompts):
        run(sql)


def run_as_postgres_user(str_sql, dbname=None):
    str_sql = escape_sql(str_sql)

    if dbname:
        cmd = 'psql -d %s --command "%s"' % (dbname, str_sql)
    else:
        cmd = 'psql --command "%s"' % str_sql

    return run("su postgres -c '%s'" % cmd)


def install_postgresql_server():
    with settings(warn_only=True):
        run('yum install -y postgresql-server')
        run('yum install -y postgresql-contrib')

    prompts = {
        'Enter new superuser password: ': conf.psql_admin_password,
        'Enter it again: ': conf.psql_admin_password
    }

    with settings(sudo_user="postgres"):
        with cd('~'):
            with settings(prompts=prompts):
                sudo('initdb -D data/ -U postgres -W')

            content = "listen_addresses = '*'"
            sudo('echo "%s" >> data/postgresql.conf' % content)

    run("echo 'host\tall\t\tall\t\t0.0.0.0/0\t\ttrust' >> "
        "/var/lib/pgsql/data/pg_hba.conf")

    run('systemctl enable postgresql')
    run('systemctl restart postgresql')


def _create_postgres_db_and_user(dbname, username, password):
    params = dict(dbname=dbname, username=username, password=password)
    content = db_init_templ % params
    filename = "%s.sh" % dbname
    with open(filename, 'w') as fp:
        fp.write(content)

    operations.put(filename, '/root/')
    run('sh /root/%s' % filename)


# 创建ambari数据库，在数据库服务器执行 
def create_ambari_postgres_db():
    _create_postgres_db_and_user('ambari', conf.ambari_username, 
                                 conf.ambari_password)


# 创建hive数据库
def create_hive_postgres_db():
    _create_postgres_db_and_user('hive', conf.hive_username, 
                                 conf.hive_password)


def create_oozie_postgres_db():
    _create_postgres_db_and_user('oozie', conf.oozie_username, 
                                 conf.oozie_password)


def _drop_postgres_db_and_user(dbname, username): 
    run_as_postgres_user('drop DATABASE IF EXISTS %s;' % dbname)
    run_as_postgres_user('drop user IF EXISTS %s;' % username)


def clean_ambari_postgres_db():
    _drop_postgres_db_and_user('ambari', conf.ambari_username)


def clean_hive_postgres_db():
    _drop_postgres_db_and_user('hive', conf.hive_username)
