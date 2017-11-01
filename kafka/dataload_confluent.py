# -*- coding: utf-8 -*-
"""
Copyright (c) 2017, NimbleX .,Ltd.

@author: zhangwenping
Created on 2017-10-31 18:36
"""
import sys
import csv

from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

schema_registry_url = 'http://192.168.10.60:8081'


def load(datafile, schema, server, topic):
    value_schema = avro.load(schema)
    # key_schema = avro.load('KeySchema.avsc')

    avroProducer = AvroProducer({
        'bootstrap.servers': server,
        'schema.registry.url': schema_registry_url},
        default_value_schema=value_schema)

    with open(datafile, 'rb') as csvfile:
        header = csvfile.readline()
        if not header.startswith('\xEF\xBB\xBF'):
            print 'have no header'
            csvfile.seek(0)

        spamreader = csv.reader(csvfile)
        for row in spamreader:

            data = {
                'STSN': row[0],
                'YWSN': row[1],
                'YWWT': row[2],
                'YWVALUE': int(row[3]),
                'YWTIME': row[4],

                'WDSN': row[5],
                'WDWT': row[6],
                'WDVALUE': int(row[7]),
                'WDTIME': row[8],

                'YLSN': row[9],
                'YLWT': row[10],
                'YLVALUE': int(row[11]),
                'YLTIME': row[12],

                'LLSN': row[13],
                'LLWT': row[14],
                'LLVALUE': int(row[15]),
                'LLDIRECT': int(row[16]),
                'LLTIME': row[17]
            }

            avroProducer.produce(topic=topic, value=data)

        avroProducer.flush()


def main():
    datafile = ''
    topic = ''
    server = 'localhost:1234'
    schema = ''

    if len(sys.argv) == 1:
        print("Usage: \n")
        print("python dataload.py datafile schema [server_address, topic]")
        print("e.g. python dataload_avro.py test_data.csv "
              "schema.avsc localhost:1234 test_topic")
        return

    if len(sys.argv) > 1:
        datafile = sys.argv[1]

    if len(sys.argv) > 2:
        schema = sys.argv[2]

    if len(sys.argv) > 3:
        server = sys.argv[3]

    if len(sys.argv) > 4:
        topic = sys.argv[4]

    load(datafile, schema, server, topic)


if __name__ == '__main__':
    main()
