from rich.console import Console
from rich.table import Table

help_table = [
    (
        "-m, --method [cyan]METHOD",
        "Request method, such as [bold]GET[/bold], [bold]POST[/bold], [bold]PUT[/bold], "
        "[bold]PATCH[/bold], [bold]DELETE[/bold], [bold]OPTIONS[/bold], [bold]HEAD[/bold]. "
        "[Default: [bold]GET[/bold]]",
    ),
    (
        "-p, --params [cyan]<NAME VALUE> ...",
        "Query parameters to include in the request URL.",
    ),
    ("-c, --content [cyan]TEXT", "Byte content to include in the request body."),
    ("-d, --data [cyan]<NAME VALUE> ...", "Form data to include in the request body."),
    (
        "-f, --files [cyan]<NAME FILENAME> ...",
        "Form files to include in the request body.",
    ),
    ("-j, --json [cyan]TEXT", "JSON data to include in the request body."),
    (
        "-h, --headers [cyan]<NAME VALUE> ...",
        "Include additional HTTP headers in the request.",
    ),
    ("--cookies [cyan]<NAME VALUE> ...", "Cookies to include in the request."),
    (
        "-a, --auth [cyan]<USER PASS>",
        "Username and password to include in the request. Specify '-' for the password to use "
        "a password prompt. Note that using --verbose/-v will expose the Authorization "
        "header, including the password encoding in a trivially reverisible format.",
    ),
    (
        "--proxy [cyan]URL",
        "Send the request via a proxy. Should be the URL giving the proxy address.",
    ),
    (
        "-t, --timeout [cyan]FLOAT",
        "Timeout value to use for network operations, such as establishing the connection, "
        "reading some data, etc... [Default: [bold]5.0[/bold]]",
    ),
    ("--no-allow-redirects", "Don't automatically follow redirects."),
    ("--no-verify", "Disable SSL verification."),
    ("--http2", "Send the request using HTTP/2, if the remote server supports it."),
    ("--download", "Save the response content as a file, rather than displaying it."),
    ("-v, --verbose", "Verbose output. Show request as well as response."),
    ("--help", "Show this message and exit."),
]


def print_help() -> None:
    console = Console()

    console.print("[bold]HTTPX :butterfly:", justify="center")
    console.print()
    console.print("A next generation HTTP client.", justify="center")
    console.print()

    table = Table.grid(padding=1, pad_edge=True)
    table.add_column("Parameter", no_wrap=True, justify="left", style="bold")
    table.add_column("Description")
    for parameter, description in help_table:
        table.add_row(parameter, description)

    console.print(table)
