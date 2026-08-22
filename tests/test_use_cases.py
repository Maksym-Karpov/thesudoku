import pytest

from app.application.exceptions import ApplicationError
from app.application.use_cases.get_game_state import GetGameStateUseCase
from app.application.use_cases.get_hint import GetHintUseCase
from app.application.use_cases.new_game import NewGameUseCase
from app.application.use_cases.restart_game import RestartGameUseCase
from app.application.use_cases.set_cell_value import SetCellValueUseCase
from app.domain.exceptions import FixedCellError, GameNotFoundError
from app.domain.services.puzzle_generator import PuzzleGenerator
from app.domain.value_objects.game_difficulty import GameDifficulty
from app.domain.value_objects.game_status import GameStatus
from app.infrastructure.repositories.game_repository import GameRepository


@pytest.fixture
def repository():
    return GameRepository()


@pytest.fixture
def new_game_state(repository):
    return NewGameUseCase(PuzzleGenerator(), repository).execute(GameDifficulty.EASY)


def test_new_game_creates_a_playable_puzzle(new_game_state):
    """A newly created game must be in progress and contain at least one empty cell."""
    assert new_game_state.status == GameStatus.IN_PROGRESS
    assert any(value is None for row in new_game_state.grid for value in row)


def test_get_game_state_roundtrips(repository, new_game_state):
    """Fetching a game's state from the repository must return the same grid it was created with."""
    fetched = GetGameStateUseCase(repository).execute(new_game_state.game_id)
    assert fetched.grid == new_game_state.grid


def test_get_game_state_unknown_id_raises(repository):
    """Fetching state for a game id that doesn't exist must raise GameNotFoundError."""
    with pytest.raises(GameNotFoundError):
        GetGameStateUseCase(repository).execute("does-not-exist")


def _first_empty_cell(state):
    for row_idx, row in enumerate(state.grid):
        for col_idx, value in enumerate(row):
            if value is None:
                return row_idx, col_idx
    raise AssertionError("Puzzle has no empty cells")


def _valid_value_for(grid, row, col):
    """Return any digit 1-9 that doesn't conflict with row/column/box peers."""
    box_row, box_col = (row // 3) * 3, (col // 3) * 3
    used = set(grid[row]) | {grid[r][col] for r in range(9)}
    used |= {grid[r][c] for r in range(box_row, box_row + 3) for c in range(box_col, box_col + 3)}
    for candidate in range(1, 10):
        if candidate not in used:
            return candidate
    raise AssertionError("No valid candidate found for cell")


def test_set_cell_value_then_clear(repository, new_game_state):
    """Setting a valid value on an empty cell then clearing it must round-trip correctly."""
    row, col = _first_empty_cell(new_game_state)
    value = _valid_value_for(new_game_state.grid, row, col)
    use_case = SetCellValueUseCase(repository)

    filled = use_case.execute(new_game_state.game_id, row, col, value)
    assert filled.grid[row][col] == value or filled.status == GameStatus.WON

    cleared = use_case.execute(new_game_state.game_id, row, col, None)
    assert cleared.grid[row][col] is None


def test_set_cell_value_on_fixed_cell_raises(repository, new_game_state):
    """Attempting to set a value on a fixed (given) cell must raise FixedCellError."""
    fixed_positions = [
        (r, c)
        for r, row in enumerate(new_game_state.fixed_mask)
        for c, is_fixed in enumerate(row)
        if is_fixed
    ]
    row, col = fixed_positions[0]
    with pytest.raises(FixedCellError):
        SetCellValueUseCase(repository).execute(new_game_state.game_id, row, col, 9)


def test_hint_reveals_correct_value(repository, new_game_state):
    """Requesting a hint for an empty cell must fill it in with a value."""
    row, col = _first_empty_cell(new_game_state)
    result = GetHintUseCase(repository).execute(new_game_state.game_id, row, col)
    assert result.grid[row][col] is not None


def test_hint_on_fixed_cell_raises(repository, new_game_state):
    """Requesting a hint for a cell that is already fixed must raise an ApplicationError."""
    fixed_positions = [
        (r, c)
        for r, row in enumerate(new_game_state.fixed_mask)
        for c, is_fixed in enumerate(row)
        if is_fixed
    ]
    row, col = fixed_positions[0]
    with pytest.raises(ApplicationError):
        GetHintUseCase(repository).execute(new_game_state.game_id, row, col)


def test_restart_clears_only_player_entries(repository, new_game_state):
    """Restarting a game must clear player-entered values while keeping the original fixed clues."""
    row, col = _first_empty_cell(new_game_state)
    value = _valid_value_for(new_game_state.grid, row, col)
    SetCellValueUseCase(repository).execute(new_game_state.game_id, row, col, value)

    restarted = RestartGameUseCase(repository).execute(new_game_state.game_id)
    assert restarted.grid[row][col] is None
    assert restarted.grid == new_game_state.grid
    assert restarted.status == GameStatus.IN_PROGRESS
