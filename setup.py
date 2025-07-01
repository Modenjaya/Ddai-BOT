from curl_cffi import requests as cffi_requests # Beri alias untuk requests dari curl_cffi
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz

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
            
    def mask_account(self, account):
        if '@' in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"

    def print_question(self):
        print(f"{Fore.WHITE + Style.BRIGHT}1. Jalankan Tanpa Proxy (Anti-Captcha menanganinya secara internal){Style.RESET_ALL}")
        while True:
            try:
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Pilih [1] -> {Style.RESET_ALL}").strip())

                if choose == 1:
                    print(f"{Fore.GREEN + Style.BRIGHT}Pilihan Jalankan Tanpa Proxy Terpilih.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Harap masukkan 1.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Input tidak valid. Masukkan angka (1).{Style.RESET_ALL}")
    
    async def solve_cf_turnstile(self, email: str, retries=5):
        if not self.ANTICAPTCHA_API_KEY:
            self.log(f"{Fore.RED}Kunci API Anti-Captcha tidak dimuat. Tidak dapat menyelesaikan captcha.{Style.RESET_ALL}")
            return None

        solver = turnstileProxyless()
        solver.set_verbose(0)
        solver.set_key(self.ANTICAPTCHA_API_KEY)
        
        solver.set_website_url(self.PAGE_URL)
        solver.set_website_key(self.SITE_KEY)
        solver.set_soft_id(0)

        self.log(f"{Fore.YELLOW}Memulai penyelesaian Cloudflare Turnstile dengan Anti-Captcha...{Style.RESET_ALL}")
        
        g_response = solver.solve_and_return_solution() # Perbaikan di sini: solve_and_return_solution()

        if g_response != 0:
            self.log(f"{Fore.GREEN}Cloudflare Turnstile terpecahkan: {g_response}{Style.RESET_ALL}")
            self.captcha_tokens[email] = g_response
            return True
        else:
            self.log(f"{Fore.RED}Gagal menyelesaikan Cloudflare Turnstile: {solver.error_code}{Style.RESET_ALL}")
            return None

    async def auth_login(self, email: str, retries=5):
        url = f"{self.BASE_API}/login"
        data = json.dumps({"email":email, "password":self.password[email], "captchaToken":self.captcha_tokens[email]})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(cffi_requests.post, url=url, headers=headers, data=data, timeout=60, impersonate="chrome110", verify=False) # Perbaikan di sini: cffi_requests
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
        
    async def process_accounts(self, email: str):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}Proxy  :{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} Ditangani oleh Anti-Captcha {Style.RESET_ALL}"
        )

        self.log(f"{Fore.CYAN + Style.BRIGHT}Captcha:{Style.RESET_ALL}")

        cf_solved = await self.solve_cf_turnstile(email)
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
        
        login = await self.auth_login(email)
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
            
            if not self.ANTICAPTCHA_API_KEY:
                self.log(f"{Fore.RED + Style.BRIGHT}Kunci API Anti-Captcha tidak tersedia. Harap periksa file 'anticaptcha_key.txt'.{Style.RESET_ALL}")
                return

            use_proxy_choice = self.print_question()

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Total Akun: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

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

                    # Perbaikan di sini: Tambahkan pemeriksaan email dan password yang lebih ketat sebelum diproses
                    if not email or not "@" in email or not password:
                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                            f"{Fore.RED+Style.BRIGHT} Data Akun ({self.mask_account(email)}) Tidak Valid (Email atau Password kosong/salah format){Style.RESET_ALL}"
                        )
                        continue

                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}Akun:{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
                    )

                    self.password[email] = password

                    await self.process_accounts(email)
                    self.log(f"{Fore.YELLOW}Menunggu 60 detik sebelum memproses akun berikutnya...{Style.RESET_ALL}")
                    await asyncio.sleep(30)

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
            f"{Fore.RED + Style.BRIGHT}[ KELUAR ] DDAI Network - BOT{Style.RESET_ALL}                                      ",
        )
