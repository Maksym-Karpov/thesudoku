from app.application.dto.game_state_dto import GameStateDTO
from app.infrastructure.repositories.base_repository import BaseRepository


class RestartGameUseCase:
    def __init__(self, repository: BaseRepository):
        self._repository = repository

    def execute(self, game_id: str) -> GameStateDTO:
        game = self._repository.get_or_raise(game_id=game_id)
        game.restart()
        self._repository.save(game=game)
        return GameStateDTO.from_game(game=game)
