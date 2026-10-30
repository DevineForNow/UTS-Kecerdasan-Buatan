import argparse
import csv
import os
import sys
import time
from collections import deque

def config_default():
    return {
        "missionaries": 3, "cannibals": 3, "boat_capacity": 2,
        "start_boat": 1, "goal_m": 0, "goal_c": 0, "goal_boat": 0,
        "operator_order": "auto", "step_cost": 1, "max_depth": 0,
        "use_visited": True, "max_nodes": 5_000_000, "repeat": 5,
    }


NAMA_PARAMETER = list(config_default())


def parse_int(value, name, low, high):
    try:
        number = int(value)
    except ValueError:
        raise ValueError(f"nilai '{name}' harus bilangan bulat, ditemukan: '{value}'")
    if not low <= number <= high:
        raise ValueError(f"nilai '{name}' di luar rentang [{low}, {high}]: {value}")
    return number


def parse_boat(value, name):
    value = value.strip().lower()
    if value in ("l", "1", "kiri", "left"):
        return 1
    if value in ("r", "0", "kanan", "right"):
        return 0
    raise ValueError(f"nilai '{name}' harus 1/L (kiri) atau 0/R (kanan), ditemukan: '{value}'")


def parse_bool(value, name):
    value = value.strip().lower()
    if value in ("true", "1", "yes", "ya"):
        return True
    if value in ("false", "0", "no", "tidak"):
        return False
    raise ValueError(f"nilai '{name}' harus true/false, ditemukan: '{value}'")


def set_param(cfg, key, value):
    key, value = key.strip().lower(), value.strip()
    if key in ("missionaries", "cannibals", "goal_m", "goal_c"):
        cfg[key] = parse_int(value, key, 0, 1000)
    elif key == "boat_capacity":
        cfg[key] = parse_int(value, key, 1, 1000)
    elif key in ("start_boat", "goal_boat"):
        cfg[key] = parse_boat(value, key)
    elif key == "operator_order":
        if not value:
            raise ValueError("operator_order tidak boleh kosong")
        cfg[key] = value
    elif key in ("step_cost", "max_depth"):
        cfg[key] = parse_int(value, key, 0, 1_000_000)
    elif key == "use_visited":
        cfg[key] = parse_bool(value, key)
    elif key == "max_nodes":
        cfg[key] = parse_int(value, key, 1, 2_000_000_000)
    elif key == "repeat":
        cfg[key] = parse_int(value, key, 1, 100_000)
    else:
        raise ValueError(f"parameter tidak dikenal: '{key}'")


def load_csv(path, cfg):
    """Baca CSV berformat parameter,nilai[,keterangan]; abaikan baris kosong/#."""
    try:
        file = open(path, newline="", encoding="utf-8-sig")
    except OSError:
        raise ValueError(f"File tidak dapat dibuka: '{path}' (cek nama file / folder)")
    with file:
        for line_no, row in enumerate(file, 1):
            line = row.strip()
            if not line or line.startswith("#"):
                continue
            cols = next(csv.reader([line]))
            if len(cols) < 2:
                raise ValueError(f"Baris {line_no}: format harus 'parameter,nilai' -> '{line}'")
            key, value = cols[0].strip(), cols[1].strip()
            if key.lower() == "parameter":
                continue
            try:
                set_param(cfg, key, value)
            except ValueError as exc:
                raise ValueError(f"Baris {line_no}: {exc}")


# ------------------------------ Model ------------------------------
def nama_operator(m, c):
    return (f"{m}M" if m else "") + (f"{c}C" if c else "")


def str_state(state):
    return f"({state[0]},{state[1]},{state[2]})"


def state_aman(m, c, total_m, total_c):
    mr, cr = total_m - m, total_c - c
    return (m >= 0 and c >= 0 and mr >= 0 and cr >= 0
            and (m == 0 or m >= c) and (mr == 0 or mr >= cr))


