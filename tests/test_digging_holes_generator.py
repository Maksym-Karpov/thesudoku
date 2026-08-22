from app.domain.constants import GAME_DIFFICULTY_TO_CLUES_COUNT_MAP
from app.domain.services.digging_holes_generator import DiggingHolesGenerator
from app.domain.services.solution_generator import SolutionGenerator
from app.domain.value_objects.game_difficulty import GameDifficulty


def test_dig_removes_clues_down_to_the_difficulty_target():
    """Digging holes into a solved board must leave no more givens than the difficulty's clue target."""
    solution = SolutionGenerator().generate()
    puzzle = DiggingHolesGenerator().generate(solution=solution, difficulty=GameDifficulty.EASY)

    given_count = sum(1 for row in puzzle.get_rows() for cell in row if cell.value is not None)
    assert given_count <= GAME_DIFFICULTY_TO_CLUES_COUNT_MAP[GameDifficulty.EASY]


def test_dig_does_not_mutate_the_passed_in_solution():
    """Digging holes for a puzzle must not modify the original solution board."""
    solution = SolutionGenerator().generate()
    original_grid = solution.to_grid()

    DiggingHolesGenerator().generate(solution=solution, difficulty=GameDifficulty.HARD)

    assert solution.to_grid() == original_grid
