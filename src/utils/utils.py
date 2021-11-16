from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from PyPDF2 import PdfFileMerger
from hashlib import md5
from typing import List
import requests
import tempfile
import os

from logger.logger import log
from settings.settings import settings


def get_full_menu():
    """
    Downloads and merges the new menu pdf and removes the one of the week before the current one.
    """
    urls = get_menus_urls()
    download_and_merge_pdfs(urls)
    cleanup_latest_pdf()


def get_menus_urls():
    """
    Gets the url download menus based on the current week and on the restaurant names
    from the official DSU page (https://www.dsu.toscana.it/i-menu).
    """
    menus_url = "https://www.dsu.toscana.it/i-menu"
    base_url = "https://www.dsu.toscana.it"
    menus = requests.get(menus_url)

    if not menus.status_code == 200:
        log.error(
            f"Possible error when retrieving the menus from the website, status code: {menus.status_code}"
        )

    soup = BeautifulSoup(menus.text, "html.parser")
    current_menu = get_week_end()

    urls = []
    for anchor in soup.findAll("a"):
        href = anchor.attrs["href"].lower()
        if (
            any([restaurant in href for restaurant in settings.restaurants])
            and "takeaway" not in href
            and current_menu in href
        ):
            urls.append(base_url + href)

    log.debug(urls)
    return urls


def download_and_merge_pdfs(urls: List[str]) -> None:
    """Downloads the pdfs from the given list of URLs, merges them into a single one, and saves the result."""
    with tempfile.TemporaryDirectory() as dirname:
        merger = PdfFileMerger()
        for url in urls:

            # Download PDF
            r = requests.get(url)

            # If it fails, go ahead with others
            if r.status_code != 200:
                continue

            # Store it on the temporary directory
            pdf_path = os.path.join(dirname, md5(url.encode()).hexdigest() + ".pdf")
            with open(pdf_path, "wb+") as f:
                f.write(r.content)

            # Append it for final merge
            merger.append(pdf_path)

        # Merge and save to the standard directory for merged menus
        merger.write(get_menu_path())
        merger.close()


def cleanup_latest_pdf() -> None:
    """
    Removes the pdf of the week preceding the current one.
    """
    old_menu = get_menu_path(-1)
    if os.path.exists(old_menu):
        os.remove(old_menu)


def get_week_start(week: int = 0) -> str:
    """
    Gets the week end date and returns it as a formatted string.
    Optionally, this can be get past or incoming weeks, if needed.
    """
    dt = datetime.now()
    start = dt - timedelta(days=dt.weekday())

    if week != 0:
        start += timedelta(weeks=week)
    return start.strftime("%d.%m.%Y")


def get_week_end(week: int = 0) -> str:
    """
    Gets the week end date and returns it as a formatted string.
    Optionally, this can be get past or incoming weeks, if needed.
    """
    dt = datetime.now()
    end = dt - timedelta(days=dt.weekday() - 6)

    if week != 0:
        end += timedelta(weeks=week)
    return end.strftime("%d.%m.%Y")


def get_menu_path(week: int = 0) -> str:
    """
    Returns the path of the merged pdf. Optionally, this can be get the paths of past or future pdfs, if needed.
    """
    return os.path.join(
        settings.menus_dir,
        get_week_end(week) + ".pdf",
    )


def get_menu_name() -> str:
    return f"Menù mensa {get_week_start()}-{get_week_end()}.pdf"
