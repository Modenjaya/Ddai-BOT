from curl_cffi import requests
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, base64, time, json, os, pytz

# Import Anti-Captcha API client (you'll need to install this: pip install anticaptchaofficial)
from anticaptchaofficial.recaptchav2proxyless import *

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
        # Removed proxy-related attributes as Anti-Captcha handles them
        # self.proxies = []
        # self.proxy_index = 0
        # self.account_proxies = {}
        self.access_tokens = {}
        self.refresh_tokens = {}
        self.ANTICAPTCHA_API_KEY = self.load_anticaptcha_key() # Load API key

    def load_anticaptcha_key(self):
        """Loads Anti-Captcha API key from a file."""
        filename = "anticaptcha_key.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File '{filename}' not found. Please create it and put your Anti-Captcha API key inside.{Style.RESET_ALL}")
                return None
            with open(filename, 'r') as f:
                key = f.readline().strip()
                if not key:
                    self.log(f"{Fore.RED}Anti-Captcha API key not found in '{filename}'. Please ensure the file contains your key.{Style.RESET_ALL}")
                    return None
                return key
        except Exception as e:
            self.log(f"{Fore.RED}Failed to load Anti-Captcha API key: {e}{Style.RESET_ALL}")
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
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
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

    # Removed proxy loading and handling methods
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
    
    def print_message(self, account, color, message): # Removed proxy from print_message
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        # Simplified the proxy question as Anti-Captcha handles it
        print(f"{Fore.WHITE + Style.BRIGHT}1. Run Without Proxy (Anti-Captcha handles it internally){Style.RESET_ALL}")
        while True:
            try:
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1] -> {Style.RESET_ALL}").strip())

                if choose == 1:
                    print(f"{Fore.GREEN + Style.BRIGHT}Run Without Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter 1.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 1.{Style.RESET_ALL}")

        # Rotate proxy option is no longer relevant as Anti-Captcha handles proxies
        return choose, False

    async def solve_recaptcha_v2(self):
        """Solves reCAPTCHA v2 using Anti-Captcha."""
        if not self.ANTICAPTCHA_API_KEY:
            self.log(f"{Fore.RED}Anti-Captcha API key not loaded. Cannot solve captcha.{Style.RESET_ALL}")
            return None

        solver = recaptchaV2Proxyless()
        solver.set_verbose(0)
        solver.set_key(self.ANTICAPTCHA_API_KEY)
        
        # You need to find the sitekey and page_url for DDAI's reCAPTCHA
        # Example: sitekey = "YOUR_SITEKEY_HERE"
        # Example: page_url = "https://app.ddai.space"
        # You'll need to inspect the DDAI website to get these values.
        # For now, I'll use placeholders.
        sitekey = "6Lc_XXXX_XXXX-XXXX-XXXX-XXXXXXXXXXXX" # Placeholder: **REPLACE WITH ACTUAL SITEKEY**
        page_url = "https://app.ddai.space" # Likely correct, but verify

        solver.set_website_url(page_url)
        solver.set_website_key(sitekey)

        self.log(f"{Fore.YELLOW}Solving reCAPTCHA v2 with Anti-Captcha...{Style.RESET_ALL}")
        g_response = solver.solve_and_get_solution()

        if g_response != 0:
            self.log(f"{Fore.GREEN}reCAPTCHA solved: {g_response}{Style.RESET_ALL}")
            return g_response
        else:
            self.log(f"{Fore.RED}reCAPTCHA solving failed: {solver.error_code}{Style.RESET_ALL}")
            return None

    async def auth_login(self, email: str, password: str, g_recaptcha_response: str, retries=3):
        """
        Modified to include g_recaptcha_response for login if needed.
        This method is not in your original script but is often required when
        a login endpoint is protected by reCAPTCHA.
        """
        url = f"{self.BASE_API}/login" # Assuming a /login endpoint
        data = json.dumps({
            "email": email,
            "password": password,
            "gRecaptchaResponse": g_recaptcha_response
        })
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, timeout=60, impersonate="chrome110", verify=False)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                self.log(f"{Fore.YELLOW}Login attempt {attempt + 1}/{retries} failed: {e}{Style.RESET_ALL}")
                await asyncio.sleep(5)
        self.log(f"{Fore.RED}Login failed for {self.mask_account(email)} after {retries} attempts.{Style.RESET_ALL}")
        return None

    async def onchain_trigger(self, user_id: str, retries=5): # Removed proxy parameter
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
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, timeout=60, impersonate="chrome110", verify=False) # Removed proxy
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(user_id, Fore.YELLOW, f"Onchain Trigger Failed: {Fore.RED+Style.BRIGHT}{str(e)}") # Removed proxy

        return None

    async def auth_refresh(self, email: str, retries=5): # Removed proxy parameter
        url = f"{self.BASE_API}/refresh"
        data = json.dumps({"refreshToken":self.refresh_tokens[email]})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, timeout=60, impersonate="chrome110", verify=False) # Removed proxy
                if response.status_code == 401:
                    self.print_message(email, Fore.RED, "Refreshing Access Token Failed: " # Removed proxy
                        f"{Fore.YELLOW + Style.BRIGHT}Already Expired{Style.RESET_ALL}"
                    )
                    return None
                elif response.status_code == 403:
                    self.print_message(email, Fore.RED, "Refreshing Access Token Failed: " # Removed proxy
                        f"{Fore.YELLOW + Style.BRIGHT}Invalid, PLEASE DON'T LOGOUT or OPENED DDAI DASHBOARD WHILE BOT RUNNING{Style.RESET_ALL}"
                    )
                    return None
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, Fore.YELLOW, f"Refreshing Access Token Failed: {Fore.RED+Style.BRIGHT}{str(e)}") # Removed proxy

        return None
            
    async def model_response(self, email: str, retries=5): # Removed proxy and use_proxy, rotate_proxy parameters
        url = f"{self.BASE_API}/modelResponse"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, timeout=60, impersonate="chrome110", verify=False) # Removed proxy
                if response.status_code == 401:
                    await self.process_auth_refresh(email) # Removed proxy parameters
                    headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                    continue
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, Fore.YELLOW, f"GET Troughput Data Failed: {Fore.RED+Style.BRIGHT}{str(e)}") # Removed proxy

        return None
    
    async def mission_lists(self, email: str, retries=5): # Removed proxy and use_proxy, rotate_proxy parameters
        url = f"{self.BASE_API}/missions"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, timeout=60, impersonate="chrome110", verify=False) # Removed proxy
                if response.status_code == 401:
                    await self.process_auth_refresh(email) # Removed proxy parameters
                    headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                    continue
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, Fore.YELLOW, f"GET Mission Lists Failed: {Fore.RED+Style.BRIGHT}{str(e)}") # Removed proxy

        return None
    
    async def complete_missions(self, email: str, mission_id: str, title: str, retries=5): # Removed proxy and use_proxy, rotate_proxy parameters
        url = f"{self.BASE_API}/missions/claim/{mission_id}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}",
            "Content-Length":"0"
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, timeout=60, impersonate="chrome110", verify=False) # Removed proxy
                if response.status_code == 401:
                    await self.process_auth_refresh(email) # Removed proxy parameters
                    headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                    continue
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, Fore.WHITE, f"Mission {title}" # Removed proxy
                    f"{Fore.RED + Style.BRIGHT} Not Completed: {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None

    async def process_auth_refresh(self, email: str): # Removed use_proxy, rotate_proxy parameters
        while True:
            # Proxy handling is removed here as Anti-Captcha handles it
            refresh = await self.auth_refresh(email) # Removed proxy parameter
            if refresh:
                self.access_tokens[email] = refresh["data"]["accessToken"]

                self.save_tokens([{"Email":email, "accessToken":self.access_tokens[email], "refreshToken":self.refresh_tokens[email]}])
                self.print_message(email, Fore.GREEN, "Refreshing Access Token Success") # Removed proxy
                return True
            
            # Removed rotate_proxy logic
            await asyncio.sleep(5)
            continue
        
    async def check_token_exp_time(self, email: str): # Removed use_proxy, rotate_proxy parameters
        exp_time = self.get_token_exp_time(self.access_tokens[email])

        if int(time.time()) > exp_time:
            # Proxy handling is removed here as Anti-Captcha handles it
            self.print_message(email, Fore.YELLOW, "Access Token Expired, Refreshing...") # Removed proxy
            await self.process_auth_refresh(email) # Removed proxy parameters

        return True

    async def looping_auth_refresh(self, email: str): # Removed use_proxy, rotate_proxy parameters
        while True:
            await asyncio.sleep(10 * 60)
            await self.process_auth_refresh(email) # Removed proxy parameters

    async def process_onchain_trigger(self, email: str): # Removed use_proxy, rotate_proxy parameters
        is_valid = await self.check_token_exp_time(email) # Removed proxy parameters
        if is_valid:
            while True:
                # Proxy handling is removed here as Anti-Captcha handles it
                model = await self.onchain_trigger(email) # Removed proxy parameter
                if model:
                    req_total = model.get("data", {}).get("requestsTotal", 0)
                    self.print_message(email, Fore.GREEN, "Onchain Triggered Successfully " # Removed proxy
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Total Requests: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{req_total}{Style.RESET_ALL}"
                    )
                    return True
                
                # Removed rotate_proxy logic
                await asyncio.sleep(5)
                continue
        
    async def process_model_response(self, email: str): # Removed use_proxy, rotate_proxy parameters
        while True:
            # Proxy handling is removed here as Anti-Captcha handles it
            model = await self.model_response(email) # Removed proxy parameters
            if model:
                throughput = model.get("data", {}).get("throughput", 0)
                formatted_throughput = self.biner_to_desimal(throughput)

                self.print_message(email, Fore.GREEN, "Throughput " # Removed proxy
                    f"{Fore.WHITE + Style.BRIGHT}{formatted_throughput}%{Style.RESET_ALL}"
                )

            await asyncio.sleep(60)

    async def process_user_missions(self, email: str): # Removed use_proxy, rotate_proxy parameters
        while True:
            # Proxy handling is removed here as Anti-Captcha handles it
            mission_lists = await self.mission_lists(email) # Removed proxy parameters
            if mission_lists:
                missions = mission_lists.get("data", {}).get("missions", [])

                if missions:
                    completed = False

                    for mission in missions:
                        if mission:
                            mission_id = mission.get("_id")
                            title = mission.get("title")
                            reward = mission.get("rewards", {}).get("requests", 0)
                            type = mission.get("type")
                            status = mission.get("status")

                            if type == 3:
                                if status == "COMPLETED":
                                    claim = await self.complete_missions(email, mission_id, title) # Removed proxy parameters
                                    if claim and claim.get("data", {}).get("claimed"):
                                        self.print_message(email, Fore.WHITE, f"Mission {title}" # Removed proxy
                                            f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                            f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT}{reward} Requests{Style.RESET_ALL}"
                                        )
                            else:
                                if status == "PENDING":
                                    claim = await self.complete_missions(email, mission_id, title) # Removed proxy parameters
                                    if claim and claim.get("data", {}).get("claimed"):
                                        self.print_message(email, Fore.WHITE, f"Mission {title}" # Removed proxy
                                            f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                            f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT}{reward} Requests{Style.RESET_ALL}"
                                        )
                            else:
                                completed = True

                    if completed:
                        self.print_message(email, Fore.GREEN, "All Available Mission Is Completed") # Removed proxy

            await asyncio.sleep(24 * 60 * 60)
        
    async def process_accounts(self, email: str): # Removed use_proxy, rotate_proxy parameters
        triggered = await self.process_onchain_trigger(email) # Removed proxy parameters
        if triggered:
            tasks = [
                asyncio.create_task(self.looping_auth_refresh(email)), # Removed proxy parameters
                asyncio.create_task(self.process_model_response(email)), # Removed proxy parameters
                asyncio.create_task(self.process_user_missions(email)) # Removed proxy parameters
            ]
            await asyncio.gather(*tasks)
    
    async def main(self):
        try:
            tokens = self.load_accounts()
            if not tokens:
                self.log(f"{Fore.RED + Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return
            
            # Removed proxy choice as Anti-Captcha handles it
            use_proxy_choice, rotate_proxy = self.print_question() # This now only asks for '1'

            # The `use_proxy` variable is no longer functionally used for proxy logic,
            # but we keep it here to simplify parameter removal in other functions.
            use_proxy = False 

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )

            # Removed proxy loading
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
                            f"{Fore.CYAN + Style.BRIGHT}[ Account: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{idx}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Invalid Account Data {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                        continue

                    exp_time = self.get_token_exp_time(refresh_token)
                    if int(time.time()) > exp_time:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{idx}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Refresh Token Already Expired {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                        continue

                    self.access_tokens[email] = access_token
                    self.refresh_tokens[email] = refresh_token

                    tasks.append(asyncio.create_task(self.process_accounts(email))) # Removed proxy parameters

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
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] DDAI Network - BOT{Style.RESET_ALL}                                      ",
        )
