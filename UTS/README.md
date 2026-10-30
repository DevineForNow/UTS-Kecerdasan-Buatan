Python 3.10 atau lebih baru.

Missionaries and Cannibals: perbandingan BFS dan DFS.

Pastikan isi folder :
Folder
|- inputs
|   |-file.csv
|
|- results
|   |-hasil_eksperimen.csv
|
|- main.py
|
|- Readme.md

Cara menjalankan:
  ctrl + alt + n / run code di main.py
  Pilih [0-1] (default 1): (masukan pilihan nomer)                         # menu interaktif
  Path file CSV (Enter = inputs/mudah_3m3c_kap2.csv, 0 = kembali ke menu): (masukan file.csv)
  Algoritma [bfs/dfs/both] (default both): (masukan bfs/dfs/both)
  Aktifkan mode trace? [y/N]: (pilih y/N)
  Output ....

  Atau

  python main.py --input (nama folder)/(nama file.csv) --algo (pilih algoritma bfs/dfs/both) --log (nama file.csv simpan/hasil)

Contoh :
  ctrl + alt + n / run code di main.py
  === Missionaries and Cannibals : BFS vs DFS ===
  Sumber input kasus:
    [1] Baca dari file CSV
    [0] Keluar
  Pilih [0-1] (default 1): 1
  Path file CSV (Enter = inputs/mudah_3m3c_kap2.csv, 0 = kembali ke menu): inputs/mudah_3m3c_kap2.csv
  Algoritma [bfs/dfs/both] (default both): both
  Aktifkan mode trace? [y/N]: y
  Output :
  State awal   : (3,3,1)   Goal: (0,0,0)
  Operator     : 1M 2M 1C 2C 1M1C

  ==================== BFS ====================
  [TRACE BFS] urutan operator: 1M 2M 1C 2C 1M1C
    Aturan: BFS (FIFO), visited=ya
    Frontier awal: [(3,3,1)]
    #1 expand (3,3,1) depth=0
        anak: (3,2,0)[1C] (3,1,0)[2C] (2,2,0)[1M1C]
        frontier: [(3,2,0), (3,1,0), (2,2,0)]
    #2 expand (3,2,0) depth=1
        anak: (tidak ada)
        frontier: [(3,1,0), (2,2,0)]
    #3 expand (3,1,0) depth=1
        anak: (3,2,1)[1C]
        frontier: [(2,2,0), (3,2,1)]
    #4 expand (2,2,0) depth=1
        anak: (tidak ada)
        frontier: [(3,2,1)]
    #5 expand (3,2,1) depth=2
        anak: (3,0,0)[2C]
        frontier: [(3,0,0)]
    #6 expand (3,0,0) depth=3
        anak: (3,1,1)[1C]
        frontier: [(3,1,1)]
    #7 expand (3,1,1) depth=4
        anak: (1,1,0)[2M]
        frontier: [(1,1,0)]
    #8 expand (1,1,0) depth=5
        anak: (2,2,1)[1M1C]
        frontier: [(2,2,1)]
    #9 expand (2,2,1) depth=6
        anak: (0,2,0)[2M]
        frontier: [(0,2,0)]
    #10 expand (0,2,0) depth=7
        anak: (0,3,1)[1C]
        frontier: [(0,3,1)]
    #11 expand (0,3,1) depth=8
        anak: (0,1,0)[2C]
        frontier: [(0,1,0)]
    #12 expand (0,1,0) depth=9
        anak: (1,1,1)[1M] (0,2,1)[1C]
        frontier: [(1,1,1), (0,2,1)]
    #13 expand (1,1,1) depth=10
        anak: (0,0,0)[1M1C]
        frontier: [(0,2,1), (0,0,0)]
    #14 expand (0,2,1) depth=10
        anak: (tidak ada)
        frontier: [(0,0,0)]
    GOAL ditemukan: (0,0,0) pada kedalaman 11
  [AKHIR TRACE]

    Status                  : SOLUSI DITEMUKAN
    Jumlah langkah          : 11
    Biaya total             : 11 (11 x 1)
    Node expanded           : 14
    Node generated          : 15
    Ukuran frontier terbesar: 3
    Waktu eksekusi          : rata-rata 0.0552 ms (min 0.0490, maks 0.0694, 5 kali)
    Jalur solusi:
      Awal       : (3,3,1)
      Langkah  1 : 2C   -> (3,1,0)
      Langkah  2 : 1C   <- (3,2,1)
      Langkah  3 : 2C   -> (3,0,0)
      Langkah  4 : 1C   <- (3,1,1)
      Langkah  5 : 2M   -> (1,1,0)
      Langkah  6 : 1M1C <- (2,2,1)
      Langkah  7 : 2M   -> (0,2,0)
      Langkah  8 : 1C   <- (0,3,1)
      Langkah  9 : 2C   -> (0,1,0)
      Langkah 10 : 1M   <- (1,1,1)
      Langkah 11 : 1M1C -> (0,0,0)
    [LOG] Hasil BFS disimpan ke: results/hasil_eksperimen.csv

  ==================== DFS ====================
  [TRACE DFS] urutan operator: 1M 2M 1C 2C 1M1C
    Aturan: DFS (LIFO, anak didorong terbalik), visited=ya
    Frontier awal: [(3,3,1)]
    #1 expand (3,3,1) depth=0
        anak: (3,2,0)[1C] (3,1,0)[2C] (2,2,0)[1M1C]
        frontier: [(3,2,0), (3,1,0), (2,2,0)]
    #2 expand (3,2,0) depth=1
        anak: (3,3,1)[1C]
        frontier: [(3,3,1), (3,1,0), (2,2,0)]
    [skip] (3,3,1) sudah explored
    #3 expand (3,1,0) depth=1
        anak: (3,2,1)[1C] (3,3,1)[2C]
        frontier: [(3,2,1), (3,3,1), (2,2,0)]
    #4 expand (3,2,1) depth=2
        anak: (2,2,0)[1M] (3,1,0)[1C] (3,0,0)[2C]
        frontier: [(2,2,0), (3,1,0), (3,0,0), (3,3,1), (2,2,0)]
    #5 expand (2,2,0) depth=3
        anak: (3,2,1)[1M] (3,3,1)[1M1C]
        frontier: [(3,2,1), (3,3,1), (3,1,0), (3,0,0), (3,3,1), (2,2,0)]
    [skip] (3,2,1) sudah explored
    [skip] (3,3,1) sudah explored
    [skip] (3,1,0) sudah explored
    #6 expand (3,0,0) depth=3
        anak: (3,1,1)[1C] (3,2,1)[2C]
        frontier: [(3,1,1), (3,2,1), (3,3,1), (2,2,0)]
    #7 expand (3,1,1) depth=4
        anak: (1,1,0)[2M] (3,0,0)[1C]
        frontier: [(1,1,0), (3,0,0), (3,2,1), (3,3,1), (2,2,0)]
    #8 expand (1,1,0) depth=5
        anak: (3,1,1)[2M] (2,2,1)[1M1C]
        frontier: [(3,1,1), (2,2,1), (3,0,0), (3,2,1), (3,3,1), (2,2,0)]
    [skip] (3,1,1) sudah explored
    #9 expand (2,2,1) depth=6
        anak: (0,2,0)[2M] (1,1,0)[1M1C]
        frontier: [(0,2,0), (1,1,0), (3,0,0), (3,2,1), (3,3,1), (2,2,0)]
    #10 expand (0,2,0) depth=7
        anak: (2,2,1)[2M] (0,3,1)[1C]
        frontier: [(2,2,1), (0,3,1), (1,1,0), (3,0,0), (3,2,1), (3,3,1), (2,2,0)]
    [skip] (2,2,1) sudah explored
    #11 expand (0,3,1) depth=8
        anak: (0,2,0)[1C] (0,1,0)[2C]
        frontier: [(0,2,0), (0,1,0), (1,1,0), (3,0,0), (3,2,1), (3,3,1), (2,2,0)]
    [skip] (0,2,0) sudah explored
    #12 expand (0,1,0) depth=9
        anak: (1,1,1)[1M] (0,2,1)[1C] (0,3,1)[2C]
        frontier: [(1,1,1), (0,2,1), (0,3,1), (1,1,0), (3,0,0), (3,2,1), (3,3,1), (2,2,0)]
    #13 expand (1,1,1) depth=10
        anak: (0,1,0)[1M] (0,0,0)[1M1C]
        frontier: [(0,1,0), (0,0,0), (0,2,1), (0,3,1), (1,1,0), (3,0,0), (3,2,1), (3,3,1), (2,2,0)]
    [skip] (0,1,0) sudah explored
    GOAL ditemukan: (0,0,0) pada kedalaman 11
  [AKHIR TRACE]

    Status                  : SOLUSI DITEMUKAN
    Jumlah langkah          : 11
    Biaya total             : 11 (11 x 1)
    Node expanded           : 13
    Node generated          : 29
    Ukuran frontier terbesar: 9
    Waktu eksekusi          : rata-rata 0.0576 ms (min 0.0511, maks 0.0701, 5 kali)
    Jalur solusi:
      Awal       : (3,3,1)
      Langkah  1 : 2C   -> (3,1,0)
      Langkah  2 : 1C   <- (3,2,1)
      Langkah  3 : 2C   -> (3,0,0)
      Langkah  4 : 1C   <- (3,1,1)
      Langkah  5 : 2M   -> (1,1,0)
      Langkah  6 : 1M1C <- (2,2,1)
      Langkah  7 : 2M   -> (0,2,0)
      Langkah  8 : 1C   <- (0,3,1)
      Langkah  9 : 2C   -> (0,1,0)
      Langkah 10 : 1M   <- (1,1,1)
      Langkah 11 : 1M1C -> (0,0,0)
    [LOG] Hasil DFS disimpan ke: results/hasil_eksperimen.csv

  hasil_eksperimen.csv:
  inputs/test.csv,BFS,tanpa_solusi,-,-,13,13,3,0.04646000089,5
  inputs/test.csv,DFS,tanpa_solusi,-,-,13,27,7,0.05215999918,5