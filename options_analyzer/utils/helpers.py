"""
General helper functions used across modules.
"""

import datetime as dt
from typing import Union, List


def format_date(date_obj: Union[dt.date, dt.datetime, str]) -> str:
    """
    Format a date object as a string in YYYY-MM-DD format.
    
    Args:
        date_obj: Date object or string to format
        
    Returns:
        Formatted date string
    """
    if isinstance(date_obj, str):
        try:
            # Try to parse the string as a date
            date_obj = dt.datetime.strptime(date_obj, '%Y-%m-%d').date()
        except ValueError:
            # Return as is if parsing fails
            return date_obj
    
    if isinstance(date_obj, dt.datetime):
        date_obj = date_obj.date()
    
    return date_obj.strftime('%Y-%m-%d')


def format_currency(amount: float, include_cents: bool = True) -> str:
    """
    Format a number as currency.
    
    Args:
        amount: The amount to format
        include_cents: Whether to include cents
        
    Returns:
        Formatted currency string
    """
    if include_cents:
        return f"${amount:,.2f}"
    return f"${int(amount):,}"


def format_percent(value: float, decimals: int = 2) -> str:
    """
    Format a decimal as a percentage.
    
    Args:
        value: Decimal value (e.g., 0.05 for 5%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def calculate_days_between(start_date: Union[dt.date, dt.datetime, str], 
                          end_date: Union[dt.date, dt.datetime, str]) -> int:
    """
    Calculate the number of days between two dates.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Number of days between dates
    """
    # Convert to date objects if they are strings
    if isinstance(start_date, str):
        start_date = dt.datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = dt.datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Convert to date if they are datetime
    if isinstance(start_date, dt.datetime):
        start_date = start_date.date()
    if isinstance(end_date, dt.datetime):
        end_date = end_date.date()
    
    # Calculate difference
    delta = end_date - start_date
    return delta.days


def get_nearest_expiration_date(available_dates: List[str], 
                               target_days: int) -> str:
    """
    Find the nearest expiration date to a target number of days.
    
    Args:
        available_dates: List of available expiration dates in YYYY-MM-DD format
        target_days: Target number of days
        
    Returns:
        The nearest expiration date
    """
    today = dt.datetime.now().date()
    target_date = today + dt.timedelta(days=target_days)
    
    # Convert all dates to datetime.date objects for comparison
    date_objects = [dt.datetime.strptime(date_str, '%Y-%m-%d').date() 
                   for date_str in available_dates]
    
    # Find the closest date
    closest_date = min(date_objects, key=lambda d: abs((d - target_date).days))
    
    # Convert back to string format
    return closest_date.strftime('%Y-%m-%d')