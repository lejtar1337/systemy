/**
 * Kompilacja: g++ -o solution main.cpp -pthread -O3
 * Użycie: ./solution <plik.txt> [ilość_procesów]
 */

#include <iostream>
#include <vector>
#include <thread>
#include <cmath>
#include <cstring>
#include <cctype>

// Biblioteki systemowe (POSIX)
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <unistd.h>
#include <pthread.h>

// Struktura przechowywana w pamięci współdzielonej
struct SharedData {
    pthread_mutex_t mutex;
    unsigned int letter_counts[26]; // A-Z (indeksy 0-25)
    double sqrt_sum;
};

// Funkcja pomocnicza do obsługi błędów
void handleError(const char* msg) {
    perror(msg);
    exit(EXIT_FAILURE);
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Uzycie: " << argv[0] << " <sciezka_do_pliku> [ilosc_procesow]" << std::endl;
        return 1;
    }

    const char* filepath = argv[1];
    
    // 1. Ustalanie liczby procesów
    int num_processes = 0;
    if (argc >= 3) {
        num_processes = std::stoi(argv[2]);
    }
    if (num_processes < 1) {
        num_processes = std::thread::hardware_concurrency();
        if (num_processes == 0) num_processes = 1; // Fallback
    }

    std::cout << "Przetwarzanie pliku: " << filepath << std::endl;
    std::cout << "Liczba procesow: " << num_processes << std::endl;

    // 2. Otwarcie pliku i pobranie rozmiaru
    int fd = open(filepath, O_RDONLY);
    if (fd == -1) handleError("Blad otwarcia pliku");

    struct stat sb;
    if (fstat(fd, &sb) == -1) handleError("Blad fstat");
    size_t file_size = sb.st_size;

    if (file_size == 0) {
        std::cout << "Plik jest pusty." << std::endl;
        close(fd);
        return 0;
    }

    // 3. Mapowanie pliku do pamięci (mmap)
    char* file_content = (char*)mmap(NULL, file_size, PROT_READ, MAP_SHARED, fd, 0);
    if (file_content == MAP_FAILED) handleError("Blad mmap pliku");
    
    // Po zmapowaniu deskryptor pliku nie jest już konieczny
    close(fd);

    // 4. Alokacja anonimowej pamięci współdzielonej dla wyników i mutexa
    // MAP_ANONYMOUS | MAP_SHARED sprawia, że pamięć jest widoczna dla procesów potomnych
    SharedData* shared_mem = (SharedData*)mmap(NULL, sizeof(SharedData), 
                                               PROT_READ | PROT_WRITE, 
                                               MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    if (shared_mem == MAP_FAILED) handleError("Blad mmap shared memory");

    // Inicjalizacja struktury (zerowanie liczników i sumy)
    memset(shared_mem->letter_counts, 0, sizeof(shared_mem->letter_counts));
    shared_mem->sqrt_sum = 0.0;

    // 5. Inicjalizacja Mutexa w pamięci współdzielonej
    // WAŻNE: Mutex musi mieć atrybut PTHREAD_PROCESS_SHARED, aby działał między procesami
    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
    
    if (pthread_mutex_init(&shared_mem->mutex, &attr) != 0) handleError("Blad init mutex");
    pthread_mutexattr_destroy(&attr);

    // 6. Tworzenie procesów (Fork)
    size_t chunk_size = file_size / num_processes;
    
    for (int i = 0; i < num_processes; ++i) {
        pid_t pid = fork();

        if (pid == -1) {
            handleError("Blad fork");
        } else if (pid == 0) {
            // --- KOD PROCESU POTOMNEGO ---
            
            // Oblicz zakres dla tego procesu
            size_t start_idx = i * chunk_size;
            size_t end_idx = (i == num_processes - 1) ? file_size : (i + 1) * chunk_size;

            // Zmienne LOKALNE do akumulacji wyników (Optymalizacja użycia mutexa)
            // Dzięki temu blokujemy mutex tylko RAZ na proces, a nie dla każdego znaku.
            unsigned int local_counts[26] = {0};
            double local_sqrt_sum = 0.0;

            for (size_t k = start_idx; k < end_idx; ++k) {
                unsigned char c = file_content[k];

                // Zadanie 1: Zliczanie liter (case insensitive)
                if (std::isalpha(c)) {
                    // tolower zmienia 'A'->'a', odejmujemy 'a' by dostać indeks 0-25
                    int idx = std::tolower(c) - 'a';
                    if (idx >= 0 && idx < 26) {
                        local_counts[idx]++;
                    }
                }

                // Zadanie 2: Suma pierwiastków kodów ASCII (wszystkich znaków)
                local_sqrt_sum += std::sqrt((double)c);
            }

            // Sekcja krytyczna - aktualizacja pamięci współdzielonej
            pthread_mutex_lock(&shared_mem->mutex);
            
            for (int j = 0; j < 26; ++j) {
                shared_mem->letter_counts[j] += local_counts[j];
            }
            shared_mem->sqrt_sum += local_sqrt_sum;

            pthread_mutex_unlock(&shared_mem->mutex);

            // Zakończenie procesu potomnego
            munmap(file_content, file_size); // Dobre praktyki (choć OS i tak posprząta przy exit)
            exit(0);
        }
    }

    // 7. Oczekiwanie na procesy potomne (Parent Process)
    for (int i = 0; i < num_processes; ++i) {
        wait(NULL);
    }

    // 8. Wypisanie wyników
    std::cout << "\n--- Wyniki ---\n";
    std::cout << "Suma pierwiastkow kodow ASCII: " << std::fixed << shared_mem->sqrt_sum << std::endl;
    std::cout << "Czestotliwosc wystepowania liter:" << std::endl;
    
    for (int i = 0; i < 26; ++i) {
        char current_char = 'a' + i;
        std::cout << current_char << ": " << shared_mem->letter_counts[i] << std::endl;
    }

    // 9. Sprzątanie
    pthread_mutex_destroy(&shared_mem->mutex);
    munmap(shared_mem, sizeof(SharedData));
    munmap(file_content, file_size);

    return 0;
}