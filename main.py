import typer
import os
import time
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv
from browser_manager import BrowserManager, AUTH_FILE

load_dotenv()

app = typer.Typer()
console = Console()

LOGIN_URLS = {
    "occ": "https://www.occ.com.mx/login"
}

CREDENTIALS = {
    "occ": {
        "email": os.getenv("OCC_EMAIL"),
        "password": os.getenv("OCC_PASSWORD"),
    }
}

def get_bot(platform: str, page):
    if platform.lower() == "occ":
        from occ_bot import OCCBot
        return OCCBot(page)
    else:
        raise ValueError(f"Plataforma '{platform}' no soportada actualmente.")

def _auto_login_occ(page, email: str, password: str) -> bool:
    try:
        page.wait_for_selector('input[type="email"], input[name="email"]', timeout=10000)
        page.fill('input[type="email"], input[name="email"]', email)
        page.fill('input[type="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_url(lambda url: "login" not in url, timeout=15000)
        return True
    except Exception as e:
        console.print(f"[red]Auto-login falló: {e}[/red]")
        return False

@app.command()
def login(platform: str = typer.Option("occ", "--platform", "-p", help="Plataforma para iniciar sesión")):
    """
    Inicia sesión. Si hay credenciales en .env lo hace automático, si no abre el navegador para login manual.
    """
    creds = CREDENTIALS.get(platform.lower(), {})
    email = creds.get("email")
    password = creds.get("password")
    auto = bool(email and password)

    console.print(f"[bold blue]Login en {platform.upper()} ({'automático' if auto else 'manual'})...[/bold blue]")

    bm = BrowserManager(headless=False)
    page = bm.start(use_auth=False)
    page.goto(LOGIN_URLS.get(platform.lower(), "https://google.com"))

    if auto:
        success = _auto_login_occ(page, email, password)
        if not success:
            console.print("[yellow]Auto-login falló. Completa el login manualmente y cierra el navegador.[/yellow]")

    if not auto or not success:
        console.print("[yellow]Inicia sesión manualmente. Cierra el navegador al terminar para guardar.[/yellow]")

    try:
        page.wait_for_event("close", timeout=600000)
    except Exception:
        pass

    bm.save_auth()
    bm.stop()
    console.print("[bold green]Sesión guardada exitosamente.[/bold green]")

@app.command()
def apply(
    query: str = typer.Option(..., "--search", "-s", help="Puesto a buscar"),
    location: str = typer.Option("", "--location", "-l", help="Ubicación"),
    platform: str = typer.Option("occ", "--platform", "-p", help="Plataforma a usar"),
    limit: int = typer.Option(10, "--limit", help="Límite de vacantes")
):
    """
    Busca y aplica automáticamente a vacantes.
    """
    if not os.path.exists(AUTH_FILE):
        console.print("[bold red]Error: No hay sesión. Ejecuta 'login' primero.[/bold red]")
        return

    bm = BrowserManager(headless=True)
    page = bm.start(use_auth=True)
    
    try:
        bot = get_bot(platform, page)
        bot.search_jobs(query, location)
        job_links = bot.get_job_links()
        
        stats = {"SUCCESS": 0, "SKIPPED_FORM": 0, "ALREADY_APPLIED": 0, "ERROR": 0}
        
        for i, link in enumerate(job_links):
            if i >= limit: break
            result = bot.apply_to_job(link)
            stats[result] = stats.get(result, 0) + 1
            import time, random
            time.sleep(random.uniform(3, 6))

    except Exception as e:
        console.print(f"[bold red]Fallo crítico: {e}[/bold red]")
        stats = {}
    finally:
        bm.stop()
    
    if stats:
        console.print("\n[bold blue]--- RESUMEN ---[/bold blue]")
        table = Table(show_header=True)
        table.add_column("Estado")
        table.add_column("Total", justify="right")
        for k, v in stats.items():
            table.add_row(k, str(v))
        console.print(table)

if __name__ == "__main__":
    app()
