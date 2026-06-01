#!/usr/bin/env python3
"""
Options Analyzer Tool - Entry Point

A command-line tool for analyzing options strategies for stocks using yfinance data.
"""

import argparse
import sys
from typing import Dict, Any
import datetime as dt # Ensure datetime is imported
import os
from dotenv import load_dotenv

from options_analyzer import core
from options_analyzer.utils import config_manager
from options_analyzer.data import fetcher
from options_analyzer.analysis import strategies, volatility
from options_analyzer.ai import gemini_interface

load_dotenv()


def parse_arguments():
    """Parse command-line arguments."""
    # Load default values from config
    config = config_manager.load_config()
    default_ticker = config.get('default_ticker', 'SPY')
    default_strategy = config.get('default_strategy', 'cash_secured_put')
    default_min_premium = config.get('min_premium_percent', 0.5)
    default_max_days = config.get('max_days_to_expiry', 45)
    
    parser = argparse.ArgumentParser(
        description='Options Analyzer Tool - Analyze options strategies for stocks'
    )
    
    parser.add_argument(
        'ticker',
        nargs='?',
        default=default_ticker,
        help=f'Stock ticker symbol (default: {default_ticker})'
    )
    
    parser.add_argument(
        '-s', '--strategy',
        choices=['cash_secured_put', 'covered_call'],
        default=default_strategy,
        help=f'Options strategy to analyze (default: {default_strategy})'
    )
    
    parser.add_argument(
        '-d', '--days',
        type=int,
        default=default_max_days,
        help=f'Maximum days to expiration (default: {default_max_days})'
    )
    
    parser.add_argument(
        '-p', '--premium',
        type=float,
        default=default_min_premium,
        # %% so argparse's help formatting (which does help % params) does not choke on the percent sign
        help=f'Minimum annualized premium percentage (default: {default_min_premium}%%)'
    )
    
    parser.add_argument(
        '-e', '--expiration',
        help='Specific expiration date (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Disable AI analysis'
    )

    parser.add_argument(
        '--chart',
        action='store_true',
        help='Save a visual report (payoff, strike screen, expected move) as a PNG'
    )

    parser.add_argument(
        '--chart-dir',
        default='charts',
        help='Directory for saved chart images (default: charts)'
    )

    return parser.parse_args()


