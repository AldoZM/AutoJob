import os
import json
from playwright.sync_api import sync_playwright

AUTH_FILE = "auth_state.json"

class BrowserManager:
    def __init__(self, headless=True):
        self.headless = headless
        self.pw = None
        self.browser = None
        self.context = None

    def start(self, use_auth=True):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=self.headless)
        
        ctx_args = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "viewport": {"width": 1280, "height": 800},
        }
        if use_auth and os.path.exists(AUTH_FILE):
            ctx_args["storage_state"] = AUTH_FILE
        self.context = self.browser.new_context(**ctx_args)
        
        return self.context.new_page()

    def save_auth(self):
        if self.context:
            self.context.storage_state(path=AUTH_FILE)

    def stop(self):
        if self.browser:
            self.browser.close()
        if self.pw:
            self.pw.stop()
