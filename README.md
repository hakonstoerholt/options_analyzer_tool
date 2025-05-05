# Options Analyzer Tool

A command-line tool for analyzing stock options strategies using data from Yahoo Finance.

## Features

- Analyze various options strategies:
  - Cash Secured Puts
  - Covered Calls
  - More strategies coming soon
- Calculate key metrics:
  - Annualized returns
  - Probability of profit
  - Risk/reward ratios
- View volatility metrics:
  - Historical and implied volatility
  - IV Rank
  - Expected price moves
- Get AI-powered analysis using Google's Gemini API

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/hakonstoerholt/options_analyzer_tool.git
   cd options_analyzer_tool
   ```

2. Create and activate a virtual environment (recommended):
   ```
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your API keys (for AI analysis):
   - Create a `.env` file in the root directory
   - Add your Google Gemini API key: `GEMINI_API_KEY=your_api_key_here`
   - Or add it to `config/settings.yaml`

## Usage

### Basic Usage

```
python main.py TICKER [options]
```

For example:
```
python main.py AAPL
```

This will analyze cash secured puts for Apple Inc. using the default settings.

### Options

- `-s`, `--strategy`: Strategy to analyze (`cash_secured_put` or `covered_call`)
- `-d`, `--days`: Maximum days to expiration
- `-p`, `--premium`: Minimum annualized premium percentage
- `-e`, `--expiration`: Specific expiration date (YYYY-MM-DD format)
- `--no-ai`: Disable AI analysis

### Examples

Analyze covered calls for Tesla with minimum 1% annualized return:
```
python main.py TSLA -s covered_call -p 1.0
```

Analyze cash secured puts for SPY with a specific expiration date:
```
python main.py SPY -e 2023-12-15
```

## Configuration

You can customize default settings in the `config/settings.yaml` file:

- `min_premium_percent`: Minimum annualized premium percentage
- `max_days_to_expiry`: Maximum days to expiration
- `show_ai_analysis`: Whether to show AI analysis
- `default_strategy`: Default strategy to analyze
- `default_ticker`: Default ticker symbol

## Future Enhancements

- Additional options strategies (spreads, iron condors, etc.)
- Technical analysis integration
- Broker API integration for real-time portfolio analysis
- Web interface

## License

[MIT License](LICENSE)

## Disclaimer

This tool is for educational and informational purposes only. It is not financial advice. Always do your own research and consider your financial situation before trading options.
