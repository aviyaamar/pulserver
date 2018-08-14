import subprocess

class FileTail(object):
    def __init__(self, file_path, callback):
        self._file_path = file_path
        self._callback = callback

    def tail(self):

        # DO NOT COMMIT
        f = subprocess.Popen(['tail', '-F', self._file_path], stdout=subprocess.PIPE, stderr=None)

        while True:
            line = f.stdout.readline()
            if not line:
                break
            self._callback(line)
