import random
import time
from base_bot import BaseBot, console

class OCCBot(BaseBot):
    def __init__(self, page):
        super().__init__(page)
        self.platform = "OCC"

    def search_jobs(self, query, location=""):
        search_url = f"https://www.occ.com.mx/empleos/trabajo-en-{query.replace(' ', '-')}/"
        if location:
            search_url += f"en-{location.replace(' ', '-')}/"
        
        console.print(f"[blue]Buscando en {self.platform}: {query} en {location if location else 'Todo México'}...[/blue]")
        self.page.goto(search_url)
        self.page.wait_for_load_state("networkidle")

    def get_job_links(self):
        return self.page.query_selector_all('a[class*="job-card"]')

    def apply_to_job(self, job_element):
        try:
            job_title = job_element.inner_text().split('\n')[0]
            company_element = job_element.query_selector('span[class*="company"]')
            company_name = company_element.inner_text() if company_element else "Empresa no visible"
            href = job_element.get_attribute("href")
            full_url = f"https://www.occ.com.mx{href}" if href.startswith('/') else href
            
            console.print(f"\n[bold]Analizando: {job_title} ({company_name})[/bold]")
            
            context = self.page.context
            new_page = context.new_page()
            new_page.goto(full_url)
            new_page.wait_for_load_state("networkidle")
            
            apply_button = new_page.query_selector('button:has-text("Postularme")')
            
            if not apply_button:
                self._log_attempt(self.platform, job_title, company_name, "YA_POSTULADO", full_url)
                new_page.close()
                return "ALREADY_APPLIED"

            apply_button.click()
            time.sleep(random.uniform(2, 4))
            
            if "preguntas" in new_page.url.lower() or new_page.query_selector('form:has-text("pregunta")'):
                console.print(f"[orange1]⚠️ OMITIDO: Requiere formulario adicional[/orange1]")
                self._log_attempt(self.platform, job_title, company_name, "OMITIDO_FORMULARIO", full_url)
                new_page.close()
                return "SKIPPED_FORM"
            
            self._log_attempt(self.platform, job_title, company_name, "EXITO", full_url)
            console.print(f"[green]✅ ÉXITO: Postulado[/green]")
            new_page.close()
            return "SUCCESS"

        except Exception as e:
            console.print(f"[red]❌ ERROR: {str(e)}[/red]")
            return "ERROR"
