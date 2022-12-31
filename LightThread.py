import threading

class LightThread(threading.Thread):
    def __init__(self, name=None, *args, **kwargs):
        super(LightThread,self).__init__(*args, **kwargs)
        self.name = name
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

    def stop(self): 
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def pause(self):
        self._pause_event.set()

    def resume(self):
        self._pause_event.clear()

    def paused(self):
        return self._pause_event.is_set()