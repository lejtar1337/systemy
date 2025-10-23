#!/usr/bin/env python3
# Cel: Wypisać USER PID COMM RSS_kB dla wszystkich procesów, korzystając z /proc.
# Jak działa: iteruje po /proc/<pid>, mapuje UID→user (pwd), COMM z /proc/<pid>/comm,
#             oraz bieżące zużycie pamięci rezydentnej czyta z /proc/<pid>/status (VmRSS: ... kB).

import os
import pwd


def uid_to_name(uid):
    """Mapuje UID na nazwę użytkownika z /etc/passwd (pwd)."""
    return pwd.getpwuid(uid).pw_name  # standard POSIX do mapowania UID→nazwa


def proc_entries():
    """Zwraca PID-y (nazwy numerycznych katalogów) z /proc."""
    for name in os.listdir("/proc"):
        if name.isdigit():
            yield name  # /proc zawiera katalogi nazwane PID-ami


def read_uid_comm_rss_kb(pid):
    """Zwraca (uid, comm, rss_kb) dla danego PID na podstawie procfs."""
    st = os.stat(f"/proc/{pid}")  # właściciel katalogu → UID procesu
    uid = st.st_uid
    with open(f"/proc/{pid}/comm", "r", encoding="utf-8", errors="ignore") as f:
        comm = f.readline().strip()  # krótka nazwa polecenia
    rss_kb = 0
    # /proc/<pid>/status ma linię 'VmRSS: <liczba> kB' (resident set w kB)
    with open(f"/proc/{pid}/status", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    rss_kb = int(parts[1])
                break
    return uid, comm, rss_kb


def print_my_memory_usage():
    """Wypisuje aktualne zużycie pamięci przez ten program."""
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                print("Moje zużycie pamięci:", line.strip())
                break


def main():
    """Wypisuje: USER PID COMM RSS_kB dla wszystkich dostępnych procesów."""
    print_my_memory_usage()
    for pid in proc_entries():
        try:
            uid, comm, rss_kb = read_uid_comm_rss_kb(pid)
            user = uid_to_name(uid)
            print(f"{user} {pid} {comm} {rss_kb}")
        except Exception:
            # Proces mógł zniknąć/brak uprawnień – pomijamy bez hałasu.
            continue


if __name__ == "__main__":
    main()
