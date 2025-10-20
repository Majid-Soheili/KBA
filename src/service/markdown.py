from pathlib import Path
from hashlib import sha256
import os
import pypandoc

class MarkdownHandler:
    _text: str = None
    _data: bytes = None
    _hash: str = None
    _path: Path = None
    def __init__(self, text: str = None):
        self.set_text(text)
        self._path = Path(os.getenv("HASH_PATH", "."))

        if os.getenv("HASH_PATH", ".") == ".":
            raise ValueError("HASH_PATH environment variable is not set")



    def normalize(self)-> bytes:
        return self._text.replace('\r\n', '\n').replace('\r', '\n').encode('utf-8')

    def save(self):
        self._path.mkdir(parents=True, exist_ok=True)
        full_path = self._path / f"{self._hash}.md"

        if not full_path.exists():
            full_path.write_bytes(self._data)
        return self

    def convert_to_pdf(self, name = None):
        if name is None:
            full_path = self._path / f"{self.get_hash()}.pdf"
        else:
            full_path = self._path / f"{name}.pdf"

        if not full_path.exists():
            pypandoc.convert_text( self._text, to="pdf", format="md", outputfile=str(full_path), extra_args=['--standalone', "--pdf-engine=xelatex"])
        return self

    def load(self, name):
        full_path = self._path / f"{name}.md"
        if full_path.exists():
            text = full_path.read_text()
            self.set_text(text)
            return self
        else:
            raise Exception("The path does not exist")

    def set_text(self, text: str):
        if text is None:
            self._text = None
            self._data = None
            self._hash = None
        else:
            self._text = text.replace('\r\n', '\n').replace('\r', '\n')
            self._data = self._text.encode('utf-8')
            self._hash = sha256(self._data).hexdigest()
        return self

    def get_text(self) -> str:
        return self._text
    def get_hash(self) -> str:
        return self._hash