import math

class BuddyAllocator:
    def __init__(self, total_size, limit):
        self.total_size = total_size
        self.limit = limit
        # Minimalny rozmiar bloku wyliczony z limitu podziałów
        self.min_block_size = total_size // (2 ** limit)
        
        # Mapa wolnych bloków: {rozmiar: [lista_adresów]}
        self.free_blocks = {self.total_size: [0]}
        # Pomocnicze rozmiary pośrednie w mapie
        current_s = self.total_size // 2
        while current_s >= self.min_block_size:
            self.free_blocks[current_s] = []
            current_s //= 2
            
        # Zbiór zajętych bloków dla walidacji (adres -> rozmiar)
        self.allocated_blocks = {}

    def _get_target_block_size(self, size):
        if size <= self.min_block_size:
            return self.min_block_size
        # Obliczanie 2^ceil(log2(size))
        return 2 ** math.ceil(math.log2(size))

    def alloc(self, size):
        target_size = self._get_target_block_size(size)
        
        if target_size > self.total_size:
            print(f"Błąd: Rozmiar {target_size} przekracza całkowitą pamięć.")
            return None

        # Szukaj dostępnego bloku, zaczynając od target_size w górę
        current_size = target_size
        while current_size <= self.total_size and not self.free_blocks[current_size]:
            current_size *= 2

        if current_size > self.total_size:
            print(f"Błąd: Brak dostępnej pamięci dla rozmiaru {target_size}.")
            return None

        # Pobierz adres znalezionego (większego lub równego) bloku
        address = self.free_blocks[current_size].pop(0)

        # Rekurencyjny podział bloku, jeśli jest za duży
        while current_size > target_size:
            current_size //= 2
            buddy_address = address + current_size
            # Dodaj drugą połowę (buddy) do listy wolnych bloków
            self.free_blocks[current_size].append(buddy_address)
            # Pierwsza połowa 'address' zostaje do dalszego podziału lub alokacji

        self.allocated_blocks[address] = target_size
        return (address, target_size)

    def free(self, address, size):
        # Walidacja: czy taki blok został rzeczywiście zaalokowany
        if address not in self.allocated_blocks or self.allocated_blocks[address] != size:
            print(f"Błąd: Niepoprawny adres {address} lub rozmiar {size} (Double free lub invalid address).")
            return

        # Usuń z rejestru zajętych
        del self.allocated_blocks[address]
        
        current_size = size
        current_address = address

        # Rekurencyjne łączenie "kumpli" (buddies)
        while current_size < self.total_size:
            buddy_address = current_address ^ current_size
            
            # Sprawdź, czy kumpel jest wolny (znajduje się na liście wolnych o tym samym rozmiarze)
            if buddy_address in self.free_blocks[current_size]:
                # Usuń kumpla z listy wolnych
                self.free_blocks[current_size].remove(buddy_address)
                # Nowy adres bloku po złączeniu to mniejszy z adresów
                current_address = min(current_address, buddy_address)
                current_size *= 2
            else:
                # Kumpel jest zajęty, nie można łączyć dalej
                break
        
        # Dodaj (ewentualnie scalony) blok do listy wolnych
        self.free_blocks[current_size].append(current_address)
        print(f"Zwolniono: adres {address}, rozmiar {size}. Scalono do rozmiaru {current_size}.")

    def status(self):
        print("\n--- Stan Alokatora ---")
        print(f"Wolne bloki: {self.free_blocks}")
        print(f"Zajęte bloki: {self.allocated_blocks}")
        print("----------------------\n")

# --- Przykład użycia ---
allocator = BuddyAllocator(2048, 6)

# Alokacja 1
res1 = allocator.alloc(200) # Oczekiwanie: 256
print(f"Alokacja 1: {res1}")

# Alokacja 2
res2 = allocator.alloc(100) # Oczekiwanie: 128
print(f"Alokacja 2: {res2}")

allocator.status()

# Zwolnienie
if res1:
    allocator.free(res1[0], res1[1])

allocator.status()