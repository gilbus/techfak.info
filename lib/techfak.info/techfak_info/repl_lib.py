#!/usr/bin/env python3
"""
This script offers an interactive shell to enter details about any news that
shall be shown on the page itself
"""

import readline
from datetime import datetime
from enum import Enum
from typing import List, Union, Dict, Optional, TypeVar
from textwrap import TextWrapper

from colorama import Fore, Style
from dateutil.parser import parse as date_parse

from .Entry import Entry, Severity, State

__author__ = "tl"
__license__ = "AGPLv3"

T = TypeVar("T")

# max width of lines printed by this file to make it even accessible from a smartphone
# ssh session; worst case scenario for our infra
print_width = 80

# number of archived entries which can be selected directly by their index
no_of_archived_entries_to_show = 20


class InputAction(Enum):
    """
    Enum class to abstract from simple strings and get some type safety
    """
    yes = "y"
    no = "n"
    add = "a"
    edit = "e"
    move = "m"

    def __str__(self) -> str:
        return self.value


def print_with_max_width(
    text: str = "", text_wrapper=TextWrapper(width=print_width)
) -> None:
    # only print something if any text has been passed
    if not text:
        print()
    else:
        print("\n".join(text_wrapper.wrap(text)))


def get_entry(existing: Optional[Entry] = None, as_template=False) -> Entry:
    """
    This functions reads the user input for every field of an entry and
    returns a dictionary containing the values.
    :param existing: If empty a new record is requested, if not an existing one
    is modified.
    :param as_template: Treat the existing entry as a template, e.g. use new modified
    values but keep everything else
    :return: Record containing the data input of the user.
    """
    if existing:
        if as_template:
            entry_to_edit = Entry(template=existing)
        else:
            entry_to_edit = existing
    else:
        entry_to_edit = Entry()

    entry_to_edit.title = _get_title(entry_to_edit.title)
    entry_to_edit.summary = _get_summary(entry_to_edit.summary)
    entry_to_edit.html = _get_content_html(entry_to_edit.html)
    entry_to_edit.severity = _get_severity(entry_to_edit.severity)
    entry_to_edit.begin = _get_begin(entry_to_edit.begin)
    entry_to_edit.eta = _get_eta(entry_to_edit.eta)
    entry_to_edit.state = _get_state(entry_to_edit.state)

    return entry_to_edit


def repl_menu(entries: List[Entry]) -> str:
    """
    Offers possible actions for the available data which are printed beforehand.
    Either add a new entry, edit or remove an existing one. Returns the string to pass to the
    techfak_info api.
    :return:
    """
    choices = [InputAction.add.value, InputAction.edit.value, InputAction.move.value]
    print_with_max_width(
        """If any changes to entries are made new static html pages will be generated
        afterwards (if called via `status edit`). Contact tl@techfak for any questions.
        Exit the program at any time via Ctrl+c in which case no changes will be saved.
        """
    )
    print_with_max_width()
    # sort entries by date since this is the same order as used on the website
    entries.sort(key=lambda e: e.date_modified, reverse=True)
    # separate active from archived entries
    archive_entries = [entry for entry in entries if entry.state is State.archive]
    non_archive_entries = [
        entry for entry in entries if entry.state is not State.archive
    ]

    print_with_max_width("Current non-archive entries:")
    print_with_index(non_archive_entries)
    print()
    print_with_max_width("Recently archived entries:")
    print_with_index(archive_entries[:5])
    print()
    # ask what the user wants to do
    action = InputAction(
        _parse_user_choice(
            """Choosing an archived entry uses it as template for a new one. Do you want
            to [a]dd, [e]dit or [m]ove (copy from archive/move to archive) an entry?""",
            choices,
        )
    )

    if action is InputAction.add:
        # call function which asks user to enter the fields of the new record
        return get_entry().as_new()

    # no entries at all
    elif not archive_entries and not non_archive_entries:
        print_with_max_width("Currently, there are no entries. Exiting")
        raise KeyboardInterrupt

    elif action is InputAction.edit:
        # user wants to edit an existing entry
        # get index of the record
        index_str = _parse_user_choice(
            "Please enter the index of an entry:",
            [str(i) for i in range(len(non_archive_entries))],
        )
        # pass record to function where the user can edit the information
        return repr(get_entry(non_archive_entries[int(index_str)]))

    else:
        # user wants to move an active entry to the archive or the other way round
        active_entry_index_str_or_a = _get_index(
            len(non_archive_entries), additional=["a"] if archive_entries else []
        )
        if active_entry_index_str_or_a == "a":
            print_with_max_width(
                "Showing {} most recent archived entries".format(
                    no_of_archived_entries_to_show
                )
            )
            print_with_index(archive_entries[:no_of_archived_entries_to_show])
            archive_entry_index = _get_index(
                min(no_of_archived_entries_to_show, len(archive_entries))
            )
            _entry = archive_entries[int(archive_entry_index)]
            # give user possibility to edit entry before restoring it from the archive
            return get_entry(_entry, as_template=True).as_new()

        entry_to_move_to_archive = non_archive_entries[int(active_entry_index_str_or_a)]
        entry_to_move_to_archive.state = State.archive
        return repr(entry_to_move_to_archive)


def print_with_index(entries: List[Entry]) -> None:
    for index, entry in enumerate(entries):
        print_with_max_width(
            "[{index}]: {entry}".format(index=index, entry=colorful_entry_index(entry))
        )


