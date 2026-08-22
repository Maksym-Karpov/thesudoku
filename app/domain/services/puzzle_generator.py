from app.domain.entities.board import Board
from app.domain.services.digging_holes_generator import DiggingHolesGenerator
from app.domain.services.solution_generator import SolutionGenerator
from app.domain.value_objects.game_difficulty import GameDifficulty


class PuzzleGenerator:
    def __init__(
        self,
        solution_generator: SolutionGenerator | None = None,
        holes_generator: DiggingHolesGenerator | None = None,
    ):
        self._solution_generator = solution_generator or SolutionGenerator()
        self._holes_generator = holes_generator or DiggingHolesGenerator()

    def generate(self, difficulty: GameDifficulty) -> tuple[Board, Board]:
        """
        Builds a solution and digs holes in it copy to match the desired difficulty
        """
        solution = self._solution_generator.generate()
        puzzle = self._holes_generator.generate(solution=solution, difficulty=difficulty)
        return puzzle, solution
