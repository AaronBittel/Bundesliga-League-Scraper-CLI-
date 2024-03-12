"""Handles request of Football table."""

from __future__ import annotations

from bundesliga_scraper.api import api
from bundesliga_scraper.data_printer import table_printer
from bundesliga_scraper.datatypes.constants import LEAGUE_NAMES, League
from bundesliga_scraper.datatypes.fixture_entry import FixtureEntry
from bundesliga_scraper.datatypes.table_entry import TableEntry

FIRST_ROUND_MATCHDAY = 17


def handle_table_request(args: dict[str, str | int]) -> None:
    """Handles the table request.

    Args:
        args (dict[str, str  |  int]): user arguments
    """

    league = (
        api.League.Bundesliga
        if args.league == "bundesliga"
        else api.League.Bundesliga_2
    )

    current_matchday = api.retrieve_current_matchday(league=league)
    if args.first_round:
        if current_matchday <= FIRST_ROUND_MATCHDAY:
            handle_table(league=league, matchday=-1, current_matchday=current_matchday)
        else:
            handle_first_round(league)
    elif args.second_round:
        if current_matchday <= FIRST_ROUND_MATCHDAY:
            handle_table(league=league, matchday=-1, current_matchday=current_matchday)
        else:
            handle_second_round(league, current_matchday)
    elif args.last:
        handle_table_last(league, args.last, current_matchday)
    else:
        matchday = args.matchday
        handle_table(
            league=league, matchday=matchday, current_matchday=current_matchday
        )


def standard_title(league: League, matchday: int) -> str:
    return f"{LEAGUE_NAMES[league]} Matchday {matchday}"


def handle_table(league: League, matchday: int, current_matchday: int) -> None:
    # -1 == get current one
    if matchday == -1:
        matchday = current_matchday

    # need to calculate the table for the given matchday by myself
    # get all fixtures -> calculate till matchday

    # TODO: Depending on League max matchday may be greater or less than 34
    if matchday < 1 or matchday > 34:
        raise ValueError(f"matchday must be between 1 and 34. You gave {matchday}.")

    all_fixtures = api.retrieve_all_fixtures(league=league)

    selected_fixtures = select_fixtures(all_fixtures=all_fixtures, to=matchday - 1)

    table_list_prior_matchday = calculate_table_entries(selected_fixtures)

    selected_fixtures = select_fixtures(all_fixtures=all_fixtures, to=matchday)
    table_list = calculate_table_entries(selected_fixtures)

    for pl, entry in enumerate(table_list):
        old_pl = index_of(entry=entry, table_list=table_list_prior_matchday)
        if pl == old_pl:
            continue
        elif pl > old_pl:
            entry.direction = -1
        else:
            entry.direction = 1

    table_printer.print_table_entries(
        title=standard_title(league=league, matchday=matchday), table_list=table_list
    )


def handle_table_last(league: League, n: int, current_matchday: int) -> None:
    from_matchday = current_matchday - n + 1
    if from_matchday < 1:
        from_matchday = 1

    all_fixtures = api.retrieve_all_fixtures(league=league)
    selected_fixtures = select_fixtures(
        all_fixtures=all_fixtures,
        from_=from_matchday,
        to=current_matchday,
        include_postponed_matches=True,
    )

    table_list = calculate_table_entries(selected_fixtures)
    table_printer.print_table_entries(
        title=f"{LEAGUE_NAMES[league]} Table Last {n} Matchdays",
        table_list=table_list,
    )


def initialize_empty_table_entries_dict(
    fixtures: list[FixtureEntry],
) -> dict[str, TableEntry]:
    table_entries = {}
    for fixture in fixtures[0:9]:
        table_entries[fixture.home_team] = TableEntry(team_name=fixture.home_team)
        table_entries[fixture.away_team] = TableEntry(team_name=fixture.away_team)
    return table_entries


def select_fixtures(
    all_fixtures: list[FixtureEntry],
    to: int,
    from_: int = 1,
    include_postponed_matches: bool = False,
) -> list[FixtureEntry]:
    selected_fixtures = []
    for fixture in all_fixtures:
        if fixture.matchday < from_:
            continue
        if fixture.matchday > to:
            if include_postponed_matches and len(selected_fixtures) != 9 * (
                to - from_ + 1
            ):
                continue
            break
        selected_fixtures.append(fixture)
    return selected_fixtures


def handle_first_round(league: League) -> None:
    all_fixtures = api.retrieve_all_fixtures(league=league)

    selected_fixtures = select_fixtures(
        all_fixtures=all_fixtures,
        to=FIRST_ROUND_MATCHDAY,
        include_postponed_matches=True,
    )

    table_list = calculate_table_entries(fixtures=selected_fixtures)

    table_printer.print_table_entries(
        title=f"{LEAGUE_NAMES[league]} First Round Table", table_list=table_list
    )


def handle_second_round(league: League, current_matchday: int) -> None:
    all_fixtures = api.retrieve_all_fixtures(league=league)

    selected_fixtures = select_fixtures(
        all_fixtures=all_fixtures,
        from_=FIRST_ROUND_MATCHDAY,
        to=current_matchday,
        include_postponed_matches=True,
    )

    table_list = calculate_table_entries(fixtures=selected_fixtures)

    table_printer.print_table_entries(
        title=f"{LEAGUE_NAMES[league]} Second Round Table", table_list=table_list
    )


def calculate_table_entries(fixtures: list[FixtureEntry]) -> list[TableEntry]:
    # TODO Somehow use Defaultdict
    table_entries = initialize_empty_table_entries_dict(fixtures)

    for fixture in fixtures:
        table_entries[fixture.home_team].update(fixture)
        table_entries[fixture.away_team].update(fixture)

    table_list = list(table_entries.values())
    return sorted(table_list, reverse=True)


def index_of(entry: TableEntry, table_list: list[TableEntry]) -> int:
    for i, table_entry in enumerate(table_list):
        if table_entry.team_name == entry.team_name:
            return i


def game_is_in_future(fixture: FixtureEntry, matchday: int) -> bool:
    return (
        fixture.matchday > matchday
        or not fixture.match_is_finished
        and not fixture.match_is_live
    )
