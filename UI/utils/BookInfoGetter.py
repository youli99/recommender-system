import requests
import pandas as pd
import json


class BookInfoGetter(object):
    def __init__(self):
        self._book_info = None
        self._book_meta = pd.read_csv("UI/data/items_cleaned.csv")
        self._book_tags = pd.read_excel("UI/data/items_tagged.xlsx")

    def load_book_info(self, book_id):
        if book_id is None:
            raise ValueError("Book ID not set")

        book_meta = self._book_meta[self._book_meta["i"] == book_id]
        book_tags = self._book_tags[self._book_tags["i"] == book_id]

        if book_meta.empty or book_tags.empty:
            raise ValueError("Book ID not found in metadata or tags")

        isbn_raw = book_meta.iloc[0].get("ISBN Valid", "")
        isbn_list = str(isbn_raw).split('; ') if isbn_raw else []
        isbn = next((s for s in isbn_list if s.startswith("978")), None)

        book_info = {
            "title": book_meta.iloc[0]["Title"],
            "author": book_meta.iloc[0]["author_clean"],
            "isbn": isbn,
            "publisher": book_meta.iloc[0]["Publisher"],
            "tags": {
                "genre": book_tags.iloc[0]["Genre"],
                "subgenre": book_tags.iloc[0]["Subgenre"],
                "themes": eval(book_tags.iloc[0]["Themes"]),
                "tone_mood": eval(book_tags.iloc[0]["Tone_Mood"]),
                "target_audience": book_tags.iloc[0]["Target_Audience"],
                "short_summary": book_tags.iloc[0]["Short_Summary"],
            },
        }

        self._book_info = book_info

    def get_book_info(self, book_id):
        if book_id is None:
            raise ValueError("Book ID not set")
        self.load_book_info(book_id)
        return self._book_info

    def get_book_cover(self, book_id):
        if book_id is None:
            raise ValueError("Book ID not set")
        self.load_book_info(book_id)
        isbn = self._book_info["isbn"]
        if not isbn or len(isbn) == 0:
            return None
        url = f"https://bookcover.longitood.com/bookcover/{isbn}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("url")
        else:
            return None
