from dataclasses import dataclass, field

from .exceptions import InvalidRequestException
from .strutils import is_alpha_char, substring_ignore_case


@dataclass
class ParlamentoCrawlRequest:
    legislature: set[int] = field(default_factory=lambda: {0})
    _letters: list[str] = field(default_factory=list)
    allowed_names: list[str] = field(default_factory=list)
    forbidden_names: list[str] = field(default_factory=list)

    def __post_init__(self):
        # use setter to validate and convert
        self.letters = self._letters

    @property
    def letters(self):
        return self._letters

    @letters.setter
    def letters(self, value: list[str]):
        self.validate_letters(value)
        self._letters = [letter.upper() for letter in value]  # Conversione in maiuscolo

    def validate_letters(self, value: list[str]):
        """Validazione delle lettere.
        Solleva un'eccezione se ci sono caratteri non validi.
        """
        if value:
            not_chars = [letter for letter in value if not is_alpha_char(letter)]
            if not_chars:
                raise InvalidRequestException(f"Le seguenti lettere non sono valide: {', '.join(not_chars)}")

    def normalize_legislature(self, ultima_legislatura):
        if self.legislature:
            normalized = map(lambda l: l if l > 0 else ultima_legislatura + l, self.legislature)
            self.legislature = set(normalized)

    def is_included(self, legislatura, lettera: str | None = None, name_to_check: str | None = None) -> bool:
        requested = True
        if legislatura and self.legislature:
            requested = requested and legislatura in self.legislature
        if lettera and self.letters:
            requested = requested and lettera.upper() in self.letters
        if name_to_check and self.allowed_names:
            found = any(substring_ignore_case(name, name_to_check) for name in self.allowed_names)
            requested = requested and found
        if name_to_check and self.forbidden_names:
            found = any(substring_ignore_case(name, name_to_check) for name in self.forbidden_names)
            requested = requested and not found
        return requested
