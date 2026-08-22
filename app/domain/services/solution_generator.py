from app.domain.entities.board import Board
from app.domain.exceptions import UnsolvableBoardError
from app.domain.services.sudoku_solver import SudokuSolver


class SolutionGenerator:
    def __init__(self, solver: SudokuSolver | None = None):
        self._solver = solver or SudokuSolver()

    def generate(self) -> Board:
        """
        Builds a fully solved, randomized Sudoku board
        """
        solved = self._solver.solve(board=Board.empty(), randomize=True)
        if solved is None:
            raise UnsolvableBoardError("Failed to generate a full Sudoku solution")
        return solved
