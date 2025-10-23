import time
import sys

def main():
    if len(sys.argv) != 2:
        print("python3 zad2.py [plik w którym będzie jechało (jazda z ...)]")
        sys.exit(1)

    plik = sys.argv[1]


    with open(plik, "w", encoding="utf-8") as f:
        i = 0
        try:
            while True:
                f.write(f"{i}\n")
                f.flush()
                i += 1
                time.sleep(1)
        except KeyboardInterrupt:
            # zakończenie po Ctrl+C
            pass

if __name__ == "__main__":
    main()