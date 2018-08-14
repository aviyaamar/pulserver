import os
import json

import logging

class ServerConfiguration(object):
    def __init__(self):
        # Try to read configuration from "/etc/pulse.conf"
        if os.path.exists("/etc/pulse.conf"):
            self._path = "/etc/pulse.conf"

        else:
            self._path = "pulse.conf"

        configuration = json.loads(open(self._path, "rt").read())
        self._configuration = configuration

        logging.info("Loaded Server Configuration %s" % self._configuration)

    def set_computer_key(self, computer_key):
        self._configuration["computer_key"] = computer_key
        self._save()

    def get_computer_key(self):
        return self._configuration.get("computer_key", None)

    def get_client_key(self):
        return self._configuration["client_key"]

    def get_server_address(self):
        return self._configuration["server_address"]

    def _save(self):
        open(self._path, "wt").write(json.dumps(self._configuration))