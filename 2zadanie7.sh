#!/bin/bash

# --- Funkcje menu ---

procctl_top_cpu() {
    echo "--- Top 5 Processes by CPU Usage ---"; ps aux --sort=-%cpu | head -n 6
}
procctl_top_mem() {
    echo "--- Top 5 Processes by Memory Usage ---"; ps aux --sort=-%mem | head -n 6
}
procctl_tree() {
    echo "--- Process Tree ---"; pstree -p -u
}
procctl_name_by_pid() {
    read -r -p "Enter PID: " pid
    [[ ! "$pid" =~ ^[0-9]+$ ]] && { echo "Error: PID must be a number."; return; }
    local n; n=$(ps -p "$pid" -o comm= 2>/dev/null)
    [[ -n "$n" ]] && echo "Process with PID $pid: $n" || echo "Error: Process with PID $pid not found."
}
procctl_pid_by_name() {
    read -r -p "Enter process name (or part of it): " name
    local p; p=$(pgrep -l -f "$name")
    [[ -n "$p" ]] && { echo "Processes matching '$name':"; echo "$p"; } || echo "No processes found matching '$name'."
}
procctl_kill_pid() {
    read -r -p "Enter PID to kill (SIGTERM): " pid
    [[ ! "$pid" =~ ^[0-9]+$ ]] && { echo "Error: PID must be a number."; return; }
    kill "$pid" 2>/dev/null && echo "Process with PID $pid terminated (SIGTERM)." || echo "Error: Could not kill process $pid."
}
procctl_kill_name() {
    read -r -p "Enter process name to kill (careful!): " name
    pkill -f "$name" 2>/dev/null && echo "All processes matching '$name' terminated (SIGTERM)." || echo "Error: No processes found matching '$name' or couldn't kill them."
}
procctl_show_menu() {
    echo ""; echo "Process Control:"; echo "1) List top 5 processes by CPU usage"; echo "2) List top 5 processes by memory usage"
    echo "3) Show process tree"; echo "4) Show process name by PID"; echo "5) Show process PID(s) by name"
    echo "6) Kill process by PID"; echo "7) Kill process by name"; echo "q) Exit"; echo -n "Choice: "
}

# --- Główna pętla skryptu ---

while true; do
    procctl_show_menu
    read -r c
    case "$c" in
        1) procctl_top_cpu ;; 2) procctl_top_mem ;; 3) procctl_tree ;; 4) procctl_name_by_pid ;;
        5) procctl_pid_by_name ;; 6) procctl_kill_pid ;; 7) procctl_kill_name ;;
        [Qq]) echo "Exiting Process Control. Goodbye!"; break ;;
        *) echo "Invalid choice. Please select from 1-7 or q." ;;
    esac
    echo ""; read -r -t 1 -n 1 -s -r -p "Press any key to continue..."
done
