import psutil

from sampler import IntervalSampler


class CpuSampler(IntervalSampler):
    def __init__(self, server, interval_time):
        super().__init__(server, "cpu", interval_time)

    def sample(self):
        # Use psutils to gather cpu sample
        return dict(
            cpus={
                "cpu-{}".format(i): value
                for i, value in enumerate(psutil.cpu_percent(interval=1, percpu=True))
            }
        )
