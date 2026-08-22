from app.application.dto.game_state_dto import GameStateDTO
from app.domain.repositories.game_repository import BaseRepository
from app.domain.entities.game import Game
from app.domain.services.puzzle_generator import PuzzleGenerator
from app.domain.value_objects.game_difficulty import GameDifficulty


class NewGameUseCase:
    def __init__(self, generator: PuzzleGenerator, repository: BaseRepository):
        self._generator = generator
        self._repository = repository

    def execute(self, difficulty: GameDifficulty) -> GameStateDTO:
        puzzle, solution = self._generator.generate(difficulty=difficulty)
        game = Game(board=puzzle, solution=solution, difficulty=difficulty)
        self._repository.save(game=game)
        return GameStateDTO.from_game(game=game)
