#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <thread>
#include <mutex>
#include <cmath>
#include <cctype>
#include <algorithm>

#define LETTER_COUNT 26

struct context {
    std::string content;
    unsigned long count[LETTER_COUNT] = {0};
    double sumOfSqrt = 0; 
    std::mutex mtx;
};

void worker(const std::string& data, size_t start, size_t end, context& ctx) {
   
    unsigned long local_count[LETTER_COUNT] = {0};
    double local_sum = 0.0;

    for (size_t i = start; i < end; ++i) {
        unsigned char c = static_cast<unsigned char>(data[i]);
        
        
        local_sum += std::sqrt(static_cast<double>(c));

       
        if (std::isalpha(c)) {
            char lower_c = std::tolower(c);
            if (lower_c >= 'a' && lower_c <= 'z') {
                local_count[lower_c - 'a']++;
            }
        }
    }

    std::lock_guard<std::mutex> lock(ctx.mtx);
    for (int i = 0; i < LETTER_COUNT; ++i) {
        ctx.count[i] += local_count[i];
    }
    ctx.sumOfSqrt += local_sum;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Użycie: " << argv[0] << " <plik> [ilość_wątków]" << std::endl;
        return 1;
    }

    
    std::ifstream file(argv[1], std::ios::binary);
    if (!file) {
        std::cerr << "Nie można otworzyć pliku!" << std::endl;
        return 1;
    }

    context ctx;
    file.seekg(0, std::ios::end);
    ctx.content.resize(file.tellg());
    file.seekg(0, std::ios::beg);
    file.read(&ctx.content[0], ctx.content.size());
    file.close();

    
    unsigned int num_threads = (argc >= 3) ? std::stoi(argv[2]) : std::thread::hardware_concurrency();
    if (num_threads == 0) num_threads = 1;

    std::vector<std::thread> threads;
    size_t total_size = ctx.content.size();
    size_t chunk_size = total_size / num_threads;


    for (unsigned int i = 0; i < num_threads; ++i) {
        size_t start = i * chunk_size;
        size_t end = (i == num_threads - 1) ? total_size : (i + 1) * chunk_size;
        
        threads.emplace_back(worker, std::ref(ctx.content), start, end, std::ref(ctx));
    }

    
    for (auto& t : threads) {
        t.join();
    }

    
    std::cout << "--- Statystyki liter (A-Z) ---" << std::endl;
    for (int i = 0; i < LETTER_COUNT; ++i) {
        std::cout << static_cast<char>('a' + i) << ": " << ctx.count[i] << "\t";
        if ((i + 1) % 4 == 0) std::cout << "\n";
    }
    
    std::cout << "\n\nSuma pierwiastków kodów ASCII: " << ctx.sumOfSqrt << std::endl;

    return 0;
}