"""Target construction utilities for DTRM experiments."""


def simple_return(start_price: float, end_price: float) -> float:
    """
    Calculate simple percentage return.

    R = (P_end - P_start) / P_start
    """
    if start_price <= 0:
        raise ValueError("start_price must be greater than zero.")

    return (end_price - start_price) / start_price


def market_adjusted_target(
    stock_return: float,
    beta: float,
    market_return: float,
) -> float:
    """
    Calculate the market-adjusted DTRM target.

    Y = stock_return - beta * market_return
    """
    return stock_return - beta * market_return