from dataclasses import dataclass, field

from .exceptions import InvalidRequestException


@dataclass
class ParlamentoCrawlRequest:
    legislature: set[int] = field(default_factory=lambda: {0})
    _lettere: list[str] = field(default_factory=list)
    allowed_names: list[str] = field(default_factory=list)
    forbidden_names: list[str] = field(default_factory=list)

    @property
    def lettere(self):
        return self._lettere

    @lettere.setter
    def lettere(self, value: list[str]):
        valid_letters = []
        for letter in value:
            if len(letter) != 1 or not letter.isalpha() or not letter.isascii():  # Controllo se è una lettera
                raise InvalidRequestException(f"'{letter}' non è una lettera valida.")
            valid_letters.append(letter.upper())  # Conversione in maiuscolo

        self._lettere = valid_letters

    def normalize_legislature(self, ultima_legislatura):
        if self.legislature:
            normalized = map(lambda l: l if l > 0 else ultima_legislatura + l, self.legislature)
            self.legislature = set(normalized)

    def is_included(self, legislatura, lettera=None, name_to_check=None) -> bool:
        requested = True
        if legislatura and self.legislature:
            requested = requested and legislatura in self.legislature
        if lettera and self.lettere:
            requested = requested and lettera in self.lettere
        if name_to_check and self.allowed_names:
            found = any(name in name_to_check for name in self.allowed_names)
            requested = requested and found
        if name_to_check and self.forbidden_names:
            found = any(name in name_to_check for name in self.forbidden_names)
            requested = requested and not found
        return requested
