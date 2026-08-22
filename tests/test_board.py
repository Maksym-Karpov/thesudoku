import pytest

from app.domain.entities.board import Board
from app.domain.exceptions import FixedCellError, InvalidCellValueError
from app.domain.value_objects.cell_position import CellPosition
from app.domain.value_objects.cell_value import CellValue


def test_set_value_rejects_row_conflict():
    """Setting a value that already exists in the same row should be rejected."""
    board = Board.empty()
    board.set_value(CellPosition(0, 0), CellValue.FIVE)
    with pytest.raises(InvalidCellValueError):
        board.set_value(CellPosition(0, 1), CellValue.FIVE)


def test_set_value_rejects_box_conflict():
    """Setting a value that already exists in the same 3x3 square should be rejected."""
    board = Board.empty()
    board.set_value(CellPosition(0, 0), CellValue.FIVE)
    with pytest.raises(InvalidCellValueError):
        board.set_value(CellPosition(1, 1), CellValue.FIVE)


def test_set_value_allows_same_row_position_overwrite():
    """Overwriting the same cell with a new value should succeed, since the old
    value at that position is not considered a conflict with itself."""
    board = Board.empty()
    board.set_value(CellPosition(0, 0), CellValue.FIVE)
    board.set_value(CellPosition(0, 0), CellValue.SIX)
    assert board.get_cell(CellPosition(0, 0)).value == CellValue.SIX


def test_set_value_on_fixed_cell_raises():
    """Cells marked as fixed (e.g. initial puzzle clues) must not be editable."""
    board = Board.empty()
    board.force_set(CellPosition(0, 0), CellValue.FIVE, is_fixed=True)
    with pytest.raises(FixedCellError):
        board.set_value(CellPosition(0, 0), CellValue.SIX)


def test_is_full_and_is_solved():
    """A freshly created empty board is neither full nor solved."""
    board = Board.empty()
    assert not board.is_full()
    assert not board.is_solved()


def test_clone_is_independent():
    """Cloning a board must produce a deep copy: mutating the clone must not
    affect the original board's cells."""
    board = Board.empty()
    clone = board.clone()
    clone.set_value(CellPosition(0, 0), CellValue.ONE)
    assert board.get_cell(CellPosition(0, 0)).value is None
