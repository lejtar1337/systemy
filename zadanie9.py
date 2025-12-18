import csv
import sys
from collections import deque

class Process:
    def __init__(self, name, length, start):
        self.name = name
        self.remaining_time = int(length)
        self.start_time = int(start)
        self.initial_length = int(length)

    def __repr__(self):
        return f"{self.name}(len={self.initial_length}, start={self.start_time})"

class RoundRobinScheduler:
    def __init__(self, processes, quantum):
        # Kolejka procesów, które jeszcze nie pojawiły się w systemie
        self.waiting_queue = deque(processes)
        # Kolejka procesów gotowych do wykonania
        self.ready_queue = deque()
        self.quantum = quantum
        self.current_time = 0

    def run(self):
        while self.waiting_queue or self.ready_queue:
            # 1. Sprawdź, czy nadeszły nowe procesy
            new_arrivals = False
            while self.waiting_queue and self.waiting_queue[0].start_time <= self.current_time:
                proc = self.waiting_queue.popleft()
                self.ready_queue.append(proc)
                print(f"T={self.current_time}: New process {proc.name} is waiting for execution (length={proc.remaining_time})")
                new_arrivals = True

            # 2. Jeśli nic nie ma w ready_queue, inkrementuj czas i pomiń krok
            if not self.ready_queue:
                if not new_arrivals and self.waiting_queue:
                    print(f"T={self.current_time}: No processes currently available")
                self.current_time += 1
                continue

            # 3. Pobierz proces z początku kolejki ready
            current_process = self.ready_queue.popleft()
            
            # Oblicz czas pracy (kwant lub tyle, ile zostało procesowi)
            run_time = min(self.quantum, current_process.remaining_time)
            
            print(f"T={self.current_time}: {current_process.name} will be running for {run_time} time units. Time left: {current_process.remaining_time - run_time}")
            
            # Wykonaj proces (inkrementacja czasu symulacji)
            for _ in range(run_time):
                self.current_time += 1
                # Sprawdzanie nowych procesów w trakcie trwania kwantu
                while self.waiting_queue and self.waiting_queue[0].start_time == self.current_time:
                    proc = self.waiting_queue.popleft()
                    self.ready_queue.append(proc)
                    print(f"T={self.current_time}: New process {proc.name} is waiting for execution (length={proc.remaining_time})")

            current_process.remaining_time -= run_time

            # 4. Obsługa zakończenia lub wywłaszczenia
            if current_process.remaining_time > 0:
                self.ready_queue.append(current_process)
            else:
                print(f"T={self.current_time}: Process {current_process.name} has been finished")

        print(f"T={self.current_time}: No more processes in queues")

def main():
    if len(sys.argv) < 3:
        print("Użycie: python rr.py <plik.csv> <kwant_czasu>")
        return

    file_path = sys.argv[1]
    quantum = int(sys.argv[2])
    processes = []

    try:
        with open(file_path, mode='r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    processes.append(Process(row[0], row[1], row[2]))
    except FileNotFoundError:
        print("Błąd: Nie znaleziono pliku CSV.")
        return

    scheduler = RoundRobinScheduler(processes, quantum)
    scheduler.run()

if __name__ == "__main__":
    main()