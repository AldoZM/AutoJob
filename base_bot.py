import os
import csv
from datetime import datetime
from abc import ABC, abstractmethod
from rich.console import Console

console = Console()
LOG_FILE = "postulaciones.csv"

class BaseBot(ABC):
    def __init__(self, page):
        self.page = page
        self._init_log()

    def _init_log(self):
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Fecha", "Plataforma", "Puesto", "Empresa", "Estado", "URL"])

    def _log_attempt(self, platform, title, company, status, url):
        with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), platform, title, company, status, url])

    @abstractmethod
    def search_jobs(self, query, location=""):
        pass

    @abstractmethod
    def get_job_links(self):
        pass

    @abstractmethod
    def apply_to_job(self, job_element):
        pass
