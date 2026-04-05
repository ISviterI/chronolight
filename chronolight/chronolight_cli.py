import typer
from .core import delay

app = typer.Typer()
tasks = {}

@app.command()
def add(name: str, delay_seconds: int):
    tasks[name] = f"Scheduled in {delay_seconds} seconds"
    delay(delay_seconds, lambda: print(f"Task {name} executed"))
    typer.echo(f"Task {name} added")

@app.command()
def list():
    if not tasks:
        typer.echo("No scheduled tasks")
    for name, status in tasks.items():
        typer.echo(f"{name}: {status}")

@app.command()
def remove(name: str):
    if name in tasks:
        tasks.pop(name)
        typer.echo(f"Task {name} removed")
    else:
        typer.echo(f"Task {name} not found")