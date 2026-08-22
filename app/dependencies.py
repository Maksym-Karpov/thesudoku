"""Shared composition root for every presentation adapter (CLI, web).

Wires one in-memory repository to every use case so the CLI and the web
app don't each have to duplicate the wiring logic.
"""

from dataclasses import dataclass

from app.application.use_cases.get_game_state import GetGameStateUseCase
from app.application.use_cases.get_hint import GetHintUseCase
from app.application.use_cases.new_game import NewGameUseCase
from app.application.use_cases.restart_game import RestartGameUseCase
from app.application.use_cases.set_cell_value import SetCellValueUseCase
from app.domain.services.puzzle_generator import PuzzleGenerator
from app.infrastructure.repositories.game_repository import GameRepository


@dataclass(frozen=True, slots=True)
class Dependencies:
    """Bundle of application-layer use cases handed to a presentation adapter."""

    new_game_use_case: NewGameUseCase
    get_game_state_use_case: GetGameStateUseCase
    set_cell_value_use_case: SetCellValueUseCase
    restart_game_use_case: RestartGameUseCase
    get_hint_use_case: GetHintUseCase


def dependencies_facade() -> Dependencies:
    """Build every use case wired to one shared in-memory repository."""
    repository = GameRepository()
    generator = PuzzleGenerator()

    return Dependencies(
        new_game_use_case=NewGameUseCase(generator=generator, repository=repository),
        get_game_state_use_case=GetGameStateUseCase(repository=repository),
        set_cell_value_use_case=SetCellValueUseCase(repository=repository),
        restart_game_use_case=RestartGameUseCase(repository=repository),
        get_hint_use_case=GetHintUseCase(repository=repository),
    )