def alasan_ilegal(m, c, total_m, total_c):
    mr, cr = total_m - m, total_c - c
    if min(m, c, mr, cr) < 0:
        return "jumlah orang di luar rentang 0..total"
    if m > 0 and c > m:
        return f"sisi kiri: cannibals ({c}) > missionaries ({m})"
    if mr > 0 and cr > mr:
        return f"sisi kanan: cannibals ({cr}) > missionaries ({mr})"
    return ""


def parse_operator(spec, capacity):
    ops = []
    if spec.strip().lower() == "auto":
        ops += [(m, 0, nama_operator(m, 0)) for m in range(1, capacity + 1)]
        ops += [(0, c, nama_operator(0, c)) for c in range(1, capacity + 1)]
        for total in range(2, capacity + 1):
            ops += [(m, total - m, nama_operator(m, total - m))
                    for m in range(1, total)]
        return ops

    for token in spec.split(";"):
        token = token.strip()
        if not token:
            continue
        m = c = 0
        digits = ""
        for char in token:
            if char.isdigit():
                digits += char
            elif char.upper() in ("M", "C") and digits:
                if char.upper() == "M":
                    m += int(digits)
                else:
                    c += int(digits)
                digits = ""
            else:
                raise ValueError(f"operator '{token}' salah format (contoh benar: 1M, 2C, 1M1C)")
        if digits:
            raise ValueError(f"operator '{token}' salah format: angka harus diikuti M atau C")
        if m + c < 1:
            raise ValueError(f"operator '{token}' tidak membawa siapa pun")
        if m + c > capacity:
            raise ValueError(f"operator '{token}' membawa {m+c} orang > kapasitas perahu ({capacity})")
        if any(old_m == m and old_c == c for old_m, old_c, _ in ops):
            raise ValueError(f"operator '{token}' muncul lebih dari sekali")
        ops.append((m, c, nama_operator(m, c)))
    if not ops:
        raise ValueError("operator_order tidak berisi operator")
    return ops


def buat_masalah(cfg):
    tm, tc = cfg["missionaries"], cfg["cannibals"]
    if cfg["goal_m"] > tm:
        raise ValueError(f"goal_m ({cfg['goal_m']}) > jumlah missionaries ({tm})")
    if cfg["goal_c"] > tc:
        raise ValueError(f"goal_c ({cfg['goal_c']}) > jumlah cannibals ({tc})")
    start = (tm, tc, cfg["start_boat"])
    goal = (cfg["goal_m"], cfg["goal_c"], cfg["goal_boat"])
    for label, state in (("awal", start), ("goal", goal)):
        if not state_aman(state[0], state[1], tm, tc):
            raise ValueError(f"state {label} {str_state(state)} ILEGAL: "
                             f"{alasan_ilegal(state[0], state[1], tm, tc)}")
    try:
        ops = parse_operator(cfg["operator_order"], cfg["boat_capacity"])
    except ValueError as exc:
        raise ValueError(f"operator_order: {exc}")
    return {"tm": tm, "tc": tc, "awal": start, "goal": goal, "ops": ops,
            **{key: cfg[key] for key in ("step_cost", "max_depth", "use_visited", "max_nodes")}}


def successors(problem, state):
    m, c, boat = state
    out = []
    for index, (om, oc, _) in enumerate(problem["ops"]):
        if boat:  # kiri ke kanan
            if m < om or c < oc:
                continue
            new = (m - om, c - oc, 0)
        else:     # kanan ke kiri
            if problem["tm"] - m < om or problem["tc"] - c < oc:
                continue
            new = (m + om, c + oc, 1)
        if state_aman(new[0], new[1], problem["tm"], problem["tc"]):
            out.append((new, index))
    return out


# ---------------------------- BFS dan DFS -------------------------
def str_frontier(frontier, nodes, bfs):
    limit = 14
    order = list(frontier) if bfs else list(reversed(frontier))
    text = ", ".join(str_state(nodes[i]["s"]) for i in order[:limit])
    if len(order) > limit:
        text += f", ... (+{len(order)-limit})"
    return f"[{text}]"


