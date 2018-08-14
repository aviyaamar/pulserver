import socket

from sampler import IntervalSampler


class ConnectionSampler(IntervalSampler):
    def __init__(self, server, interval_time):
        super().__init__(server, "connection", interval_time)

    def internet(self):
        host = "8.8.8.8"
        port = 53
        timeout = 3
        """
     ...   Host: 8.8.8.8 (google-public-dns-a.google.com)
     ...   OpenPort: 53/tecp
     ...   Service: domain (DNS/TCP)
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except Exception as ex:
            print("something went wrong", ex)
            return False

    def sample(self):
        return self.internet()


