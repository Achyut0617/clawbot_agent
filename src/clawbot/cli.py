import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .audio import VoiceInput, VoiceUnavailable, speak
from .config import get_settings
from .runtime import AgentRuntime

app = typer.Typer(help="ClawBot — voice and text agent with OpenClaw orchestration.")
console = Console()


@app.command()
def doctor():
    """Check local prerequisites without executing any tasks."""
    settings = get_settings()
    runtime = AgentRuntime(settings)
    console.print(Panel.fit("[bold]ClawBot diagnostics[/bold]"))
    console.print(f"OpenClaw CLI: {'[green]found[/green]' if runtime.orchestrator.available() else '[yellow]not found[/yellow]'}")
    console.print(f"Microphone: {'[green]available[/green]' if VoiceInput.microphone_available() else '[yellow]unavailable (text mode works)[/yellow]'}")
    console.print(f"Database: {settings.db_path}")
    console.print(f"Approval required: {settings.require_approval}")


@app.command()
def setup():
    """Print platform-aware setup instructions."""
    import platform
    system = platform.system()
    console.print(f"Detected platform: [bold]{system}[/bold]")
    console.print("1. Install Python 3.11+ and create a virtual environment.")
    console.print("2. Install ClawBot: [cyan]pip install -e '.[dev,voice]'[/cyan]")
    if system == "Windows":
        console.print("3. Install OpenClaw using PowerShell:")
        console.print("   [cyan]iwr -useb https://openclaw.ai/install.ps1 | iex[/cyan]")
    else:
        console.print("3. Install OpenClaw:")
        console.print("   [cyan]curl -fsSL https://openclaw.ai/install.sh | bash[/cyan]")
    console.print("4. Run [cyan]openclaw onboard[/cyan], then [cyan]openclaw gateway status[/cyan].")
    console.print("5. Run [cyan]clawbot doctor[/cyan], then [cyan]clawbot chat[/cyan].")


@app.command()
def chat():
    """Start an interactive text-first loop; voice is an optional command."""
    settings = get_settings()
    runtime = AgentRuntime(settings)
    voice = VoiceInput(settings.vosk_model_path)
    console.print(Panel.fit("[bold cyan]ClawBot Agent[/bold cyan]\n"
                            "Text is always available. Commands: /voice /history /help /quit"))
    if not runtime.orchestrator.available():
        console.print("[yellow]OpenClaw CLI not detected. Install it before sending tasks.[/yellow]")
    pending_text = None
    while True:
        try:
            text = console.input("\n[bold green]You[/bold green] > ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\nGoodbye.")
            break
        if not text:
            continue
        command = text.lower()
        if command in {"/quit", "/exit"}:
            break
        if command == "/cancel":
            pending_text = None
            console.print("[yellow]Pending approval cleared.[/yellow]")
            continue
        if command == "/approve":
            if not pending_text:
                console.print("[yellow]There is no pending task to approve.[/yellow]")
                continue
            approved_text = pending_text
            pending_text = None
            task_id, result = runtime.submit(approved_text, source="text", approved=True)
            console.print(Panel(result, title=f"Task {task_id[:8]}"))
            speak(result, settings.tts_enabled)
            continue
        if command == "/help":
            console.print("/voice — capture one voice command\n/history — recent tasks\n/quit — exit")
            continue
        if command == "/history":
            table = Table("Task", "Status", "Input")
            for item in runtime.store.recent():
                table.add_row(item["task_id"][:8], item["status"], item["text"][:70])
            console.print(table)
            continue
        if command == "/voice":
            if not settings.voice_enabled:
                console.print("[yellow]Voice disabled in settings; type commands instead.[/yellow]")
                continue
            try:
                console.print("[cyan]Listening for up to 6 seconds...[/cyan]")
                text = voice.listen_once()
                if not text:
                    console.print("[yellow]No speech recognized.[/yellow]")
                    continue
                console.print(f"[bold]Recognized:[/bold] {text}")
            except VoiceUnavailable as exc:
                console.print(f"[yellow]{exc}[/yellow]")
                console.print("Continue in text mode.")
                continue
        task_id, result = runtime.submit(text, source="voice" if command == "/voice" else "text")
        if result == "APPROVAL_REQUIRED":
            console.print(Panel(f"Task: {task_id}\n{text}\n\n"
                                "This task requires explicit approval. Send it again prefixed with /approve "
                                "after reviewing the requested action."))
            # The user must explicitly resubmit the exact text with /approve.
            continue
        console.print(Panel(result, title=f"Task {task_id[:8]}"))
        speak(result, settings.tts_enabled)


@app.command()
def run(text: str = typer.Argument(..., help="Task to send to OpenClaw"),
        approve: bool = typer.Option(False, "--approve", help="Approve this task for orchestration")):
    """Submit one task."""
    settings = get_settings()
    task_id, result = AgentRuntime(settings).submit(text, approved=approve)
    console.print(Panel(result, title=f"Task {task_id}"))
    if result == "APPROVAL_REQUIRED":
        raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
