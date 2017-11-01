# -*- coding: utf-8 -*-
"""
Copyright (c) 2017, NimbleX .,Ltd.

@author: zhangwenping
Created on 2017-10-25 16:00
"""
import sys
from kafka import KafkaConsumer


def read(server, topic, groupid):
    consumer = KafkaConsumer(topic,
                             bootstrap_servers=server,
                             group_id=groupid)
    for msg in consumer:
        print msg


def main():
    topic = ''
    server = ''

    if len(sys.argv) == 1:
        print "Usage: \n"
        print "python dataload.py server_address, topic, groupid"
        print "e.g. python dataload.py test_data.csv localhost:1234 test_topic"
        return

    if len(sys.argv) > 1:
        server = sys.argv[1]

    if len(sys.argv) > 2:
        topic = sys.argv[2]

    if len(sys.argv) > 3:
        groupid = sys.argv[3]

    read(server, topic, groupid)


if __name__ == '__main__':
    main()
