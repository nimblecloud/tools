# -*- coding: utf-8 -*-
"""
Copyright (c) 2017, NimbleX .,Ltd.

@author: zhangwenping
Created on 2017-10-25 14:10
"""
import csv
import time
import random
import sys


GWW = 'GW'  # 高位预警
DWW = 'DW'  # 低位预警
FLW = 'FW'  # 第一级报警
SLW = 'SW'  # 第二级报警


def _get_datetime_generator(start, end):
    """
    随机生成一个时间，start和end之间。输入时间格式：2017-08-10
    """
    start = time.mktime(time.strptime(start, '%Y-%m-%d'))
    end = time.mktime(time.strptime(end, '%Y-%m-%d'))

    def generator():
        t = random.randint(start, end)
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))

    return generator


def _get_serial_number_generator(prefix, start, end):
    if len(prefix) >= 10:
        prefix = prefix[:10]
    else:
        prefix = prefix + "X" * (10 - len(prefix))

    def generator():
        sn = random.randint(start, end)
        return '%s%040X' % (prefix, sn)

    return generator


def YW_warnning_generator():
    """
    液位报警数据生成器
    """

    high = random.randint(80, 100)
    low = random.randint(1, 20)
    v = random.choice((high, low))

    info = GWW if v >= 80 else DWW
    return info, v


def WD_warnning_generator():
    """
    温度报警数据生成器
    """
    value = random.randint(50, 80)
    info = SLW if value >= 65 else FLW
    return info, value


def YL_warnning_generator():
    """
    压力报警数据生成器
    """
    value = random.randint(150, 200)

    info = SLW if value >= 175 else FLW
    return info, value


def LL_warnning_generator():
    """
    流量报警数据生成器
    """
    value = random.randint(300, 400)

    info = SLW if value >= 350 else FLW
    direct = random.choice((1, 2))
    return info, value, direct


# 储蓄编码
CX_number_generator = _get_serial_number_generator("CXSN", 1, 1000)

# 液位传感器位号
YW_number_generator = _get_serial_number_generator("YWSN", 1, 1000)

# 温度传感器位号
WD_number_generator = _get_serial_number_generator("WDSN", 1, 1000)

# 压力传感器位号
YL_number_generator = _get_serial_number_generator("YLSN", 1, 1000)

# 流量传感器位号
LL_number_generator = _get_serial_number_generator("LLSN", 1, 1000)

# 时间生成器
time_generator = _get_datetime_generator('2017-07-01', '2017-09-30')


def write_head(csvfile, writer):
    # 写utf-8格式头
    csvfile.write('\xEF\xBB\xBF')
    writer.writerow(
        ['储蓄编码',
         '液位传感器号', '报警类型', '液位数据', '报警时间',
         '温度传感器号', '报警类型', '温度数据', '报警时间',
         '压力传感器号', '报警类型', '压力数据', '报警时间',
         '流量传感器号', '报警类型', '流量数据', '流量方向', '报警时间'])


def gen_test_data(n=10000):
    with open('test_data.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        # write_head(csvfile, writer)

        for x in xrange(1, n + 1):
            # 储蓄编码
            cxsn = CX_number_generator()

            # 液位报警数据：液位传感器SN，报警类型，液位数据，报警时间
            ywsn = YW_number_generator()
            yw_type, yw_value = YW_warnning_generator()
            yw_time = time_generator()

            # 温度报警数据：温度传感器SN，温度报警类型，温度数据，报警时间
            wdsn = WD_number_generator()
            wd_type, wd_value = WD_warnning_generator()
            wd_time = time_generator()

            # 压力报警数据：压力传感器SN，压力报警类型，压力数据，报警时间
            ylsn = YL_number_generator()
            yl_type, yl_value = YL_warnning_generator()
            yl_time = time_generator()

            # 流量报警数据：流量传感器SN，报警类型，数据，流量方向，报警时间
            llsn = LL_number_generator()
            ll_type, ll_value, ll_direct = LL_warnning_generator()
            ll_time = time_generator()

            writer.writerow([cxsn,
                             ywsn, yw_type, yw_value, yw_time,
                             wdsn, wd_type, wd_value, wd_time,
                             ylsn, yl_type, yl_value, yl_time,
                             llsn, ll_type, ll_value, ll_direct, ll_time])


def main():
    n = 10000
    if len(sys.argv) == 2:
        n = int(sys.argv[1])

    gen_test_data(n)


if __name__ == '__main__':
    main()
