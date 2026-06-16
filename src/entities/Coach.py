from dataclasses import dataclass, field
from typing import List


@dataclass
class Coach:
    name: str
    biography: str = ""
    teams: List[str] = field(default_factory=list)   # clubes que já treinou
    style: str = ""                                   # estilo de jogo / características
