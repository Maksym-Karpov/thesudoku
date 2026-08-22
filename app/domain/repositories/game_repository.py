from abc import ABC, abstractmethod

from app.domain.entities.game import Game
from app.domain.exceptions import GameNotFoundError


class BaseRepository(ABC):
    @abstractmethod
    def save(self, game: Game) -> None:
        ...

    @abstractmethod
    def get(self, game_id: str) -> Game | None:
        ...

    def get_or_raise(self, game_id: str) -> Game:
        game = self.get(game_id=game_id)
        if game is None:
            raise GameNotFoundError(f"No game found with id {game_id}")
        return game
