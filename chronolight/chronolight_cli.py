import typer
import threading
from datetime import datetime, timedelta
from chronolight import delay

app = typer.Typer()
tasks = {}


@app.command()
def add(name: str, delay_seconds: int, repeat: int = 1):
    """Add a delayed task (optionally repeatable)"""

    def task():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Task {name} executed")

    def schedule(remaining):
        timer = threading.Timer(delay_seconds, task)
        timer.start()
        tasks[name] = {"timer": timer, "remaining": remaining - 1 if remaining > 1 else 0}

        if remaining > 1:
            timer2 = threading.Timer(delay_seconds, lambda: schedule(remaining - 1))
            timer2.start()

    schedule(repeat)
    typer.echo(f"Task {name} added (will run {repeat} time(s) every {delay_seconds}s)")


@app.command()
def list():
    """List all scheduled tasks"""
    if not tasks:
        typer.echo("No scheduled tasks")
        return

    for name, data in tasks.items():
        remaining = data.get("remaining", 0)
        status = f"will run {remaining} more time(s)" if remaining > 0 else "pending"
        typer.echo(f"{name}: {status}")


@app.command()
def remove(name: str):
    """Remove a scheduled task"""
    if name in tasks:
        tasks[name].get("timer").cancel()
        tasks.pop(name)
        typer.echo(f"Task {name} removed")
    else:
        typer.echo(f"Task {name} not found")


@app.command()
def clear():
    """Remove all tasks"""
    for name in list(tasks.keys()):
        tasks[name].get("timer").cancel()
        tasks.clear()
    typer.echo("All tasks cleared")


@app.command()
def run(seconds: int, message: str = "Time's up!"):
    """Simple timer with message"""
    typer.echo(f"Timer started for {seconds} seconds...")
    delay(seconds, lambda: print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}"))


@app.command()
def repeat(seconds: int, times: int, message: str = "Repeat!"):
    """Repeat a message every N seconds"""
    typer.echo(f"Will repeat '{message}' every {seconds} seconds, {times} times")

    def task():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    remaining = times

    def schedule():
        nonlocal remaining
        if remaining <= 0:
            return
        timer = threading.Timer(seconds, task)
        timer.start()
        timer2 = threading.Timer(seconds, schedule)
        timer2.start()
        remaining -= 1

    schedule()


@app.command()
def version():
    """Show version"""
    typer.echo("chronolight 1.2.4")