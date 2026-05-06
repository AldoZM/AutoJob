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
        
        if use_auth and os.path.exists(AUTH_FILE):
            self.context = self.browser.new_context(storage_state=AUTH_FILE)
        else:
            self.context = self.browser.new_context()
        
        return self.context.new_page()

    def save_auth(self):
        if self.context:
            self.context.storage_state(path=AUTH_FILE)

    def stop(self):
        if self.browser:
            self.browser.close()
        if self.pw:
            self.pw.stop()
