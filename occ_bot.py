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
        self.page.wait_for_timeout(3000)

    def get_job_links(self):
        cards = self.page.query_selector_all('[data-id]')
        jobs = []
        seen = set()
        for card in cards:
            job_id = card.get_attribute('data-id')
            if not job_id or not job_id.isdigit() or job_id in seen:
                continue
            seen.add(job_id)

            title_el = card.query_selector('[class*="title"], h2, h3, strong')
            title = title_el.inner_text().strip() if title_el else "Sin título"

            company_el = card.query_selector('a[href*="bolsa-de-trabajo"]')
            company = company_el.inner_text().strip() if company_el else "Empresa no visible"

            jobs.append({
                'url': f'https://www.occ.com.mx/empleo/oferta/{job_id}',
                'title': title,
                'company': company,
            })

        console.print(f"[blue]Vacantes encontradas: {len(jobs)}[/blue]")
        return jobs

    def apply_to_job(self, job):
        job_url = job['url']
        job_title = job.get('title', 'Sin título')
        company_name = job.get('company', 'Empresa no visible')
        try:
            console.print(f"\n[bold]Analizando: {job_title[:60]} ({company_name[:40]})[/bold]")

            context = self.page.context
            new_page = context.new_page()
            new_page.goto(job_url)
            new_page.wait_for_load_state("networkidle")
            new_page.wait_for_timeout(2000)

            apply_button = new_page.query_selector('button:has-text("Postularme")')

            if not apply_button:
                self._log_attempt(self.platform, job_title, company_name, "YA_POSTULADO", job_url)
                new_page.close()
                return "ALREADY_APPLIED"

            apply_button.click()
            time.sleep(random.uniform(2, 4))

            if "preguntas" in new_page.url.lower() or new_page.query_selector('form:has-text("pregunta")'):
                console.print(f"[orange1]OMITIDO: Requiere formulario adicional[/orange1]")
                self._log_attempt(self.platform, job_title, company_name, "OMITIDO_FORMULARIO", job_url)
                new_page.close()
                return "SKIPPED_FORM"

            self._log_attempt(self.platform, job_title, company_name, "EXITO", job_url)
            console.print(f"[green]EXITO: Postulado[/green]")
            new_page.close()
            return "SUCCESS"

        except Exception as e:
            console.print(f"[red]ERROR: {str(e)[:100]}[/red]")
            self._log_attempt(self.platform, job_title, company_name, "ERROR", job_url)
            return "ERROR"
