#!/usr/bin/env python3
# Cel: Wypisać USER PID COMM RSS_kB dla wszystkich procesów, korzystając z /proc.
# Jak działa: iteruje po /proc/<pid>, mapuje UID→user (pwd), COMM z /proc/<pid>/comm,
#             oraz bieżące zużycie pamięci rezydentnej czyta z /proc/<pid>/status (VmRSS: ... kB).

import os, pwd

def uid_to_name(uid):
    """Mapuje UID na nazwę użytkownika z /etc/passwd (pwd)."""
    return pwd.getpwuid(uid).pw_name  # standard POSIX do mapowania UID→nazwa [web:84][web:87]

def proc_entries():
    """Zwraca PID-y (nazwy numerycznych katalogów) z /proc."""
    for name in os.listdir("/proc"):
        if name.isdigit():
            yield name  # /proc zawiera katalogi nazwane PID-ami [web:11][web:90]

def read_uid_comm_rss_kb(pid):
    """Zwraca (uid, comm, rss_kb) dla danego PID na podstawie procfs."""
    st = os.stat(f"/proc/{pid}")          # właściciel katalogu → UID procesu [web:90][web:11]
    uid = st.st_uid
    with open(f"/proc/{pid}/comm", "r", encoding="utf-8", errors="ignore") as f:
        comm = f.readline().strip()       # krótka nazwa polecenia [web:11][web:86]
    rss_kb = 0
    # /proc/<pid>/status ma linię 'VmRSS: <liczba> kB' (resident set w kB) [web:79][web:81]
    with open(f"/proc/{pid}/status", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    rss_kb = int(parts[1])
                break
    return uid, comm, rss_kb

def main():
    """Wypisuje: USER PID COMM RSS_kB dla wszystkich dostępnych procesów."""
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