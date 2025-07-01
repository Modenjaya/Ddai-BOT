from curl_cffi import requests
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, base64, time, json, os, pytz

# Impor klien API Anti-Captcha untuk Cloudflare Turnstile
from anticaptchaofficial.turnstileproxyless import *

wib = pytz.timezone('Asia/Jakarta')

class DDAI:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://app.ddai.space",
            "Referer": "https://app.ddai.space/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://auth.ddai.space"
        self.PAGE_URL = "https://app.ddai.space" # URL halaman tempat Turnstile muncul
        self.SITE_KEY = "0x4AAAAAABdw7Ezbqw4v6Kr1" # Kunci situs Cloudflare Turnstile Anda
        self.ANTICAPTCHA_API_KEY = self.load_anticaptcha_key() # Muat kunci API Anti-Captcha

        # Hapus semua atribut terkait proxy manual
        # self.proxies = []
        # self.proxy_index = 0
        # self.account_proxies = {}

        self.access_tokens = {}
        self.refresh_tokens = {}

    def load_anticaptcha_key(self):
        """Memuat kunci API Anti-Captcha dari sebuah file."""
        filename = "anticaptcha_key.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File '{filename}' tidak ditemukan. Harap buat dan masukkan kunci API Anti-Captcha Anda di dalamnya.{Style.RESET_ALL}")
                return None
            with open(filename, 'r') as f:
                key = f.readline().strip()
                if not key:
                    self.log(f"{Fore.RED}Kunci API Anti-Captcha tidak ditemukan di '{filename}'. Pastikan file tersebut berisi kunci Anda.{Style.RESET_ALL}")
                    return None
                return key
        except Exception as e:
            self.log(f"{Fore.RED}Gagal memuat kunci API Anti-Captcha: {e}{Style.RESET_ALL}")
            return None

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}DDAI Network - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "tokens.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Tidak Ditemukan.{Style.RESET_ALL}")
                return []

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []

    def save_tokens(self, new_accounts):
        filename = "tokens.json"
        try:
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, 'r') as file:
                    existing_accounts = json.load(file)
            else:
                existing_accounts = []

            account_dict = {acc["Email"]: acc for acc in existing_accounts}

            for new_acc in new_accounts:
                account_dict[new_acc["Email"]] = new_acc

            updated_accounts = list(account_dict.values())

            with open(filename, 'w') as file:
                json.dump(updated_accounts, file, indent=4)

        except Exception as e:
            return []

    # Hapus semua metode terkait proxy manual
    # async def load_proxies(self, use_proxy_choice: int):
    #     ...
    # def check_proxy_schemes(self, proxies):
    #     ...
    # def get_next_proxy_for_account(self, user_id):
    #     ...
    # def rotate_proxy_for_account(self, user_id):
    #     ...
            
    def get_token_exp_time(self, token: str):
        try:
            header, payload, signature = token.split(".")
            decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            exp_time = parsed_payload["exp"]
            
            return exp_time
        except Exception as e:
            return None
            
    def biner_to_desimal(self, troughput: str):
        desimal = int(troughput, 2)
        return desimal
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
    
    def print_message(self, account, color, message): # Hapus parameter proxy
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Akun:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        # Sederhanakan pertanyaan proxy karena Anti-Captcha menanganinya
        print(f"{Fore.WHITE + Style.BRIGHT}1. Jalankan Tanpa Proxy (Anti-Captcha menanganinya secara internal){Style.RESET_ALL}")
        while True:
            try:
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Pilih [1] -> {Style.RESET_ALL}").strip())

                if choose == 1:
                    print(f"{Fore.GREEN + Style.BRIGHT}Pilihan Jalankan Tanpa Proxy Terpilih.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Harap masukkan 1.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Input tidak valid. Masukkan 1.{Style.RESET_ALL}")

        # Opsi rotasi tidak lagi relevan
        return choose, False

    # Fungsi solve_recaptcha_v2 tidak lagi relevan, ini adalah Turnstile
    # async def solve_recaptcha_v2(self):
    #     ...

    async def onchain_trigger(self, user_id: str, retries=5): # Hapus parameter proxy
        url = f"{self.BASE_API}/onchainTrigger"
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": f"Bearer {self.access_tokens[user_id]}",
            "Content-Length":"0",
            "Origin": "chrome-extension://pigpomlidebemiifjihbgicepgbamdaj",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Storage-Access": "active",
            "User-Agent": FakeUserAgent().random
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, timeout=60, impersonate="chrome110", verify=False) # Hapus proxy
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(user_id, Fore.YELLOW, f"Onchain Trigger Gagal: {Fore.RED+Style.BRIGHT}{str(e)}") # Hapus proxy

        return None

    async def auth_refresh(self, email: str, retries=5): # Hapus parameter proxy
        url = f"{self.BASE_API}/refresh"
        data = json.dumps({"refreshToken":self.refresh_tokens[email]})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, timeout=60, impersonate="chrome110", verify=False) # Hapus proxy
                if response.status_code == 401:
                    self.print_message(email, Fore.RED, "Refresh Token Akses Gagal: " # Hapus proxy
                        f"{Fore.YELLOW + Style.BRIGHT}Sudah Kadaluarsa{Style.RESET_ALL}"
                    )
                    return None
                elif response.status_code == 403:
                    self.print_message(email, Fore.RED, "Refresh Token Akses Gagal: " # Hapus proxy
                        f"{Fore.YELLOW + Style.BRIGHT}Tidak Valid, JANGAN LOGOUT atau BUKA DASHBOARD DDAI SAAT BOT BERJALAN{Style.RESET_ALL}"
                    )
                    return None
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, Fore.YELLOW, f"Refresh Token Akses Gagal: {Fore.RED+Style.BRIGHT}{str(e)}") # Hapus proxy

        return None
            
    async def model_response(self, email: str, retries=5): # Hapus parameter proxy dan use_proxy, rotate_proxy
        url = f"{self.BASE_API}/modelResponse"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, timeout=60, impersonate="chrome110", verify=False) # Hapus proxy
                if response.status_code == 401:
                    await self.process_auth_refresh(email) # Hapus parameter proxy
                    headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                    continue
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, Fore.YELLOW, f"GET Data Throughput Gagal: {Fore.RED+Style.BRIGHT}{str(e)}") # Hapus proxy

        return None
    
    async def mission_lists(self, email: str, retries=5): # Hapus parameter proxy dan use_proxy, rotate_proxy
        url = f"{self.BASE_API}/missions"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, timeout=60, impersonate="chrome110", verify=False) # Hapus proxy
                if response.status_code == 401:
                    await self.process_auth_refresh(email) # Hapus parameter proxy
                    headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                    continue
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, Fore.YELLOW, f"GET Daftar Misi Gagal: {Fore.RED+Style.BRIGHT}{str(e)}") # Hapus proxy

        return None
    
    async def complete_missions(self, email: str, mission_id: str, title: str, retries=5): # Hapus parameter proxy dan use_proxy, rotate_proxy
        url = f"{self.BASE_API}/missions/claim/{mission_id}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}",
            "Content-Length":"0"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, timeout=60, impersonate="chrome110", verify=False) # Hapus proxy
                if response.status_code == 401:
                    await self.process_auth_refresh(email) # Hapus parameter proxy
                    headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                    continue
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, Fore.WHITE, f"Misi {title}" # Hapus proxy
                    f"{Fore.RED + Style.BRIGHT} Tidak Selesai: {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None

    async def process_auth_refresh(self, email: str): # Hapus parameter use_proxy, rotate_proxy
        while True:
            refresh = await self.auth_refresh(email) # Hapus parameter proxy
            if refresh:
                self.access_tokens[email] = refresh["data"]["accessToken"]

                self.save_tokens([{"Email":email, "accessToken":self.access_tokens[email], "refreshToken":self.refresh_tokens[email]}])
                self.print_message(email, Fore.GREEN, "Refresh Token Akses Berhasil") # Hapus proxy
                return True
            
            # Logika rotasi proxy dihapus
            await asyncio.sleep(5)
            continue
        
    async def check_token_exp_time(self, email: str): # Hapus parameter use_proxy, rotate_proxy
        exp_time = self.get_token_exp_time(self.access_tokens[email])

        if int(time.time()) > exp_time:
            self.print_message(email, Fore.YELLOW, "Token Akses Kadaluarsa, Merefresh...") # Hapus proxy
            await self.process_auth_refresh(email) # Hapus parameter proxy

        return True

    async def looping_auth_refresh(self, email: str): # Hapus parameter use_proxy, rotate_proxy
        while True:
            await asyncio.sleep(10 * 60)
            await self.process_auth_refresh(email) # Hapus parameter proxy

    async def process_onchain_trigger(self, email: str): # Hapus parameter use_proxy, rotate_proxy
        is_valid = await self.check_token_exp_time(email) # Hapus parameter proxy
        if is_valid:
            while True:
                model = await self.onchain_trigger(email) # Hapus parameter proxy
                if model:
                    req_total = model.get("data", {}).get("requestsTotal", 0)
                    self.print_message(email, Fore.GREEN, "Onchain Berhasil Dipicu " # Hapus proxy
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Total Permintaan: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{req_total}{Style.RESET_ALL}"
                    )
                    return True
                
                # Logika rotasi proxy dihapus
                await asyncio.sleep(5)
                continue
        
    async def process_model_response(self, email: str): # Hapus parameter use_proxy, rotate_proxy
        while True:
            model = await self.model_response(email) # Hapus parameter proxy
            if model:
                throughput = model.get("data", {}).get("throughput", 0)
                formatted_throughput = self.biner_to_desimal(throughput)

                self.print_message(email, Fore.GREEN, "Throughput " # Hapus proxy
                    f"{Fore.WHITE + Style.BRIGHT}{formatted_throughput}%{Style.RESET_ALL}"
                )

            await asyncio.sleep(60)

    async def process_user_missions(self, email: str): # Hapus parameter use_proxy, rotate_proxy
        while True:
            mission_lists = await self.mission_lists(email)
            if mission_lists:
                missions = mission_lists.get("data", {}).get("missions", [])

                if missions:
                    any_claimable_missions_found = False # Flag untuk melacak apakah ada misi yang bisa diklaim/sudah diklaim dalam siklus ini

                    for mission in missions:
                        if mission:
                            mission_id = mission.get("_id")
                            title = mission.get("title")
                            reward = mission.get("rewards", {}).get("requests", 0)
                            type = mission.get("type")
                            status = mission.get("status")

                            # Logika untuk mengklaim misi
                            if (type == 3 and status == "COMPLETED") or (status == "PENDING"):
                                claim = await self.complete_missions(email, mission_id, title)
                                if claim and claim.get("data", {}).get("claimed"):
                                    self.print_message(email, Fore.WHITE, f"Misi {title}"
                                        f"{Fore.GREEN + Style.BRIGHT} Selesai {Style.RESET_ALL}"
                                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                        f"{Fore.CYAN + Style.BRIGHT} Hadiah: {Style.RESET_ALL}"
                                        f"{Fore.WHITE + Style.BRIGHT}{reward} Permintaan{Style.RESET_ALL}"
                                    )
                                    any_claimable_missions_found = True # Set flag jika misi diproses
                            # Tidak ada else di sini, karena jika tidak memenuhi kondisi di atas,
                            # misi tidak perlu diklaim dan tidak mempengaruhi any_claimable_missions_found
                            # sampai misi yang *bisa* diklaim ditemukan.

                    if not any_claimable_missions_found:
                        self.print_message(email, Fore.GREEN, "Semua Misi yang Tersedia Telah Selesai (Tidak ada yang perlu diklaim saat ini)")
                else:
                    self.print_message(email, Fore.GREEN, "Tidak ada misi yang tersedia.")

            await asyncio.sleep(24 * 60 * 60) # Cek misi setiap 24 jam
        
    async def process_accounts(self, email: str): # Hapus parameter use_proxy, rotate_proxy
        triggered = await self.process_onchain_trigger(email) # Hapus parameter proxy
        if triggered:
            tasks = [
                asyncio.create_task(self.looping_auth_refresh(email)), # Hapus parameter proxy
                asyncio.create_task(self.process_model_response(email)), # Hapus parameter proxy
                asyncio.create_task(self.process_user_missions(email)) # Hapus parameter proxy
            ]
            await asyncio.gather(*tasks)
    
    async def main(self):
        try:
            tokens = self.load_accounts()
            if not tokens:
                self.log(f"{Fore.RED + Style.BRIGHT}Tidak Ada Akun yang Dimuat.{Style.RESET_ALL}")
                return
            
            # Memuat kunci Anti-Captcha
            if not self.ANTICAPTCHA_API_KEY:
                self.log(f"{Fore.RED + Style.BRIGHT}Kunci API Anti-Captcha tidak tersedia. Harap periksa file 'anticaptcha_key.txt'.{Style.RESET_ALL}")
                return

            use_proxy_choice, rotate_proxy = self.print_question() # Ini sekarang hanya akan menanyakan '1'

            # Variabel `use_proxy` tidak lagi digunakan secara fungsional untuk logika proxy,
            # tetapi kita menyimpannya di sini untuk menyederhanakan penghapusan parameter dalam fungsi lain.
            # use_proxy = False 
            # if use_proxy_choice == 1: # Karena hanya ada satu pilihan sekarang
            #     use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Total Akun: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )

            # Penghapusan pemuatan proxy manual
            # if use_proxy:
            #     await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*75)

            tasks = []
            for idx, token in enumerate(tokens, start=1):
                if token:
                    email = token["Email"]
                    access_token = token["accessToken"]
                    refresh_token = token["refreshToken"]

                    if not "@" in email or not access_token or not refresh_token:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Akun: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{idx}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Data Akun Tidak Valid {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                        continue

                    # Perbaikan: get_token_exp_time harus memeriksa token akses, bukan refresh token
                    # karena refresh token tidak memiliki 'exp' di payload JWT-nya
                    # Namun, jika refresh token yang Anda maksud juga JWT, maka biarkan saja.
                    # Asumsi: refresh_token juga JWT dengan 'exp'
                    exp_time = self.get_token_exp_time(refresh_token)
                    if exp_time is None or int(time.time()) > exp_time: # Tambahkan cek None
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Akun: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{idx}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Refresh Token Sudah Kadaluarsa atau Tidak Valid {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                        continue

                    self.access_tokens[email] = access_token
                    self.refresh_tokens[email] = refresh_token

                    tasks.append(asyncio.create_task(self.process_accounts(email))) # Hapus parameter proxy

            await asyncio.gather(*tasks)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = DDAI()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ KELUAR ] DDAI Network - BOT{Style.RESET_ALL}                                      ",
        )
