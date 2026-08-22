from app.domain.value_objects.game_difficulty import GameDifficulty


GAME_DIFFICULTY_TO_CLUES_COUNT_MAP: dict[GameDifficulty, int] = {
    GameDifficulty.EASY: 40,
    GameDifficulty.MEDIUM: 32,
    GameDifficulty.HARD: 17,
}
