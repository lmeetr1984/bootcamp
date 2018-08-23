# coding=utf8
from django.http import HttpResponseBadRequest

"""
修饰函数， 判断一下一个请求是不是ajax请求

"""

def ajax_required(f):
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()

        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap
