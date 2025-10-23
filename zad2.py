#!/usr/bin/env python3
import argparse
import time
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Co sekundę dopisuje do pliku nową linię z jej numerem, licząc od zera."
    )
    parser.add_argument("plik", help="Ścieżka do pliku wyjściowego (zostanie utworzony od nowa).")
    args = parser.parse_args()

    # 'w' tworzy/zeruje plik
    with open(args.plik, "w", encoding="utf-8") as f:
        i = 0
        try:
            while True:
                f.write(f"{i}\n")
                f.flush()          # upewnij się, że treść trafia na dysk na bieżąco
                i += 1
                time.sleep(1)
        except KeyboardInterrupt:
            # zakończenie po Ctrl+C
            pass

if __name__ == "__main__":
    main()
