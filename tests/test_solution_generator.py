from app.domain.services.solution_generator import SolutionGenerator


def test_generate_solution_is_full_and_valid():
    """A generated solution board must be fully filled, valid, and solved."""
    solution = SolutionGenerator().generate()
    assert solution.is_full()
    assert solution.is_valid()
    assert solution.is_solved()


def test_generate_solution_is_randomized():
    """Repeated generations should not always produce the same solution board."""
    generator = SolutionGenerator()
    boards = [generator.generate() for _ in range(5)]
    assert len({tuple(map(tuple, b.to_grid())) for b in boards}) > 1
