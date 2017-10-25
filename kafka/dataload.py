# -*- coding: utf-8 -*-
"""
Copyright (c) 2017, NimbleX .,Ltd.

@author: zhangwenping
Created on 2017-10-25 16:00
"""
import sys
from kafka import KafkaProducer

default_topic = 'test_topic'


def load(server, topic, datafile):
    producer = KafkaProducer(bootstrap_servers=server,
                             value_serializer=str.encode)

    with open(datafile, 'rb') as csvfile:
        header = csvfile.readline()
        if not header.startswith('\xEF\xBB\xBF'):
            print 'have no header'
            csvfile.seek(0)

        for line in csvfile:
            producer.send(topic, line)

        producer.flush()


def main():
    datafile = ''
    topic = default_topic
    server = 'localhost:1234'

    if len(sys.argv) == 1:
        print "Usage: \n"
        print "python dataload.py datafile [server_address, topic]"
        print "e.g. python dataload.py test_data.csv localhost:1234 test_topic"
        return

    if len(sys.argv) > 1:
        datafile = sys.argv[1]

    if len(sys.argv) > 2:
        server = sys.argv[2]

    if len(sys.argv) > 3:
        topic = sys.argv[3]

    load(server, topic, datafile)


if __name__ == '__main__':
    main()
