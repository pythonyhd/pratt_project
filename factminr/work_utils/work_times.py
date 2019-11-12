# -*- coding: utf-8 -*-
# @Time    : 2019/11/12 15:56
# @Author  : Yasaka.Yu
# @File    : work_times.py
import time


def statistic_time(function):
    def wrapper(*args,**kwargs):
        print('[Function: {name} start...]'.format(name=function.__name__))
        start_time = time.time()  # 开始时间
        result = function(*args, **kwargs)
        end_time = time.time()
        print('[Function: {name} finished, spent time: {time:.2f}s]'.format(name=function.__name__,time=end_time - start_time))
        return result
    return wrapper