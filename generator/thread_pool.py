# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import threading


class MyThread(threading.Thread):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.start()

    def run(self):
        while True:
            try:
                func, args, kwargs = self.queue.get(block=False)
                func(*args, **kwargs)
                self.queue.task_done()
            except Exception:
                break


class ThreadPool(object):
    def __init__(self, queue, size):
        self.pool = []
        for i in range(size):
            self.pool.append(MyThread(queue))

    def join_all(self):
        for thd in self.pool:
            if thd.isAlive() is True:
                thd.join()
