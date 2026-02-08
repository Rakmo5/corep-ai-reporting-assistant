from core.tools.calculator import Calculator


def test_compute_total():

    result = Calculator.compute_total(100, 50)

    assert result == 150

