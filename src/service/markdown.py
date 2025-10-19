from pathlib import Path
from hashlib import sha256
import os
import pypandoc

class MarkdownHandler:
    _text: str = None
    _data: bytes = None
    _name: str = None
    _path: Path = None
    def __init__(self, text: str = None):
        self._text = text
        self._path = Path(os.getenv("HASH_PATH", "."))

    def normalize(self)-> bytes:
        return self._text.replace('\r\n', '\n').replace('\r', '\n').encode('utf-8')

    def save(self) -> str:
        self._path.mkdir(parents=True, exist_ok=True)
        data = self.normalize()
        h = sha256(data).hexdigest()
        full_path = self._path / f"{h}.md"

        if not full_path.exists():
            full_path.write_bytes(data)

        full_path = self._path / f"{h}.pdf"
        pypandoc.convert_text( self._text, to="pdf", format="md", outputfile=full_path, extra_args=['--standalone'])

        return h

    def load(self, name) -> str:
        full_path = self._path / f"{name}.md"
        if full_path.exists():
            self._text = full_path.read_text()
            return self._text
        else:
            raise Exception("The path does not exist")

    def set_text(self, text: str):
        self._text = text
        return self