import base64

from sampler import Sampler
from tail import FileTail
class LogSampler(Sampler):

    def __init__(self, server, file_path):
        super().__init__(server, "log")
        self._file_path = file_path
        self._lines = []

    def threaded_worker(self):
        file0 = FileTail(self._file_path, self._new_line)
        file0.tail()

    def _new_line(self, line):
        # Received new line.
        # Send statistics once every 100 rows
        self._lines.append(line.decode("utf-8"))
        if len(self._lines) >= 10:
            self.send_statistics(dict(file_path=self._file_path, lines=self._lines))
            self._lines = []

