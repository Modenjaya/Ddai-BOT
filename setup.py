from curl_cffi import requests
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz

# Impor klien API Anti-Captcha (Anda perlu menginstal ini: pip install anticaptchaofficial)
from anticaptchaofficial.turnstile import * # Menggunakan turnstile karena SITE_KEY yang diberikan

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
        self.PAGE_URL = "https://app.ddai.space"
        # SITE_KEY Anda (0x4AAAAAABdw7Ezbqw4v6Kr1) menunjukkan ini adalah Cloudflare Turnstile, bukan reCAPTCHA.
        self.SITE_KEY = "0x4AAAAAABdw7Ezbqw4v6Kr1" 
        self.ANTICAPTCHA_API_KEY = self.load_anticaptcha_key() # Muat kunci API Anti-Captcha
        # self.CAPTCHA_KEY = None # Tidak lagi diperlukan karena Anti-Captcha
        # Atribut proxy tidak lagi diperlukan karena Anti-Captcha menanganinya
        # self.proxies = []
        # self.proxy_index = 0
        # self.account_proxies = {}
        self.captcha_tokens = {}
        self.password = {}

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
        # Tolak untuk menghapus watermark
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Setup {Fore.BLUE + Style.BRIGHT}DDAI Network - BOT
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
        filename = "accounts.json"
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
            
    # Metode load_2captcha_key tidak lagi diperlukan
    # def load_2captcha_key(self):
    #     try:
    #         with open("2captcha_key.txt", 'r') as file:
    #             captcha_key = file.read().strip()
    #         return captcha_key
    #     except Exception as e:
    #         return None

    # Metode terkait proxy dihapus
    # async def load_proxies(self, use_proxy_choice: int):
    #     ...
    # def check_proxy_schemes(self, proxies):
    #     ...
    # def get_next_proxy_for_account(self, user_id):
    #     ...
    # def rotate_proxy_for_account(self, user_id):
    #     ...
            
    def mask_account(self, account):
        if '@' in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"

    def print_question(self):
        # Pilihan proxy disederhanakan karena Anti-Captcha menanganinya secara internal
        print(f"{Fore.WHITE + Style.BRIGHT}1. Jalankan Tanpa Proxy (Anti-Captcha menanganinya secara internal){Style.RESET_ALL}")
        while True:
            try:
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Pilih [1] -> {Style.RESET_ALL}").strip())

                if choose == 1:
                    print(f"{Fore.GREEN + Style.BRIGHT}Pilihan Jalankan Tanpa Proxy Terpilih.{Style.RESET_ALL}")
                    return choose # Mengembalikan 1
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Harap masukkan 1.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Input tidak valid. Masukkan angka (1).{Style.RESET_ALL}")
    
    async def solve_cf_turnstile(self, email: str, retries=5): # Parameter proxy dihapus
        if not self.ANTICAPTCHA_API_KEY:
            self.log(f"{Fore.RED}Kunci API Anti-Captcha tidak dimuat. Tidak dapat menyelesaikan captcha.{Style.RESET_ALL}")
            return None

        solver = CloudflareTurnstile() # Menggunakan CloudflareTurnstile
        solver.set_verbose(0)
        solver.set_key(self.ANTICAPTCHA_API_KEY)
        
        solver.set_website_url(self.PAGE_URL)
        solver.set_website_key(self.SITE_KEY)

        self.log(f"{Fore.YELLOW}Memulai penyelesaian Cloudflare Turnstile dengan Anti-Captcha...{Style.RESET_ALL}")
        
        # Penanganan proxy di sini dilakukan oleh pustaka Anti-Captcha secara internal
        # Jika Anda ingin menggunakan proxy kustom, Anda akan mengaturnya di sini
        # Contoh: solver.set_proxy_address("your_proxy_address")
        # solver.set_proxy_port(port)
        # solver.set_proxy_login(username)
        # solver.set_proxy_password(password)
        # solver.set_proxy_type("http") # atau "https", "socks4", "socks5"
        
        g_response = solver.solve_and_get_solution()

        if g_response != 0:
            self.log(f"{Fore.GREEN}Cloudflare Turnstile terpecahkan: {g_response}{Style.RESET_ALL}")
            self.captcha_tokens[email] = g_response
            return True
        else:
            self.log(f"{Fore.RED}Gagal menyelesaikan Cloudflare Turnstile: {solver.error_code}{Style.RESET_ALL}")
            return None

    async def auth_login(self, email: str, retries=5): # Parameter proxy dihapus
        url = f"{self.BASE_API}/login"
        data = json.dumps({"email":email, "password":self.password[email], "captchaToken":self.captcha_tokens[email]})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, timeout=60, impersonate="chrome110", verify=False) # Parameter proxy dihapus
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Login Gagal {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
        
    async def process_accounts(self, email: str): # Parameter use_proxy dihapus
        # Baris ini tidak lagi diperlukan karena proxy ditangani oleh Anti-Captcha
        # proxy = self.get_next_proxy_for_account(email) if use_proxy else None
        
        # Anda dapat menghapus baris log proxy ini atau mengubahnya untuk mencerminkan bahwa proxy ditangani oleh Anti-Captcha
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}Proxy  :{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} Ditangani oleh Anti-Captcha {Style.RESET_ALL}" # Mengubah pesan
        )

        self.log(f"{Fore.CYAN + Style.BRIGHT}Captcha:{Style.RESET_ALL}")

        cf_solved = await self.solve_cf_turnstile(email) # Parameter proxy dihapus
        if not cf_solved:
            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}    >{Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT} Status: {Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT}Tidak Terpecahkan{Style.RESET_ALL}"
            )
            return
            
        self.log(
            f"{Fore.MAGENTA + Style.BRIGHT}    >{Style.RESET_ALL}"
            f"{Fore.BLUE + Style.BRIGHT} Status: {Style.RESET_ALL}"
            f"{Fore.GREEN + Style.BRIGHT}Terpecahkan{Style.RESET_ALL}"
        )
        
        login = await self.auth_login(email) # Parameter proxy dihapus
        if login and login.get("status") == "success":
            access_token = login["data"]["accessToken"]
            refresh_token = login["data"]["refreshToken"]

            self.save_tokens([{"Email":email, "accessToken":access_token, "refreshToken":refresh_token}])

            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Status :{Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT} Token Berhasil Disimpan {Style.RESET_ALL}"
            )
        
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED + Style.BRIGHT}Tidak Ada Akun yang Dimuat.{Style.RESET_ALL}")
                return
            
            # Memuat kunci Anti-Captcha
            if not self.ANTICAPTCHA_API_KEY:
                self.log(f"{Fore.RED + Style.BRIGHT}Kunci API Anti-Captcha tidak tersedia. Harap periksa file 'anticaptcha_key.txt'.{Style.RESET_ALL}")
                return

            use_proxy_choice = self.print_question() # Ini sekarang hanya akan menanyakan '1'

            # Variabel `use_proxy` tidak lagi digunakan secara fungsional untuk logika proxy,
            # tetapi kita menyimpannya di sini untuk menyederhanakan penghapusan parameter dalam fungsi lain.
            # use_proxy = False 
            # if use_proxy_choice == 1: # Karena hanya ada satu pilihan sekarang
            #     use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Total Akun: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            # Penghapusan pemuatan proxy manual
            # if use_proxy:
            #     await self.load_proxies(use_proxy_choice)

            separator = "="*25
            for idx, account in enumerate(accounts, start=1):
                if account:
                    email = account["Email"]
                    password = account["Password"]
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}Dari{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {len(accounts)} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                    )

                    if not "@" in email or not password:
                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                            f"{Fore.RED+Style.BRIGHT} Data Akun Tidak Valid {Style.RESET_ALL}"
                        )
                        continue

                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}Akun:{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
                    )

                    self.password[email] = password

                    await self.process_accounts(email) # Parameter use_proxy dihapus
                    await asyncio.sleep(3)

            self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*68)

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
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] DDAI Network - BOT{Style.RESET_ALL}                                      ",
        )
