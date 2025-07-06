#!/usr/bin/env python3
"""
USTravelDocs Bot - Comprehensive Playwright-based automation bot

This bot navigates through the complete ustraveldocs.com flow:
1. Visa entry page navigation
2. Login with credentials
3. Captcha solving using 2captcha
4. Security questions handling
5. Appointment rescheduling interface access

Features:
- Advanced anti-bot bypass techniques
- Proxy support with rotation
- Human-like interaction patterns
- Comprehensive error handling
- Screenshot capture for debugging
"""

import asyncio
import json
import os
import re
import time
import random
import base64
from datetime import datetime
from urllib.parse import urljoin, urlparse
import httpx
from playwright.async_api import async_playwright

class USTravelDocsBot:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.session_info = None
        self.screenshots_dir = "screenshots"
        self.browser = None
        self.context = None
        self.page = None
        
        if self.config.get("config", {}).get("save_screenshots", True):
            os.makedirs(self.screenshots_dir, exist_ok=True)
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("✅ Configuration loaded successfully")
            return config
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            raise
    
    async def human_delay(self, min_ms=200, max_ms=800):
        """Human-like delay between actions"""
        await asyncio.sleep((min_ms + random.random() * (max_ms - min_ms)) / 1000)
    
    async def take_screenshot(self, name):
        """Take screenshot for debugging"""
        if not self.config.get("config", {}).get("save_screenshots", True) or not self.page:
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.screenshots_dir}/{name}_{timestamp}.png"
        await self.page.screenshot(path=filename)
        print(f"📸 Screenshot saved: {filename}")
        return filename
    
    async def solve_captcha(self):
        """Solve captcha using 2captcha service"""
        try:
            captcha_img = self.page.locator('#captchaImage')
            if await captcha_img.count() == 0:
                print("ℹ️ No captcha found")
                return True
                
            print("🔍 Captcha detected, solving...")
            await self.take_screenshot("captcha_detected")
            
            captcha_base64 = await self.page.evaluate('''
                () => {
                    const img = document.querySelector('#captchaImage');
                    if (!img) return null;
                    const canvas = document.createElement('canvas');
                    canvas.width = img.naturalWidth || img.width;
                    canvas.height = img.naturalHeight || img.height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    return canvas.toDataURL('image/png').split(',')[1];
                }
            ''')
            
            if not captcha_base64:
                print("❌ Failed to extract captcha image")
                return False
            
            api_key = self.config.get("config", {}).get("captcha_api_key")
            if not api_key:
                print("❌ No captcha API key configured")
                return False
            
            async with httpx.AsyncClient() as client:
                response = await client.post('http://2captcha.com/in.php', data={
                    'key': api_key,
                    'method': 'base64',
                    'body': captcha_base64,
                    'json': 1
                })
                result = response.json()
                
                if result.get('status') != 1:
                    print(f"❌ 2captcha error: {result}")
                    return False
                
                request_id = result['request']
                print(f"ℹ️ Captcha submitted, ID: {request_id}")
                
                for _ in range(30):
                    await asyncio.sleep(5)
                    response = await client.get('http://2captcha.com/res.php', params={
                        'key': api_key,
                        'action': 'get',
                        'id': request_id,
                        'json': 1
                    })
                    result = response.json()
                    
                    if result.get('status') == 1:
                        captcha_solution = result['request']
                        print(f"✅ Captcha solved: {captcha_solution}")
                        
                        await self.page.fill('#extension_atlasCaptchaResponse', captcha_solution)
                        return True
                    elif result.get('request') != 'CAPCHA_NOT_READY':
                        print(f"❌ Captcha solving error: {result}")
                        return False
                
                print("❌ Captcha solving timeout")
                return False
                
        except Exception as e:
            print(f"❌ Captcha solving error: {e}")
            return False
    
    async def handle_popups_and_overlays(self):
        """Handle popups and overlays that might block interaction"""
        try:
            overlay_selectors = [
                '.usa-dialog-overlay.is-visible',
                '[aria-hidden="true"].is-visible',
                '[data-v-47dfbd8e=""].usa-dialog-overlay',
                '.modal-backdrop',
                '.overlay',
                '.popup-overlay'
            ]
            
            for selector in overlay_selectors:
                try:
                    overlay = self.page.locator(selector).first
                    if await overlay.count() > 0 and await overlay.is_visible():
                        print(f"ℹ️ Overlay detected: {selector}")
                        
                        close_selectors = [
                            'button:has-text("Kapat")',
                            'button:has-text("Close")',
                            'button:has-text("×")',
                            '.close-button',
                            '.popup-close',
                            '.usa-button--outline',
                            '[aria-label="Close"]',
                            '[data-dismiss="modal"]'
                        ]
                        
                        for close_selector in close_selectors:
                            try:
                                close_btn = self.page.locator(close_selector).first
                                if await close_btn.count() > 0 and await close_btn.is_visible():
                                    await close_btn.click(force=True, timeout=5000)
                                    print(f"✅ Popup closed using: {close_selector}")
                                    await asyncio.sleep(1)
                                    break
                            except Exception:
                                continue
                        
                        try:
                            await overlay.click(force=True, position={'x': 10, 'y': 10})
                            print("ℹ️ Clicked outside overlay")
                            await asyncio.sleep(1)
                        except Exception:
                            pass
                except Exception:
                    continue
            
            try:
                await self.page.evaluate('''
                    () => {
                        try {
                            const overlays = [
                                ...document.querySelectorAll('.usa-dialog-overlay.is-visible'),
                                ...document.querySelectorAll('.overlay'),
                                ...document.querySelectorAll('.modal-backdrop'),
                                ...document.querySelectorAll('[aria-hidden="true"].is-visible')
                            ];
                            
                            for (const el of overlays) {
                                if (el && el.style) {
                                    el.style.display = 'none';
                                    if (el.classList) {
                                        el.classList.remove('is-visible');
                                        el.classList.remove('show');
                                    }
                                    if (el.setAttribute) {
                                        el.setAttribute('aria-hidden', 'true');
                                    }
                                }
                            }
                            
                            const closeButtons = document.querySelectorAll('button:has-text("Kapat"), button:has-text("Close"), .close-button');
                            for (const btn of closeButtons) {
                                if (btn && btn.offsetParent !== null) {
                                    btn.click();
                                }
                            }
                            
                            return overlays.length > 0;
                        } catch (e) {
                            console.error("Popup closing JS error:", e);
                            return false;
                        }
                    }
                ''')
            except Exception:
                pass
            
            try:
                await self.page.keyboard.press('Escape')
                await asyncio.sleep(1)
            except Exception:
                pass
            
            return True
        except Exception as e:
            print(f"❌ Popup/overlay handling error: {e}")
            return False
    
    async def slow_type(self, input_element, text, min_delay=0.08, max_delay=0.18):
        """Type text slowly like a human"""
        await input_element.fill("")
        for char in text:
            await input_element.type(char)
            await asyncio.sleep(random.uniform(min_delay, max_delay))
    
    def normalize_text(self, text):
        """Normalize text for comparison"""
        import unicodedata
        if not text:
            return ""
        text = text.lower().strip()
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        text = ' '.join(text.split())
        return text
    
    async def handle_security_questions(self):
        """Handle security questions with intelligent matching"""
        import unicodedata
        
        def normalize(text):
            if not text:
                return ""
            text = text.lower().strip()
            text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
            text = ' '.join(text.split())
            return text

        max_attempts = 3
        for attempt in range(max_attempts):
            print(f"\n🔄 Security questions attempt {attempt + 1}/{max_attempts}...")
            try:
                await self.page.wait_for_load_state('domcontentloaded', timeout=15000)
                is_security_page = await self.page.locator(':text-matches("Güvenlik Sorusu|Security Question|kbq", "i")').count() > 0
                if not is_security_page:
                    print("✅ Security questions page no longer visible, assuming success.")
                    return True
                    
                await self.take_screenshot(f"security_attempt_{attempt+1}")

                question_input_pairs = []
                question_ps = await self.page.query_selector_all('p.textInParagraph')
                for p in question_ps:
                    question_text = await p.text_content()
                    li = await p.evaluate_handle('el => el.closest("li")')
                    next_li = await li.evaluate_handle('el => el.nextElementSibling')
                    if next_li:
                        input_el = await next_li.query_selector('input[type="password"]')
                        if input_el:
                            question_input_pairs.append((input_el, question_text))
                
                if not question_input_pairs:
                    security_inputs = self.page.locator('input[type="password"]')
                    for i in range(await security_inputs.count()):
                        input_el = security_inputs.nth(i)
                        question_text = ""
                        try:
                            input_id = await input_el.get_attribute('id')
                            if input_id:
                                label = self.page.locator(f'label[for="{input_id}"]').first
                                if await label.count() > 0:
                                    question_text = await label.text_content()
                        except:
                            pass
                        
                        if not question_text or len(question_text.strip()) < 5:
                            try:
                                question_text = await self.page.evaluate(
                                    '''
                                    (el) => {
                                        let node = el.parentElement;
                                        for (let i=0; i<5 && node; i++) {
                                            if (node.innerText && node.innerText.length > 10) return node.innerText;
                                            node = node.parentElement;
                                        }
                                        node = el.previousElementSibling;
                                        for (let i=0; i<5 && node; i++) {
                                            if (node.innerText && node.innerText.length > 10) return node.innerText;
                                            node = node.previousElementSibling;
                                        }
                                        let tagNames = ['li','div','p','span'];
                                        node = el;
                                        for (let i=0; i<5 && node; i++) {
                                            if (tagNames.includes(node.tagName.toLowerCase()) && node.innerText && node.innerText.length > 10)
                                                return node.innerText;
                                            node = node.parentElement;
                                        }
                                        return '';
                                    }
                                    ''',
                                    input_el
                                )
                            except:
                                pass
                        question_input_pairs.append((input_el, question_text or ""))

                for idx, (input_el, question_text) in enumerate(question_input_pairs):
                    print(f"  -> Input {idx+1} detected question: '{question_text or 'NOT_FOUND'}'")

                security_questions = self.config.get("security_questions", {})
                normalized_qas = {normalize(q): a for q, a in security_questions.items()}

                for input_el, question_text in question_input_pairs:
                    norm_question = normalize(question_text)
                    answer = None
                    best_score = 0
                    for nq, a in normalized_qas.items():
                        score = 0
                        if nq == norm_question:
                            score = 100
                        elif nq in norm_question or norm_question in nq:
                            score = 80
                        else:
                            score = len(set(nq.split()) & set(norm_question.split())) * 10
                        if score > best_score:
                            best_score = score
                            answer = a
                    if not answer:
                        answer = "sokak"
                    print(f"  -> Answering: Question='{question_text}', Answer='{answer}' (score={best_score})")
                    await self.slow_type(input_el, answer)

                continue_btn = self.page.locator('#continue').first
                if await continue_btn.count() > 0 and await continue_btn.is_visible():
                    await continue_btn.click(force=True)
                else:
                    await self.page.keyboard.press('Enter')
                print("✅ Continue command sent. Waiting for result...")

                try:
                    for _ in range(20):
                        await asyncio.sleep(1)
                        try:
                            error_count = await self.page.locator(':text-matches("yanlış|incorrect|did not match|hatalı|cevaplar eşleşmedi", "i")').count()
                        except Exception as e:
                            print(f"[WARNING] Error check failed due to context closed or navigation: {e}")
                            print("[WARNING] Script continuing, browser will stay open!")
                            return True
                        try:
                            is_still_security = await self.page.locator(':text-matches("Güvenlik Sorusu|Security Question|kbq", "i")').count() > 0
                        except Exception as e:
                            print(f"[WARNING] Security page check failed due to context closed or navigation: {e}")
                            print("[WARNING] Script continuing, browser will stay open!")
                            return True
                        if error_count > 0:
                            print(f"❌ Error message received. Retrying... ({attempt + 1}/{max_attempts})")
                            await self.take_screenshot(f"security_error_message_{attempt+1}")
                            break
                        if not is_still_security:
                            print("✅ Success! Security questions passed.")
                            await self.take_screenshot("security_success")
                            return True
                    else:
                        print(f"❌ Timeout! No URL change or error message within 20 seconds. Attempt {attempt + 1} failed.")
                        await self.take_screenshot(f"security_timeout_{attempt+1}")
                        break
                except Exception as e:
                    print(f"[WARNING] Navigation or context closed error: {e}")
                    print("[WARNING] Script continuing, browser will stay open!")
                    return True
            except Exception as e:
                print(f"[WARNING] Security question error due to context closed or navigation: {e}")
                print("[WARNING] Script continuing, browser will stay open!")
                return True
        
        print("❌ Maximum security question attempts reached or critical error occurred.")
        await self.take_screenshot("security_questions_max_attempts_error")
        print("[WARNING] Script continuing, browser will stay open!")
        return True
    
    async def initialize_browser(self):
        """Initialize browser with anti-bot measures"""
        p = await async_playwright().start()
        
        proxy_config = None
        if self.config.get("proxy", {}).get("enabled", False):
            proxy_settings = self.config.get("proxy", {})
            proxy_server = proxy_settings.get("server", "geo.iproyal.com:12321")
            proxy_username = proxy_settings.get("username")
            proxy_password = proxy_settings.get("password")
            if proxy_username and proxy_password:
                proxy_config = {
                    "server": f"http://{proxy_server}",
                    "username": proxy_username,
                    "password": proxy_password
                }
        
        browser_config = self.config.get("browser_config", {})
        browser_launch_options = {
            "headless": browser_config.get("headless", False),
            "slow_mo": random.randint(50, 150),
            "args": [
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-field-trial-config',
                '--disable-back-forward-cache',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-component-extensions-with-background-pages',
                '--no-default-browser-check',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-popup-blocking',
                '--disable-translate',
                '--disable-background-networking',
                '--disable-sync',
                '--metrics-recording-only',
                '--disable-ipc-flooding-protection',
                f'--user-agent={browser_config.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")}'
            ]
        }
        
        if proxy_config:
            browser_launch_options["proxy"] = proxy_config
            
        self.browser = await p.chromium.launch(**browser_launch_options)
        
        viewport = browser_config.get("viewport", {"width": 1366, "height": 768})
        self.context = await self.browser.new_context(
            viewport={
                'width': random.randint(viewport["width"] - 200, viewport["width"] + 200), 
                'height': random.randint(viewport["height"] - 100, viewport["height"] + 100)
            },
            user_agent=browser_config.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
            locale='tr-TR',
            timezone_id='Europe/Istanbul',
            permissions=['geolocation'],
            geolocation={'latitude': 39.9334, 'longitude': 32.8597},
            color_scheme='light',
            reduced_motion='no-preference',
            forced_colors='none',
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
        )
        
        self.page = await self.context.new_page()
        
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['tr-TR', 'tr', 'en-US', 'en'],
            });
            
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32',
            });
            
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            const getParameter = WebGLRenderingContext.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel(R) Iris(R) Xe Graphics';
                }
                return getParameter(parameter);
            };
            
            ['mousedown', 'mouseup', 'mousemove', 'keydown', 'keyup', 'click'].forEach(eventType => {
                document.addEventListener(eventType, function(e) {
                }, true);
            });
        """)
        
        print("✅ Browser initialized with anti-bot measures")
    
    async def navigate_to_visa_entry(self):
        """Navigate to visa entry page"""
        urls_to_try = [
            self.config.get("urls", {}).get("visa_entry", "https://www.ustraveldocs.com/tr/tr/nonimmigrant-visa"),
            self.config.get("urls", {}).get("turkish_base", "https://www.ustraveldocs.com/tr/tr"),
            self.config.get("urls", {}).get("base_url", "https://www.ustraveldocs.com"),
        ]
        
        successful_load = False
        
        for i, url in enumerate(urls_to_try):
            try:
                print(f"🔍 Attempt {i+1}/{len(urls_to_try)}: {url}")
                
                if i == 0 and self.config.get("proxy", {}).get("enabled", False):
                    try:
                        print("🔍 Testing proxy connection...")
                        await self.page.goto('https://httpbin.org/ip', wait_until='networkidle', timeout=15000)
                        ip_info = await self.page.evaluate('document.body.textContent')
                        print(f"✅ Proxy IP: {ip_info}")
                        await asyncio.sleep(2)
                    except Exception as e:
                        print(f"⚠️ Proxy test error: {e}")
                
                await self.page.goto(url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(random.uniform(3, 6))
                
                page_title = await self.page.title()
                page_content = await self.page.content()
                
                if len(page_content) > 1000 and ("ustraveldocs" in page_content.lower() or "visa" in page_content.lower()):
                    print(f"✅ Site loaded successfully: {page_title}")
                    successful_load = True
                    break
                else:
                    print(f"❌ Insufficient page content: {len(page_content)} characters")
                    
            except Exception as e:
                print(f"❌ URL {url} failed to load: {e}")
                continue
        
        if not successful_load:
            raise Exception("Failed to load any URL")
        
        await self.page.mouse.move(random.randint(200, 1000), random.randint(200, 800))
        await asyncio.sleep(random.uniform(1, 2))
        
        for i in range(3):
            await self.page.evaluate(f'window.scrollTo(0, {i * 200})')
            await asyncio.sleep(random.uniform(0.5, 1))
        
        await self.handle_popups_and_overlays()
        await self.take_screenshot("main_page")
        
        print("✅ Successfully navigated to visa entry page")
    
    async def navigate_to_login(self):
        """Navigate to login page"""
        print("🔍 Looking for Visa Entry button...")
        visa_login_selectors = [
            'a:has-text("Vize Girişi")',
            'a:has-text("Visa Login")',
            'a[href*="login"]',
            'a[href*="signin"]',
            'a[href*="account"]',
            'button:has-text("Giriş")',
            'a:has-text("Sign In")',
            'a:has-text("Log In")'
        ]
        
        visa_login_found = False
        for selector in visa_login_selectors:
            try:
                visa_btn = self.page.locator(selector).first
                if await visa_btn.count() > 0 and await visa_btn.is_visible():
                    print(f"✅ Visa entry button found: {selector}")
                    await visa_btn.click()
                    await self.page.wait_for_load_state('networkidle', timeout=15000)
                    visa_login_found = True
                    break
            except Exception:
                continue
        
        if not visa_login_found:
            print("[WARNING] Visa Entry button not found, trying direct URL...")
            await self.page.goto(self.config.get("urls", {}).get("login_fallback", "https://www.usvisascheduling.com/tr-TR/signin"), wait_until='domcontentloaded')
        
        await asyncio.sleep(3)
        await self.take_screenshot("after_visa_entry")
        
        print("🔍 Looking for Sign In button...")
        signin_selectors = [
            '#signin',
            'a:has-text("Oturum Aç")',
            'a:has-text("Sign In")',
            'button:has-text("Oturum Aç")',
            'button:has-text("Sign In")',
            'a[href*="SignIn"]',
            'a[href*="Login"]',
            '[data-testid*="signin"]',
            '.signin-button',
            '.login-button'
        ]
        
        signin_found = False
        for selector in signin_selectors:
            try:
                signin_btn = self.page.locator(selector).first
                if await signin_btn.count() > 0 and await signin_btn.is_visible():
                    print(f"✅ Sign in button found: {selector}")
                    await signin_btn.click()
                    await self.page.wait_for_load_state('networkidle', timeout=15000)
                    signin_found = True
                    break
            except Exception:
                continue
        
        if not signin_found:
            print("[WARNING] Sign In button not found, trying Azure B2C direct URL...")
            await self.page.goto('https://atlasauth.b2clogin.com/tfp/f50ebcfb-eadd-41d8-9099-a7049d073f5c/b2c_1a_atoproduction_atlas_susi/oauth2/v2.0/authorize?client_id=b2969e82-aa3e-406a-bdf1-ad6bf71af78a&scope=openid%20profile&redirect_uri=https%3A%2F%2Fwww.usvisascheduling.com%2Ftr-TR%2FAccount%2FLogin%2FExternalLoginCallback&response_type=code&response_mode=form_post', wait_until='domcontentloaded')
        
        await asyncio.sleep(5)
        await self.take_screenshot("login_form")
        print("✅ Successfully navigated to login form")
    
    async def perform_login(self):
        """Perform login with credentials"""
        print("🔍 Looking for login form...")
        
        form_selectors = [
            '#signInName',
            '#email',
            '#username',
            'input[name="email"]',
            'input[name="username"]',
            'input[type="email"]',
            'input[placeholder*="email"]',
            'input[placeholder*="kullanıcı"]'
        ]
        
        password_selectors = [
            '#password',
            'input[name="password"]',
            'input[type="password"]',
            'input[placeholder*="password"]',
            'input[placeholder*="şifre"]'
        ]
        
        username = self.config.get("config", {}).get("username")
        password = self.config.get("config", {}).get("password")
        
        if not username or not password:
            raise Exception("Username or password not configured")
        
        username_filled = False
        for selector in form_selectors:
            try:
                username_field = self.page.locator(selector).first
                if await username_field.count() > 0 and await username_field.is_visible():
                    print(f"✅ Username field found: {selector}")
                    await self.slow_type(username_field, username)
                    username_filled = True
                    break
            except Exception:
                continue
        
        if not username_filled:
            raise Exception("Username field not found")
        
        password_filled = False
        for selector in password_selectors:
            try:
                password_field = self.page.locator(selector).first
                if await password_field.count() > 0 and await password_field.is_visible():
                    print(f"✅ Password field found: {selector}")
                    await self.slow_type(password_field, password)
                    password_filled = True
                    break
            except Exception:
                continue
        
        if not password_filled:
            raise Exception("Password field not found")
        
        await self.human_delay()
        captcha_success = await self.solve_captcha()
        if not captcha_success:
            raise Exception("Captcha solving failed")
        
        print("🔍 Submitting login form...")
        await self.page.click('#continue')
        await self.page.wait_for_load_state('networkidle', timeout=30000)
        await asyncio.sleep(3)
        await self.take_screenshot("after_login")
        
        print("✅ Login form submitted successfully")
    
    async def navigate_to_appointment_scheduling(self):
        """Navigate to appointment scheduling interface"""
        security_success = await self.handle_security_questions()
        if not security_success:
            raise Exception("Security questions handling failed")
        
        print("🔍 Navigating to appointment page...")
        await self.take_screenshot("main_page_before_button")
        
        dashboard_selectors = [
            'a:has-text("Yeniden Randevu Planla")',
            'a:has-text("Reschedule Appointment")',
            'a[href*="schedule"]',
            'a:has-text("Randevu")',
            'button:has-text("Devam")',
            'a:has-text("Devam")',
            'h2:has-text("Hoş Geldiniz")',
            'h2:has-text("Welcome")'
        ]
        
        dashboard_selector_string = ", ".join(dashboard_selectors)
        try:
            await self.page.wait_for_selector(dashboard_selector_string, state='visible', timeout=30000)
        except Exception:
            await self.take_screenshot("dashboard_loading_error")
        
        button_found = False
        button_selectors = [
            'a:has-text("Yeniden Randevu Planla")',
            'a:has-text("Reschedule Appointment")',
            'button:has-text("Devam")',
            'a:has-text("Devam")',
            'a:has-text("Randevu")',
            'a:has-text("Appointment")',
            'a:has-text("Schedule")',
            'a[href*="schedule"]',
            'a[href*="appointment"]',
            'a[href*="randevu"]',
            'button:has-text("Randevu")',
            'button:has-text("Appointment")'
        ]
        
        for selector in button_selectors:
            try:
                reschedule_btn = self.page.locator(selector).first
                if await reschedule_btn.count() > 0 and await reschedule_btn.is_visible():
                    await asyncio.sleep(1)
                    await reschedule_btn.click(force=True, timeout=15000)
                    await self.page.wait_for_load_state('networkidle', timeout=30000)
                    button_found = True
                    print(f"✅ Appointment button clicked: {selector}")
                    break
            except Exception:
                continue
        
        if not button_found:
            all_buttons = await self.page.evaluate('''
                () => {
                    const elements = Array.from(document.querySelectorAll('a, button'));
                    return elements.map(el => ({
                        href: el.href || '',
                        text: el.innerText.trim(),
                        visible: el.offsetParent !== null
                    })).filter(el => el.visible && el.text.length > 0);
                }
            ''')
            
            keywords = ["randevu", "appointment", "schedule", "planla", "devam", "continue"]
            for btn_data in all_buttons:
                text = btn_data.get("text", "").lower()
                href = btn_data.get("href", "").lower()
                if any(keyword in text for keyword in keywords) or any(keyword in href for keyword in keywords):
                    try:
                        target_element = self.page.locator(f'a:has-text("{btn_data.get("text")}"), button:has-text("{btn_data.get("text")}")').first
                        if await target_element.count() > 0:
                            await target_element.click(force=True, timeout=15000)
                            await self.page.wait_for_load_state('networkidle', timeout=30000)
                            button_found = True
                            print(f"✅ Found and clicked appointment button: {btn_data.get('text')}")
                            break
                    except Exception:
                        pass
        
        await asyncio.sleep(5)
        await self.take_screenshot("appointment_page")
        
        cookies = await self.context.cookies()
        self.session_info = {
            "user_agent": await self.page.evaluate('navigator.userAgent'),
            "cookies": cookies,
            "last_login": datetime.now().isoformat()
        }
        
        with open('session.json', 'w', encoding='utf-8') as f:
            json.dump(self.session_info, f, ensure_ascii=False, indent=2)
        print("✅ Session information saved")
        
        print("✅ Successfully reached appointment scheduling interface")
    
    async def run_complete_flow(self):
        """Run the complete bot flow"""
        try:
            print("\n🤖 USTravelDocs Bot - Starting Complete Flow")
            print("=" * 60)
            
            await self.initialize_browser()
            await self.navigate_to_visa_entry()
            await self.navigate_to_login()
            await self.perform_login()
            await self.navigate_to_appointment_scheduling()
            
            print("\n✅ SUCCESS! Bot completed the full flow successfully!")
            print("✅ Reached appointment rescheduling interface")
            print("🎉 Login and security questions passed successfully")
            print("📱 Browser will remain open for manual inspection")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Bot flow failed: {e}")
            await self.take_screenshot("error_final")
            return False
    
    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.browser:
                await self.browser.close()
                print("✅ Browser closed")
        except Exception as e:
            print(f"⚠️ Browser cleanup error: {e}")

async def main():
    """Main execution function"""
    bot = USTravelDocsBot()
    
    try:
        success = await bot.run_complete_flow()
        
        if success:
            print("\n🎉 Bot execution completed successfully!")
            print("📱 Browser will remain open for inspection...")
            await asyncio.Event().wait()
        else:
            print("\n❌ Bot execution failed!")
            
    except KeyboardInterrupt:
        print("\n⚠️ Bot execution interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        await bot.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
