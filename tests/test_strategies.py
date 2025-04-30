"""
Tests for the options strategies module.
"""

import unittest
from unittest.mock import patch, MagicMock
import datetime as dt
from options_analyzer.analysis import strategies


class TestStrategies(unittest.TestCase):
    """Test cases for the strategies module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample stock info
        self.stock_info = {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'current_price': 150.0,
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'previous_close': 149.0,
            'open': 149.5,
            'day_low': 148.0,
            'day_high': 151.0,
            'fifty_two_week_low': 120.0,
            'fifty_two_week_high': 180.0,
            'volume': 80000000,
            'avg_volume': 90000000,
            'market_cap': 2400000000000,
            'beta': 1.2,
            'pe_ratio': 25.0,
            'eps': 6.0,
            'dividend_rate': 0.88,
            'dividend_yield': 0.006,
        }
        
        # Get today's date
        today = dt.datetime.now().date()
        
        # Create expiration date 30 days from today
        expiry = today + dt.timedelta(days=30)
        expiry_str = expiry.strftime('%Y-%m-%d')
        
        # Sample options data
        self.options_data = {
            'expiration_date': expiry_str,
            'calls': [
                {
                    'strike': 155.0,
                    'bid': 4.0,
                    'ask': 4.2,
                    'impliedVolatility': 0.3,
                    'volume': 1000,
                    'openInterest': 5000
                },
                {
                    'strike': 160.0,
                    'bid': 2.5,
                    'ask': 2.7,
                    'impliedVolatility': 0.32,
                    'volume': 800,
                    'openInterest': 4000
                }
            ],
            'puts': [
                {
                    'strike': 145.0,
                    'bid': 3.0,
                    'ask': 3.2,
                    'impliedVolatility': 0.33,
                    'volume': 900,
                    'openInterest': 4500
                },
                {
                    'strike': 140.0,
                    'bid': 1.8,
                    'ask': 2.0,
                    'impliedVolatility': 0.35,
                    'volume': 700,
                    'openInterest': 3500
                }
            ]
        }
    
    def test_analyze_cash_secured_puts(self):
        """Test analyzing cash secured puts strategy."""
        # Call the function
        result = strategies.analyze_cash_secured_puts(
            self.stock_info,
            self.options_data,
            min_premium_percent=0.5,
            max_days_to_expiry=45
        )
        
        # Assertions
        self.assertIsInstance(result, list)
        if result:  # If any results match our criteria
            self.assertIn('strike', result[0])
            self.assertIn('premium', result[0])
            self.assertIn('annualized_return', result[0])
            self.assertIn('probability_otm', result[0])
            self.assertIn('effective_purchase_price', result[0]) # Check for new metric
            self.assertTrue(0 <= result[0]['probability_otm'] <= 100) # Check probability bounds
            
            # Check if sorted by annualized return (descending)
            if len(result) > 1:
                self.assertGreaterEqual(result[0]['annualized_return'], result[1]['annualized_return'])
    
    def test_analyze_covered_calls(self):
        """Test analyzing covered calls strategy."""
        # Call the function
        result = strategies.analyze_covered_calls(
            self.stock_info,
            self.options_data,
            shares_owned=100,
            min_premium_percent=0.5,
            max_days_to_expiry=45
        )
        
        # Assertions
        self.assertIsInstance(result, list)
        if result:  # If any results match our criteria
            self.assertIn('strike', result[0])
            self.assertIn('premium', result[0])
            self.assertIn('annualized_return', result[0])
            self.assertIn('potential_profit_if_called', result[0])
            self.assertTrue(0 <= result[0]['probability_otm'] <= 100) # Check probability bounds
            
            # Check if sorted by annualized return (descending)
            if len(result) > 1:
                self.assertGreaterEqual(result[0]['annualized_return'], result[1]['annualized_return'])


if __name__ == '__main__':
    unittest.main()