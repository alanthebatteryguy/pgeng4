from .optimize import optimize
from .results import display_results


def main() -> None:
    # example inputs
    inputs = {'fc': 6000, 'span': 30}
    overrides = {}
    result = optimize(inputs, overrides)
    display_results(result)


if __name__ == '__main__':
    main()
