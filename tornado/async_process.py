import subprocess

class AsyncProcess(object):
    """An non-blocking process

    Example usage:

        class MainHandler(tornado.web.RequestHandler):
            @tornado.web.asynchronous
            def get(self):
                proc = AsyncProcess()
                proc.execute('sleep 5; cat /var/run/syslog.pid',
                           self.async_callback(self.on_response))

            def on_response(self, output):
                self.write(output)
                self.finish()

    execute() can take a string command line.
    """
    def __init__(self, io_loop=None):
        self.io_loop = io_loop or ioloop.IOLoop.instance()

    def execute(self, command, callback, **kargs):
        self.pipe = subprocess.Popen(command, shell=True,
                stdout=subprocess.PIPE, **kargs).stdout
        self.callback = callback

        self.io_loop.add_handler(self.pipe.fileno(),
                self._handle_events, self.io_loop.READ)

    def _handle_events(self, fd, events):
        """Called by IOLoop when there is activity on the pipe output. """
        self.io_loop.remove_handler(fd)
        output = ''.join(self.pipe)
        self.callback(output)

if __name__ == "__main__":
    import ioloop

    def handle_output(output):
        print output
        ioloop.IOLoop.instance().stop()

    proc = AsyncProcess()
    proc.execute("sleep 5; ls -la /var/run/", handle_output)
    ioloop.IOLoop.instance().start()