def _get_index(
    max_index: int,
    min_index: int = 0,
    additional: Optional[List[str]] = None,
    prompt: str = "Please enter an index or any additional possibility:",
) -> str:
    """
    Parses the user's input for the selection of an index or any additional value.
    Expected to be called via `_get_index(len(List))`.
    :param max_index: Exclusive maximal index, as default by range
    :param min_index: Minimal index if different from 0
    :param additional: Any additional items which should be available for selection too
    :param prompt: Custom prompt to show.
    :return: Selected choice by the user as str
    """
    return _parse_user_choice(
        prompt, [str(i) for i in range(min_index, max_index)] + (additional or [])
    )


def _get_title(existing: str) -> str:
    return _parse_user_input("Please enter a short title of the record:", existing)


def _get_summary(existing: str) -> str:
    return _parse_user_input(
        """Please enter a short summary (1-2 sentences, this will be shown on 
        the huge monitors):""",
        existing,
    )


def _get_content_html(existing: str) -> str:
    return _parse_user_input(
        "Please enter the whole message (may be empty, replaces summary on infopage):",
        existing,
        allow_empty=True,
    )


def _get_begin(existing: datetime) -> datetime:
    return _get_date("Please enter Begin (YYYY-mm-dd or YYYY-mm-dd HH:MM):", existing)


def _get_eta(existing: Optional[datetime]) -> Optional[datetime]:
    return _get_date(
        "Please enter ETA (YYYY-mm-dd or YYYY-mm-dd HH:MM, may be empty):",
        existing,
        allow_empty=True,
    )


def _get_date(
    prompt: str = "Enter date:", existing: Optional[datetime] = None, allow_empty=False
) -> Optional[datetime]:
    """
    In normal mode this method asks the user to input a date and checks
    for a correct format afterwards.
    In validation mode, arguments via command line are parsed and returned
    if their format is valid.
    :param existing: Possibly existing input
    :param prompt: Prompt string to use
    """
    date_str = _parse_user_input(
        prompt,
        existing.strftime("%Y-%m-%d %H:%M") if existing else "",
        allow_empty=allow_empty,
    )
    if not date_str:
        return None

    try:
        return date_parse(date_str)

    except ValueError:
        print_with_max_width(
            """Your date could not be parsed, please input a valid date. Valid formats are %Y-%m-%d[ %H:%M]"""
        )
        return _get_date(prompt=prompt, existing=existing)


def _get_state(existing: State) -> State:
    return State[
        _parse_user_choice(
            "Please enter State of the record:",
            [str(state) for state in State],
            str(existing),
        )
    ]


def _get_severity(existing: Severity) -> Severity:
    return Severity[
        _parse_user_choice(
            "Please choose a severity level. Future Tasks/Announcements are categorized as green since they do not "
            "have an immediate impact, yellow expresses a malfunction and red an outage:",
            [str(severity) for severity in Severity],
            str(existing),
        )
    ]


def _parse_user_input(prompt: str, existing: str = "", allow_empty=False) -> str:
    """
    This function reads the input of the user and puts some text on it
    beforehand if existing is passed.
    :param prompt: prompt to show to the user
    :param existing: possible str which shall be edited instead of getting
    new input
    :param allow_empty: Whether empty input is allowed
    :return: gained input from user... if it is a plain c it will be
    interpreted as cancel
    """
    if existing:
        # write existing text to terminal
        readline.set_startup_hook(lambda: readline.insert_text(existing))
    print()
    print_with_max_width(Style.BRIGHT + prompt + Style.RESET_ALL)
    try:
        res = input()
        # reset function which is responsible for putting existing text to cmd
        readline.set_startup_hook()
    except EOFError:
        # ctrl+d shows the same prompt again
        return _parse_user_input(prompt, existing)

    finally:
        # reset function which is responsible for putting existing text to cmd
        readline.set_startup_hook()
    if not res and not allow_empty:
        print_with_max_width("Some input is mandatory.")
        return _parse_user_input(prompt, existing)

    return res


def _parse_user_choice(
    prompt: str, choices: Union[List[str], Dict[str, T]], existing: str = ""
) -> Union[str, T]:
    """
    Shows the submitted prompt string to the user and checks whether the given
    answer is one of the available choices. If not the process is repeated.
    :param prompt: Prompt to show for the user.
    :param choices: Available choices for the user. Either a list of str or a dictionary
    whose keys are str
    :param existing: possible str which shall be edited instead of getting
    new input
    :return: User's choice from the list or value of the selected key.
    """
    if existing:
        # write existing text to terminal, e.g. if an existing entry is modified
        readline.set_startup_hook(lambda: readline.insert_text(existing))
    # works in list and dictionary case since iterating over a dictionary
    # yields its keys
    choices_str = ", ".join(choices)
    print()
    print_with_max_width(Style.BRIGHT + prompt + Fore.GREEN)
    try:
        res = input(
            "Choose from {}:".format(choices_str) + Style.RESET_ALL + "\n"
        ).rstrip()
    except EOFError:
        return _parse_user_choice(prompt, choices, existing)

    finally:
        # reset function which is responsible for putting existing text to cmd
        readline.set_startup_hook()

    if res in choices:
        # if answer of the user is a valid one return it directly or the value of the
        # choices dictionary
        return choices[res] if isinstance(choices, dict) else res

    print_with_max_width(
        "Your answer is not available, please choose one from: {}".format(choices_str)
    )
    return _parse_user_choice(prompt, choices, existing)


def colorful_entry_index(entry: Entry) -> str:
    severity_to_color = {
        Severity.green: Fore.GREEN, Severity.yellow: Fore.YELLOW, Severity.red: Fore.RED
    }
    return "{title} {visible}".format(
        title=severity_to_color[entry.severity] + (entry.title or "[No Title]"),
        visible=Fore.CYAN
        + (Style.DIM if entry.state is State.hidden else Style.BRIGHT)
        + str(entry.state)
        + Style.RESET_ALL,
    )
