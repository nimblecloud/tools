# -*- coding: utf-8 -*-
"""
Copyright (c) 2017, NimbleX .,Ltd.

@author: zhangwenping
Created on 2017-10-25 17:04
"""
import sys
import io
import avro.schema
import avro.io
import csv

from kafka import KafkaProducer


localserver = 'localhost:1234'

schema_file = "schema.avsc"

# Kafka topic
default_topic = "test_topic"


def load(datafile, schema_file, server, topic):
    def serializer(value):
        writer = avro.io.DatumWriter(schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write(value, encoder)
        raw_bytes = bytes_writer.getvalue()

        return raw_bytes

    producer = KafkaProducer(bootstrap_servers=server,
                             value_serializer=serializer)
    schema = avro.schema.parse(open(schema_file).read())

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

            producer.send(topic, data)

        producer.flush()


def main():
    datafile = ''
    schema = schema_file
    topic = default_topic
    server = 'localhost:1234'

    if len(sys.argv) == 1:
        print("Usage: \n")
        print("python dataload.py datafile schema [server_address, topic]")
        print("e.g. python dataload_avro.py test_data.csv "
              "schema.avsc localhost:1234 test_topic")
        return

    if len(sys.argv) > 1:
        datafile = sys.argv[1]

    if len(sys.argv) > 1:
        schema = sys.argv[2]

    if len(sys.argv) > 2:
        server = sys.argv[3]

    if len(sys.argv) > 3:
        topic = sys.argv[4]

    load(datafile, schema, server, topic)


if __name__ == '__main__':
    main()
