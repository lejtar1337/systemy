#!/bin/bash


if [ $# -eq 0 ]; then
    echo "Użycie: $0 <katalog1> [katalog2] ..."
    exit 1
fi

tmp_dir=$(mktemp -d)

trap "rm -rf $tmp_dir" EXIT

programs=("gzip" "bzip2" "xz" "zstd" "lz4" "7z")

for input_dir in "$@"; do
    echo "$input_dir"
    
    
    base_name=$(basename "$input_dir")
    tar cvf "$tmp_dir/archive.tar" -C "$(dirname "$input_dir")" "$base_name" 2>/dev/null
    
    orig_size=$(stat -c%s "$tmp_dir/archive.tar")
    
    printf "name\tcompress\tdecompress\tratio\n"
    
    for prog in "${programs[@]}"; do
        
        
        case $prog in
            gzip)  ext="gz";  cmd_c="gzip -k -f"; cmd_d="gzip -d -k -f" ;;
            bzip2) ext="bz2"; cmd_c="bzip2 -k -f"; cmd_d="bzip2 -d -k -f" ;;
            xz)    ext="xz";  cmd_c="xz -k -f"; cmd_d="xz -d -k -f" ;;
            zstd)  ext="zst"; cmd_c="zstd -k -f -q"; cmd_d="zstd -d -k -f -q" ;;
            lz4)   ext="lz4"; cmd_c="lz4 -f -q"; cmd_d="lz4 -d -f -q" ;;
            7z)    ext="7z";  cmd_c="7z a -bd -y"; cmd_d="7z x -bd -y" ;; 
        esac

        target_file="$tmp_dir/archive.tar.$ext"
        source_tar="$tmp_dir/archive.tar"

        #kompresja
        start=$(date +%s.%N)
        if [ "$prog" == "7z" ]; then
            
            $cmd_c "$target_file" "$source_tar" > /dev/null
        else
            
            $cmd_c "$source_tar"
        fi
        end=$(date +%s.%N)
        comp_time=$(echo "$end - $start" | bc -l)

        
        if [ -f "$target_file" ]; then
            comp_size=$(stat -c%s "$target_file")
            ratio=$(echo "scale=2; ($comp_size / $orig_size) * 100" | bc -l)
        else
            ratio="ERROR"
            comp_size=0
        fi

        # --- DEKOMPRESJA ---
        
        
        start=$(date +%s.%N)
        if [ "$prog" == "7z" ]; then
            $cmd_d "$target_file" -o"$tmp_dir/out_$prog" > /dev/null
        elif [ "$prog" == "lz4" ]; then
             $cmd_d "$target_file" "$tmp_dir/archive_decompressed.tar"
        else
            mv "$target_file" "$tmp_dir/temp_comp.$ext"
            $cmd_d "$tmp_dir/temp_comp.$ext"
        fi
        end=$(date +%s.%N)
        decomp_time=$(echo "$end - $start" | bc -l)

        # Wypisanie wyników (formatowanie printf)
        # LC_NUMERIC=C zapewnia kropkę zamiast przecinka w liczbach zmiennoprzecinkowych
        LC_NUMERIC=C printf "%s\t%.9f\t%.9f\t%s%%\n" "$prog" "$comp_time" "$decomp_time" "$ratio"


        # Usuń plik skompresowany
        rm -f "$target_file" "$tmp_dir/temp_comp.$ext" 
        # Usuń plik/folder po dekompresji
        rm -f "$tmp_dir/temp_comp" "$tmp_dir/archive_decompressed.tar"
        rm -rf "$tmp_dir/out_$prog"
    done
    
    echo ""
    # Usuwamy główny tar przed następną iteracją pętli katalogów
    rm -f "$tmp_dir/archive.tar"

done
