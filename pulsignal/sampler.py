import time
import threading

class Sampler(object):
    def __init__(self, server, sampler_type):
        self._server = server
        self._sampler_type = sampler_type
        self._thread = threading.Thread(target=self.threaded_worker)

    def run(self):
        # Create a thread for sampler
        self._thread.start()

    def send_statistics(self, data):
        if data:
            self._server.communicator.send_statistics(self._sampler_type, data)

    def threaded_worker(self):
        raise NotImplementedError()

    def _run_in_thread(self):
        while True:
            # Sleep for an interval
            time.sleep(self._interval_in_seconds)

            # Run the sample
            data = self.sample()

            # Send the data
            if data:
                self._server.communicator.send_statistics(
                    self._sampler_type,
                    data
                )


class IntervalSampler(Sampler):
    def __init__(self, server, sampler_type, interval_in_seconds):
        super().__init__(server, sampler_type)
        self._interval_in_seconds = interval_in_seconds

    def sample(self):
        raise NotImplementedError()

    def threaded_worker(self):
        while True:
            # Sleep for an interval
            time.sleep(self._interval_in_seconds)

            # Run the sample
            data = self.sample()

            # Send the data
            self.send_statistics(data)
