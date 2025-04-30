"""
Tests for the data fetcher module.
"""

import unittest
from unittest.mock import patch, MagicMock
from options_analyzer.data import fetcher


class TestFetcher(unittest.TestCase):
    """Test cases for the fetcher module."""
    
    @patch('yfinance.Ticker')
    def test_get_stock_info(self, mock_ticker):
        """Test getting stock information."""
        # Setup mock
        mock_ticker_instance = MagicMock()
        mock_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.info = {
            'shortName': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'currentPrice': 150.0,
            'previousClose': 149.0,
            'open': 149.5,
            'dayLow': 148.0,
            'dayHigh': 151.0,
            'fiftyTwoWeekLow': 120.0,
            'fiftyTwoWeekHigh': 180.0,
            'volume': 80000000,
            'averageVolume': 90000000,
            'marketCap': 2400000000000,
            'beta': 1.2,
            'trailingPE': 25.0,
            'trailingEps': 6.0,
            'dividendRate': 0.88,
            'dividendYield': 0.006,
        }
        
        # Call the function
        result = fetcher.get_stock_info('AAPL')
        
        # Assertions
        mock_ticker.assert_called_once_with('AAPL')
        self.assertEqual(result['symbol'], 'AAPL')
        self.assertEqual(result['name'], 'Apple Inc.')
        self.assertEqual(result['current_price'], 150.0)
        self.assertEqual(result['sector'], 'Technology')
    
    @patch('yfinance.Ticker')
    def test_get_options_chain(self, mock_ticker):
        """Test getting options chain data."""
        # Setup mock
        mock_ticker_instance = MagicMock()
        mock_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.options = ['2023-12-15', '2023-12-22']
        
        mock_option_chain = MagicMock()
        mock_ticker_instance.option_chain.return_value = mock_option_chain
        
        # Mock options data
        mock_option_chain.calls = MagicMock()
        mock_option_chain.puts = MagicMock()
        
        mock_option_chain.calls.to_dict.return_value = [
            {'strike': 150, 'bid': 5.0, 'ask': 5.2, 'impliedVolatility': 0.3}
        ]
        mock_option_chain.puts.to_dict.return_value = [
            {'strike': 145, 'bid': 3.0, 'ask': 3.2, 'impliedVolatility': 0.32}
        ]
        
        # Call the function
        result = fetcher.get_options_chain('AAPL', '2023-12-15')
        
        # Assertions
        mock_ticker.assert_called_once_with('AAPL')
        mock_ticker_instance.option_chain.assert_called_once_with('2023-12-15')
        self.assertEqual(result['expiration_date'], '2023-12-15')
        self.assertEqual(len(result['calls']), 1)
        self.assertEqual(len(result['puts']), 1)
        self.assertEqual(result['calls'][0]['strike'], 150)
        self.assertEqual(result['puts'][0]['strike'], 145)


if __name__ == '__main__':
    unittest.main()