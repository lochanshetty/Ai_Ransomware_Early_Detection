from __future__ import annotations

import os
import sys
from dataclasses import dataclass, asdict

import psutil


@dataclass
class ProcessFeatures:
    pid: int = 0
    process_name: str = "unknown"
    executable_path: str = ""
    username: str = ""
    parent_pid: int = 0
    parent_name: str = ""
    cmdline: str = ""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    num_threads: int = 0
    create_time: float = 0.0
    process_reputation: float = 0.5

    def to_dict(self) -> dict:
        return asdict(self)


def _reputation_for_process(name: str, exe: str) -> float:
    """Heuristic reputation: trusted system paths score higher."""

    lowered_exe = exe.lower()
    trusted = (
        sys.executable.lower(),
        os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "system32").lower(),
        "/usr/bin",
        "/bin",
        "/sbin",
    )
    if any(lowered_exe.startswith(prefix) for prefix in trusted if prefix):
        return 0.85
    suspicious_names = {"powershell", "cmd", "wscript", "cscript", "python", "bash", "sh"}
    if name.lower().split(".")[0] in suspicious_names:
        return 0.35
    return 0.5


def extract_process_features(pid: int | None = None) -> ProcessFeatures:
    """Extract live process metadata via psutil."""

    target_pid = pid or os.getpid()
    try:
        proc = psutil.Process(target_pid)
        with proc.oneshot():
            name = proc.name()
            exe = proc.exe() if proc.exe() else ""
            username = proc.username() if hasattr(proc, "username") else ""
            parent = proc.parent()
            parent_pid = parent.pid if parent else 0
            parent_name = parent.name() if parent else ""
            cmdline = " ".join(proc.cmdline()[:20])
            cpu = proc.cpu_percent(interval=0.0)
            mem = proc.memory_percent()
            threads = proc.num_threads()
            created = proc.create_time()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return ProcessFeatures(pid=target_pid)

    return ProcessFeatures(
        pid=target_pid,
        process_name=name,
        executable_path=exe,
        username=username,
        parent_pid=parent_pid,
        parent_name=parent_name,
        cmdline=cmdline,
        cpu_percent=float(cpu),
        memory_percent=float(mem),
        num_threads=int(threads),
        create_time=float(created),
        process_reputation=_reputation_for_process(name, exe),
    )


def find_processes_touching_path(path: str, max_processes: int = 30) -> list[ProcessFeatures]:
    """
    Best-effort: return processes with open handles to path (platform-dependent).
    Falls back to current process if enumeration fails or exceeds limit.
    """

    if os.name == "nt":
        return [extract_process_features()]

    candidates: list[ProcessFeatures] = []
    normalized = os.path.normcase(os.path.abspath(path))
    checked = 0
    for proc in psutil.process_iter(["pid", "name"]):
        if checked >= max_processes:
            break
        checked += 1
        try:
            for handle in proc.open_files():
                if os.path.normcase(handle.path) == normalized:
                    candidates.append(extract_process_features(proc.pid))
                    return candidates
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    if not candidates:
        candidates.append(extract_process_features())
    return candidates
