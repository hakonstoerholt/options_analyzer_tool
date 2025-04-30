"""
Functions for analyzing different options strategies.
"""

import datetime as dt
import math
import numpy as np


def analyze_cash_secured_puts(
    stock_info: dict, 
    options_data: dict, 
    min_premium_percent: float = 0.5,
    max_days_to_expiry: int = 45
) -> list:
    """
    Analyze cash secured put strategy for a given stock.
    
    Args:
        stock_info: Dictionary containing stock information
        options_data: Dictionary containing options chain data
        min_premium_percent: Minimum annualized premium percentage to consider (default: 0.5%)
        max_days_to_expiry: Maximum days to expiration to consider (default: 45 days)
        
    Returns:
        List of dictionaries with put option opportunities sorted by annualized return
    """
    current_price = stock_info['current_price']
    puts = options_data['puts']
    expiration_date = options_data['expiration_date']
    
    # Calculate days to expiration
    today = dt.datetime.now().date()
    expiry = dt.datetime.strptime(expiration_date, '%Y-%m-%d').date()
    days_to_expiry = (expiry - today).days
    
    # Ensure days_to_expiry is at least 1 to avoid division by zero
    days_to_expiry = max(1, days_to_expiry)
    
    # Skip if beyond max days to expiry
    if days_to_expiry > max_days_to_expiry:
        return []
    
    opportunities = []
    
    for put in puts:
        strike_price = put.get('strike', 0)
        bid_price = put.get('bid', 0)
        delta = put.get('delta') # Fetch delta if available
        
        # --- Add OTM Filter ---
        # Skip any puts that are At-The-Money (ATM) or In-The-Money (ITM)
        if strike_price >= current_price:
            continue
        # --- End OTM Filter ---

        # Skip options with no bid
        if bid_price <= 0:
            continue

        # --- Add Delta Filter ---
        # Skip if delta is available but outside the desired range (e.g., 0.05 to 0.40)
        if delta is not None and isinstance(delta, (int, float)):
            # Widen the acceptable delta range
            if not (0.05 <= abs(delta) <= 0.40):
                continue 
        # --- End Delta Filter ---
            
        # Calculate key metrics
        premium = bid_price * 100  # Convert to dollar amount (1 contract = 100 shares)
        cash_required = strike_price * 100
        premium_percent = (premium / cash_required) * 100 if cash_required else 0
        effective_purchase_price = strike_price - bid_price # Added metric
        
        # Fix annualized return calculation to be more reasonable
        # Use 252 trading days per year instead of 365 calendar days
        annualized_return = (premium_percent / days_to_expiry) * 252
        
        # Limit unreasonably high returns (cap at 1000%)
        annualized_return = min(1000, annualized_return)
        
        # Calculate probability metrics
        implied_volatility = put.get('impliedVolatility', 0)
        otm_percent = ((current_price - strike_price) / current_price) * 100 if current_price else 0
        
        # Use delta for probability if available and valid
        if delta is not None and isinstance(delta, (int, float)):
            # For puts, Prob OTM is approx 1 - abs(delta) (since delta is negative)
            probability_otm = (1 - abs(delta))
        # Fallback to calculation if delta is not usable
        elif implied_volatility < 0.01:  # Minimum IV to use in calculation
            # Simple moneyness-based probability estimate
            if strike_price >= current_price:  # ATM or ITM
                probability_otm = 0.5 * (1 - (strike_price - current_price) / current_price)
                probability_otm = max(0.05, probability_otm)  # At least 5% chance
            else:  # OTM
                probability_otm = 0.5 + 0.5 * ((current_price - strike_price) / current_price)
                probability_otm = min(0.95, probability_otm)  # At most 95% chance
        else:
            # Use Black-Scholes based probability for normal IV values
            std_dev = current_price * implied_volatility * math.sqrt(days_to_expiry / 365)
            
            # Avoid division by zero or very small values
            if std_dev < 0.01:
                std_dev = 0.01
                
            # Calculate probability OTM using normal distribution
            try:
                z_score = (strike_price - current_price) / std_dev
                probability_otm = 1 - norm_cdf(z_score)
            except (ZeroDivisionError, ValueError):
                # Fallback based on moneyness
                probability_otm = 0.5 + 0.3 * ((current_price - strike_price) / current_price)
                
            probability_otm = max(0.01, min(0.99, probability_otm))  # Reasonable bounds
        
        # Only include opportunities that meet the minimum premium criteria
        if annualized_return >= min_premium_percent:
            opportunities.append({
                'strike': strike_price,
                'premium': premium,
                'bid': bid_price,
                'ask': put.get('ask', 0),
                'implied_volatility': implied_volatility,
                'days_to_expiry': days_to_expiry,
                'cash_required': cash_required,
                'premium_percent': premium_percent,
                'annualized_return': annualized_return,
                'effective_purchase_price': effective_purchase_price, # Added metric
                'otm_percent': otm_percent,
                'probability_otm': probability_otm * 100,  # Convert to percentage
                'delta': delta, # Include delta if available
                'volume': put.get('volume', 0),
                'open_interest': put.get('openInterest', 0)
            })
    
    # Sort by annualized return (highest first)
    opportunities.sort(key=lambda x: x['annualized_return'], reverse=True)
    
    return opportunities


# Helper function for normal cumulative distribution function
def norm_cdf(x):
    """
    Calculate the standard normal cumulative distribution function.
    Simple approximation when scipy is not available.
    """
    try:
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
    except (ValueError, OverflowError):
        # Return extremes for large values to avoid math domain errors
        return 0.0 if x < -5 else 1.0 if x > 5 else 0.5


