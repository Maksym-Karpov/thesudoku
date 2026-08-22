from abc import ABC, abstractmethod

from app.domain.entities.game import Game


class BaseRepository(ABC):
    @abstractmethod
    def save(self, game: Game) -> None:
        ...

    @abstractmethod
    def get(self, game_id: str) -> Game | None:
        ...

    @abstractmethod
    def get_or_raise(self, game_id: str) -> Game:
        ...
