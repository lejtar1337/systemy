#!/bin/bash

# --- Funkcje sysinfo ---

sysinfo_cpu() {
    local m; m=$(grep 'model name' /proc/cpuinfo | head -n 1 | awk -F': ' '{print $2}' | sed 's/ (R)//g; s/ (TM)//g; s/ CPU @.*$//'); echo "CPU: $m"
}
sysinfo_ram() {
    local t u p; read -r _ t u _ <<< "$(free -m | grep 'Mem:')"; p=$(echo "scale=0; ($u * 100) / $t" | bc 2>/dev/null); echo "RAM: $u / $t MiB ($p% used)"
}
sysinfo_load() {
    local l; l=$(uptime | awk -F'load average: ' '{print $2}'); echo "Load: $l"
}
sysinfo_uptime() {
    local u; u=$(uptime | awk -F'up ' '{print $2}' | awk -F', ' '{print $1}' | sed 's/\([0-9]\+\) days/\1 day/; s/:/ hour, /; s/^\([0-9]\+\) / \1 hours, /; s/^\( *\)//; s/min(s)\?/ minutes/'); echo "Uptime: $u"
}
sysinfo_kernel() {
    echo "Kernel: $(uname -r)"
}
sysinfo_gpu() {
    local g; g=$(lspci -nnk | grep -i vga -A1 | grep -i 'VGA compatible controller' | head -n 1 | awk -F': ' '{print $2}' | sed 's/ \[.*//; s/Corporation//'); echo "GPU: $g"
}
sysinfo_user() {
    echo "User: $USER"
}
sysinfo_shell() {
    echo "Shell: $(basename "$SHELL")"
}
sysinfo_processes() {
    echo "Processes: $(ps -e --no-headers | wc -l)"
}
sysinfo_threads() {
    echo "Threads: $(find /proc/[0-9]*/task -maxdepth 0 2>/dev/null | wc -l)"
}
sysinfo_ip() {
    local i; i=$(ip -o -4 addr show | awk '/scope global/ {print $4}'); echo "IP: 127.0.0.1/8 ${i// / }"
}
sysinfo_dns() {
    local d; d=$(grep 'nameserver' /etc/resolv.conf | awk '{print $2}' | head -n 1); echo "DNS: ${d:-No DNS found}"
}
sysinfo_internet() {
    local s="FAIL"; timeout 1 ping -c 1 8.8.8.8 > /dev/null 2>&1 && s="OK"; echo "Internet: $s"
}

# --- Logika główna ---

declare -A F=(
    [cpu]=sysinfo_cpu [ram]=sysinfo_ram [load]=sysinfo_load [uptime]=sysinfo_uptime
    [kernel]=sysinfo_kernel [gpu]=sysinfo_gpu [user]=sysinfo_user [shell]=sysinfo_shell
    [processes]=sysinfo_processes [threads]=sysinfo_threads [ip]=sysinfo_ip [dns]=sysinfo_dns [internet]=sysinfo_internet
)
A=("cpu" "ram" "load" "uptime" "kernel" "gpu" "user" "shell" "processes" "threads" "ip" "dns" "internet")
E=0
T=()

if [[ $# -eq 0 ]]; then
    T=("${A[@]}")
else
    for a in "$@"; do
        l=$(echo "$a" | tr '[:upper:]' '[:lower:]')
        if [[ -v F[$l] ]]; then
            T+=("$l")
        else
            echo "Błąd: Nieznany argument '$a'." >&2; E=1
        fi
    done
fi

for k in "${T[@]}"; do
    "${F[$k]}"
done

exit $E