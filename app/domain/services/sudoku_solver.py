import random

from app.domain.entities.board import Board
from app.domain.exceptions import AttemptsBudgetExceeded
from app.domain.value_objects.cell_position import CellPosition
from app.domain.value_objects.cell_value import CellValue


class SudokuSolver:
    def solve(self, board: Board, randomize: bool = False) -> Board | None:
        """
        Solves board copy without changing given puzzle

        :returns (Board | None) a solved copy of the board, or None if no solution exists
        """
        working_copy = board.clone()
        if not working_copy.is_valid():
            return None
        if self._solve(board=working_copy, randomize=randomize):
            return working_copy
        return None

    def _solve(self, board: Board, randomize: bool = False) -> bool:
        """
        Sets recursively random applicable value for best cell candidate
        """
        position, candidates = self._get_mrv_cell(board=board)
        if position is None:
            return True
        if not candidates:
            return False

        if randomize:
            candidates = list(candidates)
            random.shuffle(candidates)

        for candidate in candidates:
            board.force_set(position=position, value=candidate)
            if self._solve(board=board, randomize=randomize):
                return True
            board.force_set(position=position, value=None)
        return False

    def count_solutions(self, board: Board, limit: int = 2, attempts_budget: int | None = None) -> int:
        """
        Count how many ways the board can be solved, stops when more than 1 way applicable

        :param board: board to solve
        :param limit: ways amount to solve
        :param attempts_budget: amount of recursive calls the search may make
        """
        if not board.is_valid():
            return 0
        remaining_attempts = [attempts_budget] if attempts_budget is not None else None
        return self._count_solutions(board=board, limit=limit, remaining_attempts=remaining_attempts)

    def _count_solutions(self, board: Board, limit: int, remaining_attempts: list[int] | None) -> int:
        if remaining_attempts is not None:
            remaining_attempts[0] -= 1
            if remaining_attempts[0] < 0:
                raise AttemptsBudgetExceeded("Exceeded attempts budget while counting solutions")

        position, candidates = self._get_mrv_cell(board=board)
        if (position, candidates) == (None, None):
            return 1

        found = 0
        for candidate in candidates:
            board.force_set(position=position, value=candidate)
            found += self._count_solutions(board=board, limit=limit - found, remaining_attempts=remaining_attempts)
            board.force_set(position=position, value=None)
            if found >= limit:
                return found
        return found

    def _get_mrv_cell(self, board: Board) -> tuple[CellPosition, list[CellValue]] | tuple[None, None]:
        best_position: CellPosition | None = None
        best_candidates: list[CellValue] | None = None

        for row in board.get_rows():
            for cell in row:
                if cell.value is not None:
                    continue
                candidates = self._search_value_candidates(board=board, position=cell.position)
                if not candidates:
                    return cell.position, candidates
                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_position, best_candidates = cell.position, candidates
                    if len(candidates) == 1:
                        return best_position, best_candidates

        if best_position is None:
            return None, None
        return best_position, best_candidates

    @staticmethod
    def _search_value_candidates(board: Board, position: CellPosition) -> list[CellValue]:
        row = board.get_row(row_idx=position.row_idx)
        column = board.get_column(column_idx=position.column_idx)
        square = board.get_square(square_idx=position.square_idx)
        peers = row + column + square

        used_values = {cell.value for cell in peers if cell.value is not None}
        return [value for value in CellValue if value not in used_values]


