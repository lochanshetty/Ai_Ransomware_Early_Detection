from __future__ import annotations

from dataclasses import dataclass, asdict

import psutil


@dataclass
class SystemFeatures:
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_read_bytes: int = 0
    disk_write_bytes: int = 0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    process_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


def extract_system_features() -> SystemFeatures:
    """Snapshot host telemetry used as detection context."""

    vm = psutil.virtual_memory()
    disk = psutil.disk_io_counters()
    net = psutil.net_io_counters()
    return SystemFeatures(
        cpu_percent=float(psutil.cpu_percent(interval=0)),
        memory_percent=float(vm.percent),
        disk_read_bytes=int(disk.read_bytes if disk else 0),
        disk_write_bytes=int(disk.write_bytes if disk else 0),
        network_bytes_sent=int(net.bytes_sent if net else 0),
        network_bytes_recv=int(net.bytes_recv if net else 0),
        process_count=len(psutil.pids()),
    )
