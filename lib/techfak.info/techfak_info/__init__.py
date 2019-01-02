from typing import Union, Dict
from configparser import ConfigParser, SectionProxy, ExtendedInterpolation
from pathlib import Path
from os import getuid

if getuid() == 0:
    print(
        """!!Do not run any of theses scripts as root or fix the
        permissions afterwards!\n"""
    )

# type signature of an entry as a dictionary
JsonFeedEntry = Dict[str, Union[Dict[str, Union[str, bool, None]], str]]

# read config
CONFIG = ConfigParser(interpolation=ExtendedInterpolation())
parsed_config_files = CONFIG.read(
    [
        # location of production config; expects this file to be in
        # $PREFIX/lib/techfak.info/techfak_info
        str(
            Path(__file__).resolve().parent.parent.parent.parent
            / "etc/techfak_info.conf"
        ),
        # in case of development read local as last to overwrite production values
        "techfak_info.conf",
    ]
)

if not parsed_config_files:
    print("Could not find config file in techfak_info directory nor parent")
    exit(2)

FEED = CONFIG["feed"]  # type: SectionProxy
COMMON = CONFIG["DEFAULT"]  # type: SectionProxy
CHECK = CONFIG["check"]  # type: SectionProxy
MAIL = CONFIG["mail"]  # type: SectionProxy

JSONFEED = {
    "version": FEED["version"],
    "title": FEED["title"],
    "home_page_url": FEED["home_page_url"],
    "feed_url": FEED["feed_url"],
    "user_comment": FEED["user_comment"],
    "items": [],
}
