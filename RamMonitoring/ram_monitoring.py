import os

import psutil as psutil
import sys


def ram_monitoring(get_response):
    def middleware(request):
        request._mem = psutil.Process(os.getpid()).memory_info()

        response = get_response(request)

        mem = psutil.Process(os.getpid()).memory_info()
        diff = mem.rss - request._mem.rss
        print '[PYTHON-DAJGO] MEMORY USAGE %r' % ((diff, request.path),)

        return response

    return middleware
