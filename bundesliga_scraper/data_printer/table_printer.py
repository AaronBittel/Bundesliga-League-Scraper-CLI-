"""Creating colorful strings of matchday table information."""

from rich.box import ROUNDED
from rich.console import Console
from rich.table import Table
from rich.style import Style

from bundesliga_scraper.api.api import League
from bundesliga_scraper.datatypes.table_entry import TableEntry

HEADER_STYLE = Style(bold=False)
DEFAULT_COLUMN_SETTINGS = {"justify": "center", "header_style": Style(bold=False)}
LEAGUE_NAMES = {League.Bundesliga: "Bundesliga", League.Bundesliga_2: "2. Bundesliga"}


def print_table_entries(
    league: League, matchday: int, table_entries: list[TableEntry]
) -> None:
    print()
    table = create_table(league, matchday)
    add_rows(table, table_entries)

    console = Console()
    console.print(table)


def create_table(league: League, matchday: int) -> None:
    table = Table(title=f"{LEAGUE_NAMES[league]} Matchday {matchday}", box=ROUNDED)

    table.add_column("#", style="bold", header_style=HEADER_STYLE)
    table.add_column("Team", header_style=HEADER_STYLE)
    table.add_column("Matches", **DEFAULT_COLUMN_SETTINGS)
    table.add_column("W", **DEFAULT_COLUMN_SETTINGS)
    table.add_column("D", **DEFAULT_COLUMN_SETTINGS)
    table.add_column("L", **DEFAULT_COLUMN_SETTINGS)
    table.add_column("Goals", **DEFAULT_COLUMN_SETTINGS)
    table.add_column("+/-", **DEFAULT_COLUMN_SETTINGS)
    table.add_column("Points", **DEFAULT_COLUMN_SETTINGS)

    return table


def add_rows(table: Table, table_entries: list[TableEntry]) -> None:
    for placement, entry in enumerate(table_entries, start=1):
        goal_diff = determine_goal_diff_color(entry.goal_diff)
        table.add_row(
            str(placement),
            str(entry.team_name),
            str(entry.matches),
            str(entry.won),
            str(entry.draw),
            str(entry.lost),
            f"{entry.goals}:{entry.opponent_goals}",
            goal_diff,
            str(entry.points),
        )


def determine_goal_diff_color(goal_diff: int) -> str:
    if goal_diff < 0:
        colored_goal_diff = str(f"[red]{goal_diff}")
    elif goal_diff > 0:
        colored_goal_diff = str(f"[green]{goal_diff}")
    else:
        colored_goal_diff = str(f"[white]{goal_diff}")
    return colored_goal_diff
