"""
Functions for formatting and displaying output in the console.
"""

import pandas as pd
from typing import Dict, List, Any
from tabulate import tabulate


def show_stock_info(stock_info: Dict[str, Any]):
    """
    Display stock information in a formatted way.
    
    Args:
        stock_info: Dictionary containing stock information
    """
    print("\n" + "=" * 80)
    print(f"Stock Information: {stock_info['name']} ({stock_info['symbol']})")
    print("=" * 80)
    
    # Create a structured view of the data
    data = [
        ["Price", f"${stock_info['current_price']:.2f}"],
        ["Previous Close", f"${stock_info['previous_close']:.2f}"],
        ["52-Week Range", f"${stock_info['fifty_two_week_low']:.2f} - ${stock_info['fifty_two_week_high']:.2f}"],
        ["Sector", stock_info['sector']],
        ["Industry", stock_info['industry']],
        ["Volume", f"{stock_info['volume']:,}"],
        ["Avg Volume", f"{stock_info['avg_volume']:,}"],
        ["Market Cap", f"${stock_info['market_cap'] / 1_000_000_000:.2f}B"],
        ["Beta", f"{stock_info['beta']:.2f}"],
        ["P/E Ratio", f"{stock_info['pe_ratio']:.2f}"],
        ["EPS", f"${stock_info['eps']:.2f}"],
        # Fix dividend yield display - it's already a decimal in the data, so multiply by 100 for proper percentage
        ["Dividend Yield", f"{stock_info['dividend_yield'] * 100:.2f}%" if stock_info['dividend_yield'] else "N/A"],
    ]
    
    print(tabulate(data, tablefmt="simple"))
    print("\n")


def show_volatility_metrics(volatility_metrics: Dict[str, Any]):
    """
    Display volatility metrics in a formatted way.
    
    Args:
        volatility_metrics: Dictionary containing volatility metrics
    """
    print("\n" + "=" * 80)
    print("Volatility Metrics")
    print("=" * 80)
    
    # Create a structured view of the data
    data = [
        ["Implied Volatility (ATM)", f"{volatility_metrics['implied_volatility'] * 100:.2f}%"],
        ["Historical Volatility (1Y)", f"{volatility_metrics['historical_volatility'] * 100:.2f}%"],
        ["Expected Move (7d)", f"${volatility_metrics['expected_move_7d']:.2f} (±{volatility_metrics['expected_move_percent_7d']:.2f}%)"],
        ["Expected Move (30d)", f"${volatility_metrics['expected_move_30d']:.2f} (±{volatility_metrics['expected_move_percent_30d']:.2f}%)"],
    ]
    
    print(tabulate(data, tablefmt="simple"))
    print("\n")


def show_cash_secured_puts(opportunities: List[Dict[str, Any]]):
    """
    Display cash secured put opportunities in a formatted table.
    
    Args:
        opportunities: List of dictionaries containing put option details
    """
    if not opportunities:
        print("No suitable cash secured put opportunities found.")
        return
    
    print("\n" + "=" * 80)
    print("Cash Secured Put Opportunities")
    print("=" * 80)
    
    # Convert to DataFrame for easier formatting
    df = pd.DataFrame(opportunities)
    
    # Select and rename columns for display
    display_df = df[['strike', 'bid', 'premium', 'effective_purchase_price', 'days_to_expiry', 'annualized_return', 
                     'cash_required', 'probability_otm', 'implied_volatility', 'volume', 'open_interest']]
    
    display_df = display_df.rename(columns={
        'strike': 'Strike',
        'bid': 'Bid',
        'premium': 'Premium ($)', # Corrected string literal
        'effective_purchase_price': 'Eff. Price ($)', # Corrected string literal
        'days_to_expiry': 'Days',
        'annualized_return': 'Ann. Return (%)',
        'cash_required': 'Cash Req. ($)', # Corrected string literal
        'probability_otm': 'Prob. OTM (%)',
        'implied_volatility': 'IV',
        'volume': 'Volume',
        'open_interest': 'OI'
    })
    
    # Format the numeric columns
    display_df['Ann. Return (%)'] = display_df['Ann. Return (%)'].map('{:.2f}'.format)
    display_df['Eff. Price ($)'] = display_df['Eff. Price ($)'].map('{:.2f}'.format) # Corrected key
    display_df['IV'] = display_df['IV'].map('{:.2f}'.format)
    display_df['Prob. OTM (%)'] = display_df['Prob. OTM (%)'].map('{:.2f}'.format)
    
    print(tabulate(display_df.head(10), headers='keys', tablefmt='simple', showindex=False))
    print("\n")


def show_covered_calls(opportunities: List[Dict[str, Any]]):
    """
    Display covered call opportunities in a formatted table.
    
    Args:
        opportunities: List of dictionaries containing call option details
    """
    if not opportunities:
        print("No suitable covered call opportunities found.")
        return
    
    print("\n" + "=" * 80)
    print("Covered Call Opportunities")
    print("=" * 80)
    
    # Convert to DataFrame for easier formatting
    df = pd.DataFrame(opportunities)
    
    # Select and rename columns for display
    display_df = df[['strike', 'bid', 'premium_per_contract', 'days_to_expiry', 
                     'annualized_return', 'annualized_profit_if_called', 'probability_otm', 
                     'implied_volatility', 'volume', 'open_interest']]
    
    display_df = display_df.rename(columns={
        'strike': 'Strike',
        'bid': 'Bid',
        'premium_per_contract': 'Premium ($)',
        'days_to_expiry': 'Days',
        'annualized_return': 'Ann. Premium (%)',
        'annualized_profit_if_called': 'Ann. If Called (%)',
        'probability_otm': 'Prob. OTM (%)',
        'implied_volatility': 'IV',
        'volume': 'Volume',
        'open_interest': 'OI'
    })
    
    # Format the numeric columns
    display_df['Ann. Premium (%)'] = display_df['Ann. Premium (%)'].map('{:.2f}'.format)
    display_df['Ann. If Called (%)'] = display_df['Ann. If Called (%)'].map('{:.2f}'.format)
    display_df['IV'] = display_df['IV'].map('{:.2f}'.format)
    display_df['Prob. OTM (%)'] = display_df['Prob. OTM (%)'].map('{:.2f}'.format)
    
    print(tabulate(display_df.head(10), headers='keys', tablefmt='simple', showindex=False))
    print("\n")


def show_analysis_results(results: Dict[str, Any], strategy_type: str):
    """
    Display analysis results for a given strategy.
    
    Args:
        results: Dictionary containing analysis results
        strategy_type: Type of options strategy
    """
    # Show stock information
    show_stock_info(results.get('stock_info', {}))
    
    # Show volatility metrics if available
    if 'volatility_metrics' in results:
        show_volatility_metrics(results['volatility_metrics'])
    
    # Show strategy-specific results
    if strategy_type.lower() == 'cash_secured_put':
        show_cash_secured_puts(results.get('opportunities', []))
    elif strategy_type.lower() == 'covered_call':
        show_covered_calls(results.get('opportunities', []))
    
    # Show AI analysis if available
    if 'ai_analysis' in results:
        print("\n" + "=" * 80)
        print("AI Analysis")
        print("=" * 80)
        print(results['ai_analysis'])
        print("\n")


def show_error(error_message: str):
    """
    Display an error message to the user.
    
    Args:
        error_message: Error message to display
    """
    print("\n" + "!" * 80)
    print(f"ERROR: {error_message}")
    print("!" * 80 + "\n")