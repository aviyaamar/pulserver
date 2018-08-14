from sampler import IntervalSampler
import psutil

class DiskSampler(IntervalSampler):
    def __init__(self, server, interval_time):
        super().__init__(server, "disk", interval_time)

    # Use psutils to gather disk sample
    def sample(self):
        return {
            partition.device: self._build_partition_data(partition)
            for partition in psutil.disk_partitions()
        }

        #systems = psutil.disk_partitions()
        #for i in range(0, len(systems)):
        #    system = systems[i]
        #    usage = psutil.disk_usage(system.mountpoint)
        #    systems[i] = {"device": system.device, "total": usage.total, "used": usage.used, "percent": usage.percent}
        #return systems

    def _build_partition_data(self, partition):
        usage = psutil.disk_usage(partition.mountpoint)
        return {
            "total": usage.total,
            "used": usage.used,
            "percent": usage.percent
        }



