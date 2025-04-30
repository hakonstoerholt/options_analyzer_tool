"""
Core orchestration module for the Options Analyzer tool.
Centralizes the workflow and coordinates between different modules.
"""

from options_analyzer.data import fetcher
from options_analyzer.analysis import strategies
from options_analyzer.ui import console_display
from options_analyzer.utils import config_manager


def analyze_option_strategy(ticker: str, strategy_type: str, **kwargs):
    """
    Main function to analyze an options strategy for a given ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        strategy_type: Type of options strategy (e.g., 'cash_secured_put')
        **kwargs: Additional parameters for the specific strategy
        
    Returns:
        Analysis results for the requested strategy
    """
    # Check if stock_info and options_data are already provided
    stock_info = kwargs.pop('stock_info', None)
    options_data = kwargs.pop('options_data', None)
    
    # If not provided, fetch them
    if stock_info is None:
        stock_info = fetcher.get_stock_info(ticker)
    
    if options_data is None:
        options_data = fetcher.get_options_chain(ticker)
    
    # Perform analysis based on strategy type
    if strategy_type.lower() == 'cash_secured_put':
        results = strategies.analyze_cash_secured_puts(
            stock_info, 
            options_data,
            **kwargs
        )
        return {'stock_info': stock_info, 'opportunities': results}
    elif strategy_type.lower() == 'covered_call':
        results = strategies.analyze_covered_calls(
            stock_info, 
            options_data,
            **kwargs
        )
        return {'stock_info': stock_info, 'opportunities': results}
    else:
        raise ValueError(f"Strategy type '{strategy_type}' not supported")


def run_analysis_and_display(ticker: str, strategy_type: str, **kwargs):
    """
    Run the analysis and display results in the console.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        strategy_type: Type of options strategy (e.g., 'cash_secured_put')
        **kwargs: Additional parameters for the specific strategy
    """
    try:
        # Check if we're receiving pre-computed results
        if 'opportunities' in kwargs and 'stock_info' in kwargs:
            # We already have the analysis results, just display them
            console_display.show_analysis_results(kwargs, strategy_type)
        else:
            # We need to perform the analysis
            results = analyze_option_strategy(ticker, strategy_type, **kwargs)
            console_display.show_analysis_results(results, strategy_type)
    except Exception as e:
        console_display.show_error(f"Analysis failed: {str(e)}")