def cari(problem, bfs, trace=False):
    result = {"found": False, "limit_hit": False, "depth_cut": False,
              "expanded": 0, "generated": 1, "max_frontier": 1,
              "steps": 0, "cost": 0, "path_states": [], "path_ops": []}
    nodes = [{"s": problem["awal"], "parent": -1, "op": -1, "depth": 0}]
    frontier, seen = deque([0]), set()
    if problem["use_visited"] and bfs:
        seen.add(problem["awal"])
    if trace:
        rule = "BFS (FIFO)" if bfs else "DFS (LIFO, anak didorong terbalik)"
        print(f"  Aturan: {rule}, visited={'ya' if problem['use_visited'] else 'tidak'}")
        print(f"  Frontier awal: {str_frontier(frontier, nodes, bfs)}")

    while frontier:
        idx = frontier.popleft() if bfs else frontier.pop()
        cur, state = nodes[idx], nodes[idx]["s"]
        if not bfs and problem["use_visited"]:
            if state in seen:
                if trace:
                    print(f"  [skip] {str_state(state)} sudah explored")
                continue
            seen.add(state)
        if state == problem["goal"]:
            result["found"] = True
            chain, parent = [], idx
            while parent != -1:
                chain.append(parent)
                parent = nodes[parent]["parent"]
            for j in reversed(chain):
                result["path_states"].append(nodes[j]["s"])
                if nodes[j]["op"] >= 0:
                    result["path_ops"].append(nodes[j]["op"])
            result["steps"] = len(chain) - 1
            result["cost"] = result["steps"] * problem["step_cost"]
            if trace:
                print(f"  GOAL ditemukan: {str_state(state)} pada kedalaman {cur['depth']}")
            return result

        result["expanded"] += 1
        if trace:
            print(f"  #{result['expanded']} expand {str_state(state)} depth={cur['depth']}")
        if problem["max_depth"] and cur["depth"] >= problem["max_depth"]:
            result["depth_cut"] = True
            if trace:
                print(f"      (batas kedalaman {problem['max_depth']} tercapai, tidak diperluas)")
            continue

        children = []
        for new_state, op in successors(problem, state):
            if bfs and problem["use_visited"]:
                if new_state in seen:
                    continue
                seen.add(new_state)
            nodes.append({"s": new_state, "parent": idx, "op": op, "depth": cur["depth"] + 1})
            result["generated"] += 1
            children.append(len(nodes) - 1)
        frontier.extend(children if bfs else reversed(children))
        result["max_frontier"] = max(result["max_frontier"], len(frontier))
        if trace:
            kids = " ".join(f"{str_state(nodes[i]['s'])}[{problem['ops'][nodes[i]['op']][2]}]"
                            for i in children) or "(tidak ada)"
            print(f"      anak: {kids}")
            print(f"      frontier: {str_frontier(frontier, nodes, bfs)}")
        if len(nodes) > problem["max_nodes"]:
            result["limit_hit"] = True
            return result
    return result


# ----------------------------- Hasil dan log -----------------------
HEADER_LOG = ["input", "algoritma", "status", "langkah", "biaya", "expanded",
              "generated", "frontier_maks", "waktu_rata2_ms", "repeat"]


def cetak_jalur(problem, result):
    count = len(result["path_ops"])
    no_width = len(str(count))
    op_width = max((len(problem["ops"][op][2]) for op in result["path_ops"]), default=0)
    print("  Jalur solusi:")
    print(f"    {'Awal':<{8+no_width}} : {str_state(result['path_states'][0])}")
    for i, op in enumerate(result["path_ops"]):
        arrow = "->" if result["path_states"][i][2] == 1 else "<-"
        label = f"Langkah {i+1:>{no_width}}"
        print(f"    {label} : {problem['ops'][op][2]:<{op_width}} {arrow} "
              f"{str_state(result['path_states'][i+1])}")


