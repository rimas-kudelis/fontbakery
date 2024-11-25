import re
from functools import lru_cache
from pkg_resources import resource_filename

from fontbakery.utils import exit_with_install_instructions


@lru_cache(maxsize=1)
def registered_vendor_ids():
    """Get a list of vendor IDs from Microsoft's website."""

    try:
        from bs4 import BeautifulSoup, NavigableString
    except ImportError:
        exit_with_install_instructions("googlefonts")

    registered_vendor_ids = {}
    CACHED = resource_filename(
        "fontbakery", "data/fontbakery-microsoft-vendorlist.cache"
    )
    content = open(CACHED, encoding="utf-8").read()
    # Strip all <A> HTML tags from the raw HTML. The current page contains a
    # closing </A> for which no opening <A> is present, which causes
    # beautifulsoup to silently stop processing that section from the error
    # onwards. We're not using the href's anyway.
    content = re.sub("<a[^>]*>", "", content, flags=re.IGNORECASE)
    content = re.sub("</a>", "", content, flags=re.IGNORECASE)
    soup = BeautifulSoup(content, "html.parser")

    IDs = [chr(c + ord("a")) for c in range(ord("z") - ord("a") + 1)]
    IDs.append("0-9-")

    for section_id in IDs:
        section = soup.find("h2", {"id": section_id})
        if not section:
            continue

        table = section.find_next_sibling("table")
        if not table or isinstance(table, NavigableString):
            continue

        # print ("table: '{}'".format(table))
        for row in table.findAll("tr"):
            # print("ROW: '{}'".format(row))
            cells = row.findAll("td")
            if not cells:
                continue

            labels = list(cells[1].stripped_strings)

            # pad the code to make sure it is a 4 char string,
            # otherwise eg "CF  " will not be matched to "CF"
            code = cells[0].string.strip()
            code = code + (4 - len(code)) * " "
            registered_vendor_ids[code] = labels[0]

            # Do the same with NULL-padding:
            code = cells[0].string.strip()
            code = code + (4 - len(code)) * chr(0)
            registered_vendor_ids[code] = labels[0]

    return registered_vendor_ids