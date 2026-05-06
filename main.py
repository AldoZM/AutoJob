import typer
import os
from rich.console import Console
from rich.table import Table
from browser_manager import BrowserManager, AUTH_FILE

app = typer.Typer()
console = Console()

def get_bot(platform: str, page):
    if platform.lower() == "occ":
        from occ_bot import OCCBot
        return OCCBot(page)
    # Aquí se añadirán más plataformas (Indeed, LinkedIn, etc.)
    else:
        raise ValueError(f"Plataforma '{platform}' no soportada actualmente.")

@app.command()
def login(platform: str = typer.Option("occ", "--platform", "-p", help="Plataforma para iniciar sesión")):
    """
    Abre el navegador para iniciar sesión manualmente.
    """
    console.print(f"[bold blue]Iniciando navegador para Login en {platform.upper()}...[/bold blue]")
    bm = BrowserManager(headless=False)
    page = bm.start(use_auth=False)
    
    urls = {
        "occ": "https://www.occ.com.mx/login"
    }
    
    page.goto(urls.get(platform.lower(), "https://google.com"))
    
    console.print("[yellow]Inicia sesión manualmente. Cierra el navegador al terminar para guardar.[/yellow]")
    
    try:
        page.wait_for_timeout(600000) 
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
