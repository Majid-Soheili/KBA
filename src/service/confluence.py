import re
from typing import Iterable
from PyPDF2 import PdfReader

class ConfluenceService:

    _necessary_headings: Iterable[str] = (
        r"summary",
        r"overview",
        r"background\s*&\s*research",
    )

    _unwanted_headings_top: Iterable[str] = (
        r"contents?",
        r"important\s+links?",
        r"project\s+team",
        r"project\s+team\s*\(contact\s*people\)",
    )

    _unwanted_headings_bottom: Iterable[str] = (
        r"meeting\s+summaries?",
        r"changelog",
        r"references?",
        r"tasks?",
    )

    # we should remove the text from __unwanted_headings_top to _necessary_headings
    # also we should remove text from  _unwanted_headings_bottom to end of text.
    # each heading start from begining of the line

    _file_path: str
    def __init__(self, file_path: str = None) -> None:
        self._file_path = file_path
        # remove blocks from top unwanted headings → next necessary heading
        self._pat_to_summary = re.compile(
            rf"^(?:{self._alt(self._unwanted_headings_top)})\s*(?:\r?\n)+.*?"
            rf"(?=^(?:{self._alt(self._necessary_headings)})\b)",
            flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )

        # remove blocks from bottom unwanted headings → end of text
        self._pat_to_end = re.compile(
            rf"^(?:{self._alt(self._unwanted_headings_bottom)})\s*(?:\r?\n).*?\Z",
            flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )

    @staticmethod
    def _alt(parts: Iterable[str]) -> str:
        """Join patterns with | and wrap them in a non-capturing group."""
        return f"(?:{'|'.join(parts)})"

    def extract_text_from_pdf(self) -> str:
        reader = PdfReader(self._file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    def clean_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = self._pat_to_summary.sub("", text)
        text = self._pat_to_end.sub("", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return text

    def process_pdf(self) -> str:
        raw_text = self.extract_text_from_pdf()
        cleaned_text = self.clean_text(raw_text)
        return cleaned_text

    def set_file_path(self, file_path: str) -> "ConfluenceService":
        self._file_path = file_path
        return self
