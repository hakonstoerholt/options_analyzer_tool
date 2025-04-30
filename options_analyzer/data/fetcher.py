"""
Functions for fetching stock and options data using yfinance.
"""

import datetime as dt
import pandas as pd
import yfinance as yf


def get_stock_info(ticker: str) -> dict:
    """
    Fetch basic stock information for a given ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        
    Returns:
        Dictionary containing stock information
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Calculate dividend yield manually for more accuracy
        dividend_yield = 0
        dividend_rate = info.get('dividendRate', 0)
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        
        if dividend_rate and current_price:
            dividend_yield = dividend_rate / current_price
        else:
            # Fallback to provided dividendYield if available
            raw_yield = info.get('dividendYield', 0)
            # Fix common error where yield is provided as percentage not decimal
            if raw_yield > 1:  # Likely a percentage (e.g., 47 instead of 0.47)
                dividend_yield = raw_yield / 100
            else:
                dividend_yield = raw_yield
        
        # Extract the most relevant information
        relevant_info = {
            'symbol': ticker,
            'name': info.get('shortName', 'Unknown'),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'current_price': current_price,
            'previous_close': info.get('previousClose', 0),
            'open': info.get('open', 0),
            'day_low': info.get('dayLow', 0),
            'day_high': info.get('dayHigh', 0),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
            'volume': info.get('volume', 0),
            'avg_volume': info.get('averageVolume', 0),
            'market_cap': info.get('marketCap', 0),
            'beta': info.get('beta', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'eps': info.get('trailingEps', 0),
            'dividend_rate': dividend_rate,
            'dividend_yield': dividend_yield,
            'ex_dividend_date': info.get('exDividendDate', None),
        }
        
        return relevant_info
    except Exception as e:
        raise Exception(f"Failed to fetch stock info for {ticker}: {str(e)}")


def get_options_chain(ticker: str, expiration_date: str = None) -> dict:
    """
    Fetch options chain for a given ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        expiration_date: Options expiration date in 'YYYY-MM-DD' format.
                         If None, fetches the nearest expiration date.
        
    Returns:
        Dictionary with 'calls' and 'puts' DataFrames
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get available expiration dates
        expirations = stock.options
        
        if not expirations:
            raise ValueError(f"No options data available for {ticker}")
        
        # If no expiration date specified, use the nearest one
        if expiration_date is None:
            expiration_date = expirations[0]
        elif expiration_date not in expirations:
            # Find the nearest available expiration date
            expiration_date = min(expirations, key=lambda x: 
                                 abs((dt.datetime.strptime(x, '%Y-%m-%d') - 
                                      dt.datetime.strptime(expiration_date, '%Y-%m-%d')).days))
        
        # Get options chain for the specified date
        options = stock.option_chain(expiration_date)
        
        # Convert to dictionaries for easier handling
        calls = options.calls.to_dict('records')
        puts = options.puts.to_dict('records')
        
        return {
            'expiration_date': expiration_date,
            'calls': calls,
            'puts': puts,
        }
    except Exception as e:
        raise Exception(f"Failed to fetch options data for {ticker}: {str(e)}")


def get_historical_data(ticker: str, period: str = '1y') -> pd.DataFrame:
    """
    Fetch historical price data for a given ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        period: Time period (e.g., '1d', '1mo', '1y')
        
    Returns:
        DataFrame with historical price data
    """
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period=period)
        return history
    except Exception as e:
        raise Exception(f"Failed to fetch historical data for {ticker}: {str(e)}")


def get_available_expirations(ticker: str) -> list:
    """
    Get all available option expiration dates for a ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        
    Returns:
        List of expiration dates in 'YYYY-MM-DD' format
    """
    try:
        stock = yf.Ticker(ticker)
        return list(stock.options)
    except Exception as e:
        raise Exception(f"Failed to fetch expiration dates for {ticker}: {str(e)}")