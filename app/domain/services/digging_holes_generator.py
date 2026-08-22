import random

from app.domain.constants import GAME_DIFFICULTY_TO_CLUES_COUNT_MAP
from app.domain.entities.board import Board
from app.domain.exceptions import AttemptsBudgetExceeded
from app.domain.services.sudoku_solver import SudokuSolver
from app.domain.value_objects.cell_position import CellPosition
from app.domain.value_objects.game_difficulty import GameDifficulty


_UNIQUENESS_CHECK_ATTEMPTS_BUDGET = 64


class DiggingHolesGenerator:
    def __init__(self, solver: SudokuSolver | None = None):
        self._solver = solver or SudokuSolver()

    def generate(self, solution: Board, difficulty: GameDifficulty) -> Board:
        """
        Digs holes in copy of the solution, returning a ready puzzle
        """
        puzzle = solution.clone()

        target_clues = GAME_DIFFICULTY_TO_CLUES_COUNT_MAP[difficulty]
        all_positions: list[CellPosition] = []
        for row in puzzle.get_rows():
            for cell in row:
                all_positions.append(cell.position)
        random.shuffle(all_positions)

        clues_remaining = Board.SIZE * Board.SIZE
        for position in all_positions:
            if clues_remaining <= target_clues:
                break
            if self._dig_hole(puzzle=puzzle, position=position):
                clues_remaining -= 1

        self._mark_cells_with_value_as_fixed(puzzle=puzzle)
        return puzzle

    def _dig_hole(self, puzzle: Board, position: CellPosition) -> bool:
        """
        Remove the value at the given position if the puzzle still has a unique solution
        """
        original_value = puzzle.get_cell(position=position).value
        puzzle.force_set(position=position, value=None)

        if self._is_unique_solution(puzzle=puzzle):
            return True

        puzzle.force_set(position=position, value=original_value)
        return False

    def _is_unique_solution(self, puzzle: Board) -> bool:
        working_copy = puzzle.clone()
        try:
            solution_count = self._solver.count_solutions(
                board=working_copy, limit=2, attempts_budget=_UNIQUENESS_CHECK_ATTEMPTS_BUDGET
            )
        except AttemptsBudgetExceeded:
            return False
        return solution_count == 1

    @staticmethod
    def _mark_cells_with_value_as_fixed(puzzle: Board) -> None:
        """
        Mark every cell that still has value as fixed
        """
        for row in puzzle.get_rows():
            for cell in row:
                puzzle.force_set(position=cell.position, value=cell.value, is_fixed=cell.value is not None)
