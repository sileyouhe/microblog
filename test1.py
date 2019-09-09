import time, functools

# 这是装饰器
def metric(fn):
    def wrapper(*args,**kwargs):
        start = time.time()
        res = fn(*args, **kwargs)
        end = time.time()
        print('%s executed in %s ms' % (fn.__name__, end-start))
        return res
    return wrapper

# 本来这个函数只有sleep功能，现在给他加上一个装饰器计算他运行的时间
@metric
def m_func():
    time.sleep(1)
    print('this is main function')
    return

# 测试
@metric
def fast(x, y):
    time.sleep(0.0012)
    return x + y


@metric
def slow(x, y, z):
    time.sleep(0.1234)
    return x * y * z

if __name__ == '__main__':
    f = fast(11, 22)
    s = slow(11, 22, 33)
    if f != 33:
        print('测试失败!')
    elif s != 7986:
        print('测试失败!')


