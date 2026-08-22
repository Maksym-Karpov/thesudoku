from app.domain.entities.board import Board
from app.domain.services.puzzle_generator import PuzzleGenerator
from app.domain.services.sudoku_solver import SudokuSolver
from app.domain.value_objects.cell_value import CellValue
from app.domain.value_objects.game_difficulty import GameDifficulty


def test_generate_puzzle_has_holes_and_valid_givens():
    """A generated puzzle must have empty cells, valid givens, a solved solution,
    and fixed cells matching exactly the cells that have a value."""
    puzzle, solution = PuzzleGenerator().generate(GameDifficulty.EASY)
    assert not puzzle.is_full()
    assert puzzle.is_valid()
    assert solution.is_solved()

    given_count = sum(1 for row in puzzle.get_rows() for cell in row if cell.value is not None)
    assert given_count <= 40  # EASY clue target reached (or fewer, still unique)

    for row in puzzle.get_rows():
        for cell in row:
            assert cell.is_fixed == (cell.value is not None)


def test_puzzle_clues_match_solution():
    """Every given clue in the puzzle must match the corresponding value in the solution."""
    puzzle, solution = PuzzleGenerator().generate(GameDifficulty.MEDIUM)
    for row_idx in range(Board.SIZE):
        for col_idx in range(Board.SIZE):
            puzzle_cell = puzzle.get_cell(puzzle.get_row(row_idx)[col_idx].position)
            if puzzle_cell.value is not None:
                assert puzzle_cell.value == solution.get_row(row_idx)[col_idx].value


def test_puzzle_has_unique_solution():
    """A generated puzzle must have exactly one solution."""
    puzzle, solution = PuzzleGenerator().generate(GameDifficulty.HARD)
    working_copy = puzzle.clone()
    assert SudokuSolver().count_solutions(working_copy, limit=2) == 1


def test_harder_difficulty_has_fewer_clues():
    """A HARD puzzle must have fewer given clues than an EASY puzzle."""
    generator = PuzzleGenerator()
    _, _ = generator.generate(GameDifficulty.EASY)
    easy_puzzle, _ = generator.generate(GameDifficulty.EASY)
    hard_puzzle, _ = generator.generate(GameDifficulty.HARD)

    def clue_count(board: Board) -> int:
        return sum(1 for row in board.get_rows() for cell in row if cell.value is not None)

    assert clue_count(hard_puzzle) < clue_count(easy_puzzle)


def test_solver_solves_a_puzzle_back_to_its_solution():
    """The solver must be able to reconstruct the original solution from a generated puzzle."""
    puzzle, solution = PuzzleGenerator().generate(GameDifficulty.HARD)
    solved = SudokuSolver().solve(board=puzzle)
    assert solved is not None
    assert solved == solution


def test_solver_reports_no_solution_for_broken_board():
    """The solver must return None when the board contains a conflicting/invalid arrangement."""
    board = Board.empty()
    board.force_set(board.get_row(0)[0].position, CellValue.ONE)
    board.force_set(board.get_row(0)[1].position, CellValue.ONE)  # duplicate in row -> unsolvable
    assert SudokuSolver().solve(board=board) is None
