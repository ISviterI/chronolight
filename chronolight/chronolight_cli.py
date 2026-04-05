import subprocess
import typer
import time
import tqdm
from plyer import notification
from chronolight import delay
app = typer.Typer()


@app.command()
def execute(seconds: int, command: str, repeat: int = 1):
    """Execute a command after delay"""

    def run():
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

    typer.echo(f"Will execute '{command}' after {str(seconds)} seconds")

    if repeat > 1:
        remaining = repeat

        def schedule():
            nonlocal remaining
            if remaining <= 0:
                return
            delay(seconds, run)
            delay(seconds, schedule)
            remaining -= 1

        schedule()
    else:
        delay(seconds, run)

@app.command()
def timer(seconds:int, message:str="haha noob, time's upp!!!", notify:bool=True):
    """Timer with system notification"""
    typer.echo(f"Timer started for {seconds} seconds...")
    for remaining in range(seconds, 0, -1):
        typer.echo(f"\rTime remaining: {remaining} seconds", nl=False)
        time.sleep(1)

    typer.echo(f"\n{message}")

    if notify:
        notification.notify(
            title="Chronolight Timer",
            message=message,
            timeout=60
        )



@app.command()
def progress(seconds: int, message: str = "Progressing..."):
    """Progress bar with time limit"""
    with tqdm.tqdm(total=seconds, desc=message, unit="s") as pbar:
        for _ in range(seconds):
            time.sleep(1)
            pbar.update(1)

    typer.echo(f"Done after {seconds} seconds!")