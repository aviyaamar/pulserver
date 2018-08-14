import logging
import threading
import queue
import time
import datetime
import requests


"""
Coordinated all communication with the server

"""
class Communicator(object):
    def __init__(self, server, client_key, computer_key):
        self._server = server
        self._thread = threading.Thread(target=self.connect)
        self.pending = queue.Queue()
        self.client_name = client_key
        self.computer_id = computer_key

    def run(self):
        # Handles running in a thread
        self._thread.start()

    def wait(self):
        self._thread.join()

    def send_statistics(self, statistics_type, statistics_data):
        self.pending.put(dict(
            type="statistics",
            data=dict(
                statistics_type=statistics_type,
                statistics_data=statistics_data,
                create_time=int(datetime.datetime.utcnow().timestamp())
            )
        ))

    def send_command_results(self, command_id, results):
        self.pending.put(dict(
            type="command_results",
            data=dict(
                command_id=command_id,
                results=results
            )
        ))

    def query_commands(self):
        result = requests.get("http://" + self._server.configuration.get_server_address() + "/api/query_commands/" + self.client_name + "/" + self.computer_id)
        return result.json()

    def connect(self):
        while True:
            if not self._send_best_effort(self.pending.get()):
                print("Sending of specific packet failed, skipping.")

    def _send_best_effort(self, packet):
        sleep_penalty = 7
        fail_count = 1

        while fail_count <= 10:
            try:
                requests.post("http://" + self._server.configuration.get_server_address() + "/api/" + packet['type'] + "/" + self.client_name + "/" + self.computer_id, json=packet['data'])
            except Exception as e:
                logging.error("Failed to connect, wait 1 minute and try again %s", e)
                time.sleep(sleep_penalty)
                sleep_penalty *= 2
                fail_count += 1

                # Continue to retry the send
                continue

            # Send was successfull, break send loop
            return True

        # We exceeded the fail count
        return False







#    def _pull_from_server(self):
#        """
#        This function runs every 10 minutes
#        """
#         Connect to the server and push information
#        pass