def teks_status(result, problem):
    if result["found"]:
        return "SOLUSI DITEMUKAN"
    if result["limit_hit"]:
        return f"DIHENTIKAN: batas max_nodes ({problem['max_nodes']}) tercapai, solusi belum ditemukan"
    if result["depth_cut"]:
        return f"TIDAK DITEMUKAN dalam batas kedalaman {problem['max_depth']} (belum tentu tidak ada solusi)"
    return "TIDAK ADA SOLUSI (seluruh state yang dapat dicapai sudah dijelajahi)"


def simpan_log(path, new_row):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    old_rows = []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8-sig") as file:
            old_rows = list(csv.reader(file))
    if old_rows and old_rows[0] != HEADER_LOG:
        print(f"[PERINGATAN] Header file log '{path}' tidak sesuai. File tidak ditimpa.")
        return
    rows, replaced = [HEADER_LOG], False
    for row in old_rows[1:] if old_rows else []:
        if not row:
            continue
        if len(row) >= 2 and row[:2] == new_row[:2]:
            if not replaced:
                rows.append(new_row)
                replaced = True
        else:
            rows.append(row)
    if not replaced:
        rows.append(new_row)
    with open(path, "w", newline="", encoding="utf-8") as file:
        csv.writer(file).writerows(rows)
    print(f"  [LOG] Hasil {new_row[1]} disimpan ke: {path}")


def jalankan_algoritma(problem, cfg, bfs, trace, input_name, log_path):
    name = "BFS" if bfs else "DFS"
    print(f"\n==================== {name} ====================")
    if trace:
        print(f"[TRACE {name}] urutan operator: " + " ".join(op[2] for op in problem["ops"]))
        cari(problem, bfs, trace=True)  # trace tidak dimasukkan ke pengukuran waktu
        print("[AKHIR TRACE]\n")
    timings = []
    result = None
    for _ in range(cfg["repeat"]):
        start = time.perf_counter()
        result = cari(problem, bfs)
        timings.append((time.perf_counter() - start) * 1000)
    average = sum(timings) / len(timings)
    print(f"  Status                  : {teks_status(result, problem)}")
    print(f"  Jumlah langkah          : {result['steps'] if result['found'] else '-'}")
    print(f"  Biaya total             : {result['cost']} ({result['steps']} x {problem['step_cost']})" if result["found"] else "  Biaya total             : -")
    print(f"  Node expanded           : {result['expanded']}")
    print(f"  Node generated          : {result['generated']}")
    print(f"  Ukuran frontier terbesar: {result['max_frontier']}")
    print(f"  Waktu eksekusi          : rata-rata {average:.4f} ms (min {min(timings):.4f}, maks {max(timings):.4f}, {cfg['repeat']} kali)")
    if result["found"]:
        cetak_jalur(problem, result)
    status = ("solusi" if result["found"] else "batas_node" if result["limit_hit"]
              else "batas_depth" if result["depth_cut"] else "tanpa_solusi")
    simpan_log(log_path, [input_name, name, status,
                         result["steps"] if result["found"] else "-",
                         result["cost"] if result["found"] else "-",
                         result["expanded"], result["generated"], result["max_frontier"],
                         f"{average:.10g}", cfg["repeat"]])


def cetak_config(cfg, problem, input_name):
    print("============== PARAMETER KASUS ==============")
    print(f"Sumber input : {input_name}")
    for key in NAMA_PARAMETER:
        value = str(cfg[key]).lower() if isinstance(cfg[key], bool) else cfg[key]
        print(f"  {key:<15} = {value}")
    print(f"State awal   : {str_state(problem['awal'])}   Goal: {str_state(problem['goal'])}")
    print("Operator     : " + " ".join(op[2] for op in problem["ops"]))


