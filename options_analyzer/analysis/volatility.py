"""
Functions for calculating volatility metrics for stocks.
"""

import numpy as np
import pandas as pd
import datetime as dt


def calculate_days_between(date1_str: str, date2_str: str) -> int:
    """
    Calculate the number of days between two date strings.
    
    Args:
        date1_str: First date in 'YYYY-MM-DD' format
        date2_str: Second date in 'YYYY-MM-DD' format
        
    Returns:
        Number of days between the two dates
    """
    date1 = dt.datetime.strptime(date1_str, '%Y-%m-%d').date()
    date2 = dt.datetime.strptime(date2_str, '%Y-%m-%d').date()
    return abs((date2 - date1).days)


def calculate_historical_volatility(price_data: pd.DataFrame, window: int = 252) -> float:
    """
    Calculate historical volatility from a price series.
    
    Args:
        price_data: DataFrame with historical prices (must have 'Close' column)
        window: Number of trading days to use for calculation (default: 252 = 1 year)
        
    Returns:
        Annualized historical volatility as a decimal (e.g., 0.25 for 25%)
    """
    # Calculate daily returns
    returns = price_data['Close'].pct_change().dropna()
    
    # Use only the specified window
    if len(returns) > window:
        returns = returns[-window:]
    
    # Calculate standard deviation and annualize
    daily_std_dev = returns.std()
    annualized_vol = daily_std_dev * np.sqrt(252)
    
    return annualized_vol


def calculate_expected_move(stock_price: float, implied_volatility: float, days: int = 7) -> float:
    """
    Calculate the expected move of a stock based on its implied volatility.
    
    Args:
        stock_price: Current stock price
        implied_volatility: Implied volatility as a decimal (e.g., 0.3 for 30%)
        days: Number of days for the expected move calculation (default: 7)
        
    Returns:
        Expected dollar move (1 standard deviation) for the given timeframe
    """
    # Convert days to years
    years = days / 365
    
    # 1 standard deviation move = stock_price * volatility * sqrt(time)
    expected_move = stock_price * implied_volatility * np.sqrt(years)
    
    return expected_move


def get_atm_implied_volatility(options_data: dict, stock_price: float) -> float:
    """
    Extract the at-the-money (ATM) implied volatility from options chain.
    
    Args:
        options_data: Options chain data dictionary
        stock_price: Current stock price
        
    Returns:
        ATM implied volatility as a decimal
    """
    # Get calls and puts
    calls = options_data.get('calls', [])
    puts = options_data.get('puts', [])
    
    # Find ATM strikes (closest to current stock price)
    if calls:
        closest_call = min(calls, key=lambda x: abs(x.get('strike', 0) - stock_price))
        call_iv = closest_call.get('impliedVolatility', 0)
    else:
        call_iv = 0
    
    if puts:
        closest_put = min(puts, key=lambda x: abs(x.get('strike', 0) - stock_price))
        put_iv = closest_put.get('impliedVolatility', 0)
    else:
        put_iv = 0
    
    # Use average of call and put IV if both are available
    if call_iv > 0 and put_iv > 0:
        return (call_iv + put_iv) / 2
    elif call_iv > 0:
        return call_iv
    elif put_iv > 0:
        return put_iv
    else:
        return 0.0