def run_analysis(args):
    """Run the options analysis based on command-line arguments."""
    try:
        # Get stock information
        stock_info = fetcher.get_stock_info(args.ticker)
        
        # Get historical data for volatility calculations
        historical_data = fetcher.get_historical_data(args.ticker, period='1y')
        
        # --- New Expiration Logic ---
        expirations = fetcher.get_available_expirations(args.ticker)
        if not expirations:
            raise ValueError(f"No options expiration dates found for {args.ticker}")

        today_date = dt.datetime.now().date()
        chosen_expiration = None

        if args.expiration:
            # User provided a specific expiration date
            try:
                exp_date = dt.datetime.strptime(args.expiration, '%Y-%m-%d').date()
                if exp_date > today_date:
                    if args.expiration in expirations:
                         chosen_expiration = args.expiration
                    else:
                         print(f"Warning: Provided expiration {args.expiration} is not listed for {args.ticker}. Checking suitability...")
                         # Allow if date is valid format and in the future, even if not listed (might be weekend/holiday issue)
                         chosen_expiration = args.expiration 
                else:
                    print(f"Warning: Provided expiration date {args.expiration} is not in the future.")
            except ValueError:
                print(f"Warning: Invalid format for expiration date '{args.expiration}'. Expected YYYY-MM-DD.")
            
            if not chosen_expiration:
                 print(f"Falling back to nearest suitable expiration within {args.days} days.")

        if not chosen_expiration: # Default logic: Find earliest expiration > 0 and <= args.days DTE
            suitable_expirations = []
            for exp_str in expirations:
                try:
                    exp_date = dt.datetime.strptime(exp_str, '%Y-%m-%d').date()
                    days_to_exp = (exp_date - today_date).days
                    # Filter for DTE > 0 and <= args.days (inclusive)
                    if 0 < days_to_exp <= args.days: # Use args.days as upper bound, remove 15 day minimum
                        suitable_expirations.append((days_to_exp, exp_str))
                except ValueError:
                    continue # Ignore invalid date formats from fetcher

            if not suitable_expirations:
                # Update error message to reflect the new range (0 to args.days)
                raise ValueError(f"No suitable expiration dates found for {args.ticker} between 1 and {args.days} days.")

            # Sort by days to expiration (ascending)
            suitable_expirations.sort()
            chosen_expiration = suitable_expirations[0][1] # Select the earliest suitable date

        print(f"Analyzing options for {args.ticker} expiring on {chosen_expiration}")

        # Fetch options chain ONCE with the determined expiration
        options_data = fetcher.get_options_chain(args.ticker, chosen_expiration)
        if not options_data or (not options_data.get('calls') and not options_data.get('puts')):
             raise ValueError(f"Could not fetch valid options data for {args.ticker} on {chosen_expiration}.")
        # --- End New Expiration Logic ---

        # Calculate volatility metrics
        hist_vol = volatility.calculate_historical_volatility(historical_data)
        # Ensure options_data is not None before accessing it for implied vol
        implied_vol = 0.0
        if options_data:
             implied_vol = volatility.get_atm_implied_volatility(options_data, stock_info['current_price'])
        else:
             print("Warning: Could not fetch options data to calculate implied volatility.")

        volatility_metrics = {
            'historical_volatility': hist_vol,
            'implied_volatility': implied_vol,
            'expected_move_7d': volatility.calculate_expected_move(
                stock_info['current_price'], implied_vol, 7
            ),
            'expected_move_percent_7d': (volatility.calculate_expected_move(
                stock_info['current_price'], implied_vol, 7
            ) / stock_info['current_price']) * 100 if stock_info['current_price'] else 0,
            'expected_move_30d': volatility.calculate_expected_move(
                stock_info['current_price'], implied_vol, 30
            ),
            'expected_move_percent_30d': (volatility.calculate_expected_move(
                stock_info['current_price'], implied_vol, 30
            ) / stock_info['current_price']) * 100 if stock_info['current_price'] else 0
        }
        
        # Analyze strategy
        strategy_results = {}
        if args.strategy.lower() == 'cash_secured_put':
            opportunities = strategies.analyze_cash_secured_puts(
                stock_info,
                options_data,
                min_premium_percent=args.premium,
                max_days_to_expiry=args.days
            )
            strategy_results = {
                'stock_info': stock_info,
                'volatility_metrics': volatility_metrics,
                'opportunities': opportunities
            }
        elif args.strategy.lower() == 'covered_call':
            opportunities = strategies.analyze_covered_calls(
                stock_info,
                options_data,
                min_premium_percent=args.premium,
                max_days_to_expiry=args.days
            )
            strategy_results = {
                'stock_info': stock_info,
                'volatility_metrics': volatility_metrics,
                'opportunities': opportunities
            }
        
        # Add AI analysis if enabled
        if not args.no_ai and config_manager.load_config().get('show_ai_analysis', True):
            try:
                ai_analysis = gemini_interface.analyze_option_strategy(
                    stock_info,
                    strategy_results.get('opportunities', []),
                    args.strategy
                )
                strategy_results['ai_analysis'] = ai_analysis
            except Exception as e:
                print(f"AI analysis failed: {str(e)}")
        
        # Display results
        # Ensure core.run_analysis_and_display exists and handles potential None for opportunities
        core.run_analysis_and_display(args.ticker, args.strategy, **strategy_results)

        # Save a visual report if requested
        if args.chart:
            if strategy_results.get('opportunities'):
                from options_analyzer.viz import charts
                chart_path = charts.build_report(
                    args.ticker, args.strategy, strategy_results,
                    chosen_expiration, out_dir=args.chart_dir
                )
                print(f"Saved chart report to {chart_path}")
            else:
                print("No opportunities found, skipping chart.")

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


def main():
    """Main entry point."""
    args = parse_arguments()
    sys.exit(run_analysis(args))


if __name__ == "__main__":
    main()