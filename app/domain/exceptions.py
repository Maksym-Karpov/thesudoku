class DomainError(Exception):
    """
    Base class for all domain errors
    """


class FixedCellError(DomainError):
    """
    Raised when user trying to mutate cell that which part of the puzzle
    """


class InvalidCellValueError(DomainError):
    """
    Raised when cell value would violate row or column or square unique values
    """


class InvalidCellPositionValueError(DomainError):
    """
    Raised when invalid cell value position provided
    """


class UnsolvableBoardError(DomainError):
    """
    Raised when can not find solution for board
    """


class InvalidBoardCellsAmount(DomainError):
    """
    Raised when board has invalid amount of cells
    """


class ServiceError(DomainError):
    """
    Raised when a service encounters an error
    """


class AttemptsBudgetExceeded(ServiceError):
    """
    Raised when a search exhausts its allotted attempts budget before settling
    """


class GameNotFoundError(DomainError):
    """
    Raised when a game_id given to a repository isn't in the repository
    """