def analyze_covered_calls(
    stock_info: dict, 
    options_data: dict,
    shares_owned: int = 100,
    cost_basis: float = None,
    min_premium_percent: float = 0.5,
    max_days_to_expiry: int = 45
) -> list:
    """
    Analyze covered call strategy for a given stock.
    
    Args:
        stock_info: Dictionary containing stock information
        options_data: Dictionary containing options chain data
        shares_owned: Number of shares owned (default: 100)
        cost_basis: Average cost per share (if None, uses current price)
        min_premium_percent: Minimum annualized premium percentage to consider (default: 0.5%)
        max_days_to_expiry: Maximum days to expiration to consider (default: 45 days)
        
    Returns:
        List of dictionaries with call option opportunities sorted by annualized return
    """
    current_price = stock_info['current_price']
    calls = options_data['calls']
    expiration_date = options_data['expiration_date']
    
    # If cost basis not provided, use current price
    if cost_basis is None:
        cost_basis = current_price
    
    # Calculate days to expiration
    today = dt.datetime.now().date()
    expiry = dt.datetime.strptime(expiration_date, '%Y-%m-%d').date()
    days_to_expiry = (expiry - today).days
    
    # Ensure days_to_expiry is at least 1 to avoid division by zero
    days_to_expiry = max(1, days_to_expiry)
    
    # Skip if beyond max days to expiry
    if days_to_expiry > max_days_to_expiry:
        return []
    
    opportunities = []
    
    for call in calls:
        strike_price = call.get('strike', 0)
        bid_price = call.get('bid', 0)
        delta = call.get('delta') # Fetch delta if available

        # --- Add OTM Filter ---
        # Skip any calls that are At-The-Money (ATM) or In-The-Money (ITM)
        if strike_price <= current_price:
            continue
        # --- End OTM Filter ---
        
        # Skip options with no bid
        if bid_price <= 0:
            continue

        # --- Add Delta Filter ---
        # Skip if delta is available but outside the desired range (e.g., 0.05 to 0.40)
        if delta is not None and isinstance(delta, (int, float)):
            # Widen the acceptable delta range
            if not (0.05 <= delta <= 0.40):
                continue
        # --- End Delta Filter ---
            
        # Skip options with strikes below cost basis if desired
        # Uncomment this if you want to avoid calls below cost basis
        # if strike_price < cost_basis:
        #     continue
        
        # Calculate key metrics
        contracts = math.floor(shares_owned / 100)
        premium = bid_price * 100 * contracts
        capital_invested = cost_basis * shares_owned
        premium_percent = (premium / capital_invested) * 100
        
        # Fix annualized return calculation to be more reasonable
        # Use 252 trading days per year instead of 365 calendar days
        annualized_return = (premium_percent / days_to_expiry) * 252
        
        # Limit unreasonably high returns (cap at 1000%)
        annualized_return = min(1000, annualized_return)
        
        # Calculate potential profit if called away
        potential_profit = ((strike_price - cost_basis) * shares_owned) + premium
        potential_profit_percent = (potential_profit / capital_invested) * 100
        annualized_profit_if_called = (potential_profit_percent / days_to_expiry) * 252
        annualized_profit_if_called = min(1000, annualized_profit_if_called)  # Cap at 1000%
        
        # Calculate probability metrics
        implied_volatility = call.get('impliedVolatility', 0)
        otm_percent = ((strike_price - current_price) / current_price) * 100 if current_price else 0
        
        # Use delta for probability if available and valid
        if delta is not None and isinstance(delta, (int, float)):
             # For calls, Prob OTM is approx 1 - delta
             probability_otm = (1 - delta)
        # Fallback to calculation if delta is not usable
        elif implied_volatility < 0.01:  # Minimum IV to use in calculation
            # Simple moneyness-based probability estimate
            if strike_price <= current_price:  # ATM or ITM
                probability_otm = 0.5 * (1 - (current_price - strike_price) / current_price)
                probability_otm = max(0.05, probability_otm)  # At least 5% chance
            else:  # OTM
                probability_otm = 0.5 + 0.5 * ((strike_price - current_price) / current_price)
                probability_otm = min(0.95, probability_otm)  # At most 95% chance
        else:
            # Use Black-Scholes based probability for normal IV values
            std_dev = current_price * implied_volatility * math.sqrt(days_to_expiry / 365)
            
            # Avoid division by zero or very small values
            if std_dev < 0.01:
                std_dev = 0.01
                
            # Calculate probability OTM using normal distribution
            try:
                z_score = (strike_price - current_price) / std_dev
                probability_otm = norm_cdf(z_score)
            except (ZeroDivisionError, ValueError):
                # Fallback based on moneyness
                probability_otm = 0.5 + 0.3 * ((strike_price - current_price) / current_price)
                
            probability_otm = max(0.01, min(0.99, probability_otm))  # Reasonable bounds
        
        # Only include opportunities that meet the minimum premium criteria
        if annualized_return >= min_premium_percent:
            opportunities.append({
                'strike': strike_price,
                'premium': premium,
                'premium_per_contract': bid_price * 100,
                'bid': bid_price,
                'ask': call.get('ask', 0),
                'implied_volatility': implied_volatility,
                'days_to_expiry': days_to_expiry,
                'premium_percent': premium_percent,
                'annualized_return': annualized_return,
                'potential_profit_if_called': potential_profit,
                'potential_profit_percent': potential_profit_percent,
                'annualized_profit_if_called': annualized_profit_if_called,
                'otm_percent': otm_percent,
                'probability_otm': probability_otm * 100,  # Convert to percentage
                'delta': delta, # Include delta if available
                'volume': call.get('volume', 0),
                'open_interest': call.get('openInterest', 0)
            })
    
    # Sort by annualized return (highest first)
    opportunities.sort(key=lambda x: x['annualized_return'], reverse=True)
    
    return opportunities