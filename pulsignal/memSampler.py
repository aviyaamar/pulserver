import psutil

from sampler import IntervalSampler


class MemoSampler(IntervalSampler):
    def __init__(self, server, interval_time):
        super().__init__(server, "virtual memory", interval_time)

    def sample(self):
        memory_storage = psutil.virtual_memory()
        memory = {"total  memory": memory_storage.total, "used memory": memory_storage.used,
                  "memory percent": memory_storage.percent, "available memory": memory_storage.available}

        return memory


