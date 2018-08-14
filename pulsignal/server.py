import logging
import os
import platform

from command import Commander
from communication import Communicator
from logsampler import LogSampler
from cpuSampler import CpuSampler
from diskSampler import DiskSampler
from connectionsampler import ConnectionSampler
from memSampler import MemoSampler
from sampler import IntervalSampler

class Server(object):
    def __init__(self, configuration):
        self._configuration = configuration
        self._communicator = Communicator(self, configuration.get_client_key(), configuration.get_computer_key())
        self._commander = Commander(self)

        self._samplers = [
            CpuSampler(self, 5),#60 * 10),
            DiskSampler(self, 5),#60 * 10)
            ConnectionSampler(self, 60),
            MemoSampler(self, 5),
            LogSampler(self, "/var/log/auth.log"),
            LogSampler(self, "/var/log/syslog")
        ]

    def run(self):
        logging.info("Server Initializing")
       # Run all components
        self._communicator.run()
        self._commander.run()
        for sampler in self._samplers:
            sampler.run()

        # When starting, send the current os version
        operating = " ".join(platform.linux_distribution())

        for line in operating.splitlines():
            tokens = line.split(" ", 1)



        self._communicator.send_statistics("system", dict(
            os=tokens[0],
            name=os.uname()[1],
            version=tokens[1],
            cpu=next(row.split("\t:", 1) for row in open("/proc/cpuinfo", "rt").readlines() if row.startswith("model name"))[1].strip()
        ))

        # Wait for components to finish
        self._communicator.wait()

    @property
    def communicator(self):
        return self._communicator

    @property
    def configuration(self):
        return self._configuration