# ------------------------------- Menu ------------------------------
def baca_baris(prompt):
    try:
        return input(prompt)
    except EOFError:
        print()
        return None


def menu_interaktif(cfg):
    while True:
        print("\n=== Missionaries and Cannibals : BFS vs DFS ===")
        print("Sumber input kasus:\n  [1] Baca dari file CSV\n  [0] Keluar")
        choice = baca_baris("Pilih [0-1] (default 1): ")
        if choice is None or choice.strip() == "0":
            print("Keluar.")
            return None
        if (choice.strip() or "1") != "1":
            print(f"[ERROR] pilihan tidak valid: '{choice}'. Coba lagi.")
            continue
        while True:
            path = baca_baris("Path file CSV (Enter = inputs/mudah_3m3c_kap2.csv, 0 = kembali ke menu): ")
            if path is None:
                return None
            path = path.strip()
            if path == "0":
                break
            path = path or "inputs/mudah_3m3c_kap2.csv"
            new_cfg = config_default()
            try:
                load_csv(path, new_cfg)
                cfg.update(new_cfg)
                return path
            except ValueError as exc:
                print(f"[ERROR FORMAT INPUT] {exc}\n  Coba lagi.")


def main():
    parser = argparse.ArgumentParser(description="Missionaries and Cannibals: BFS vs DFS")
    parser.add_argument("--input", default="", help="file CSV input; tanpa ini, tampilkan menu")
    parser.add_argument("--algo", choices=("bfs", "dfs", "both"), help="algoritma; default both")
    parser.add_argument("--trace", action="store_true", help="tampilkan proses expand dan frontier")
    parser.add_argument("--set", action="append", default=[], metavar="kunci=nilai", help="timpa parameter")
    parser.add_argument("--repeat", type=int, help="jumlah pengulangan pengukuran waktu")
    parser.add_argument("--log", default="results/hasil_eksperimen.csv", help="lokasi file log CSV")
    args = parser.parse_args()

    cfg, input_name = config_default(), args.input
    interactive = not input_name
    if interactive:
        input_name = menu_interaktif(cfg)
        if input_name is None:
            return 0
    else:
        try:
            load_csv(input_name, cfg)
        except ValueError as exc:
            print(f"[ERROR FORMAT INPUT] {exc}", file=sys.stderr)
            return 1

    overrides = [("repeat", str(args.repeat))] if args.repeat is not None else []
    for item in args.set:
        if "=" not in item:
            print(f"[ERROR ARGUMEN] --set harus berbentuk kunci=nilai, ditemukan: '{item}'", file=sys.stderr)
            return 1
        overrides.append(tuple(item.split("=", 1)))
    try:
        for key, value in overrides:
            set_param(cfg, key, value)
    except ValueError as exc:
        print(f"[ERROR ARGUMEN] {exc}", file=sys.stderr)
        return 1

    algo, trace = args.algo or "both", args.trace
    if interactive:
        if args.algo is None:
            algo = (baca_baris("Algoritma [bfs/dfs/both] (default both): ") or "").strip().lower() or "both"
            if algo not in ("bfs", "dfs", "both"):
                print(f"[ERROR] algoritma tidak valid: '{algo}'", file=sys.stderr)
                return 1
        if not trace:
            trace = (baca_baris("Aktifkan mode trace? [y/N]: ") or "").strip().lower() in ("y", "ya", "yes")
    try:
        problem = buat_masalah(cfg)
    except ValueError as exc:
        print(f"[ERROR FORMAT INPUT] {exc}", file=sys.stderr)
        return 1

    print()
    cetak_config(cfg, problem, input_name)
    if algo in ("bfs", "both"):
        jalankan_algoritma(problem, cfg, True, trace, input_name, args.log)
    if algo in ("dfs", "both"):
        jalankan_algoritma(problem, cfg, False, trace, input_name, args.log)
    return 0


if __name__ == "__main__":
    sys.exit(main())