"""
Functions to interact with the Google Gemini API for options analysis insights.
"""

import os
import json
from typing import Dict, List, Any

from options_analyzer.utils.config_manager import load_config
from options_analyzer.ai.prompts import get_prompt_template

try:
    import google.generativeai as genai
except ImportError:
    genai = None


def setup_gemini_api():
    """
    Set up the Gemini API with the API key.
    """
    if genai is None:
        raise ImportError("Google Generative AI package not installed. Run 'pip install google-generativeai'")
    
    config = load_config()
    api_key = config.get('gemini_api_key', os.getenv('GEMINI_API_KEY'))
    
    if not api_key:
        raise ValueError("Gemini API key not found. Please add it to your config file or .env file.")
    
    genai.configure(api_key=api_key)


def get_available_models():
    """
    Get a list of available Gemini models.
    
    Returns:
        List of model names
    """
    try:
        setup_gemini_api()
        models = genai.list_models()
        gemini_models = [model.name for model in models if 'gemini' in model.name]
        return gemini_models
    except Exception as e:
        print(f"Error retrieving Gemini models: {str(e)}")
        return []


def analyze_option_strategy(
    stock_info: Dict[str, Any],
    strategy_results: List[Dict[str, Any]],
    strategy_type: str,
    additional_context: str = ""
) -> str:
    """
    Get AI-generated insights about an options strategy.
    
    Args:
        stock_info: Dictionary containing stock information
        strategy_results: List of strategy analysis results
        strategy_type: Type of option strategy analyzed
        additional_context: Any additional context to include in the prompt
        
    Returns:
        AI-generated analysis as a string
    """
    try:
        setup_gemini_api()
        
        # Get the appropriate prompt template
        prompt_template = get_prompt_template(strategy_type)
        
        # Safely convert objects to strings to avoid formatting issues
        stock_info_str = json.dumps({
            "name": stock_info.get("name", "Unknown"),
            "symbol": stock_info.get("symbol", "Unknown"),
            "current_price": stock_info.get("current_price", 0),
            "sector": stock_info.get("sector", "Unknown"),
            "industry": stock_info.get("industry", "Unknown")
        })
        
        # Format results to include only the most important fields and limit to top 5
        simplified_results = []
        for result in strategy_results[:5]:
            simplified_results.append({
                "strike": result.get("strike", 0),
                "premium": result.get("premium", 0),
                "annualized_return": result.get("annualized_return", 0),
                "days_to_expiry": result.get("days_to_expiry", 0),
                "probability_otm": result.get("probability_otm", 0)
            })
        
        strategy_results_str = json.dumps(simplified_results)
        
        # Fill in the prompt template with JSON data
        prompt = f"""
        You are a professional options trader and financial advisor.

        I'm analyzing {strategy_type} for {stock_info.get('name', 'Unknown')} ({stock_info.get('symbol', 'Unknown')}) which is currently trading at ${stock_info.get('current_price', 0):.2f}.

        Here are the top opportunities I've identified:
        {strategy_results_str}

        Additional context: {additional_context}

        Please provide me with:
        1. A brief analysis of the stock's current situation and whether this strategy makes sense right now
        2. An assessment of the risk/reward for the top opportunities
        3. Any specific strikes/expirations that look particularly attractive and why
        4. Considerations about implied volatility compared to historical norms if possible
        5. Any key risks or things to watch out for

        Keep your answer concise but informative. Use plain language that an intermediate options trader would understand.
        """
        
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Generate the analysis
        response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        return f"Error generating AI analysis: {str(e)}"


def recommend_strategy(stock_info: Dict[str, Any], volatility_metrics: Dict[str, Any]) -> str:
    """
    Get AI recommendation on which options strategy might be suitable.
    
    Args:
        stock_info: Dictionary containing stock information
        volatility_metrics: Dictionary with volatility metrics
        
    Returns:
        AI-generated recommendation as a string
    """
    try:
        setup_gemini_api()
        
        # Convert objects to strings to avoid formatting issues
        stock_info_str = json.dumps({
            "name": stock_info.get("name", "Unknown"),
            "symbol": stock_info.get("symbol", "Unknown"),
            "current_price": stock_info.get("current_price", 0),
            "sector": stock_info.get("sector", "Unknown"),
            "industry": stock_info.get("industry", "Unknown"),
            "beta": stock_info.get("beta", 0),
            "pe_ratio": stock_info.get("pe_ratio", 0)
        })
        
        volatility_metrics_str = json.dumps(volatility_metrics)
        
        # Create a simpler prompt
        prompt = f"""
        You are a professional options trader and financial advisor.

        I'm looking at {stock_info.get('name', 'Unknown')} ({stock_info.get('symbol', 'Unknown')}) which is currently trading at ${stock_info.get('current_price', 0):.2f}.

        Key information about the stock:
        - Sector: {stock_info.get('sector', 'Unknown')}
        - Industry: {stock_info.get('industry', 'Unknown')}
        - Beta: {stock_info.get('beta', 0)}
        - P/E Ratio: {stock_info.get('pe_ratio', 0)}

        Volatility metrics:
        {volatility_metrics_str}

        Based on this information, please recommend:
        1. 2-3 options strategies that might be appropriate right now and why
        2. For each strategy, what strikes and expirations might make sense
        3. Key risks or conditions that might affect these strategies

        Keep your answer concise but informative. Use plain language that an intermediate options trader would understand.
        """
        
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Generate the recommendation
        response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        return f"Error generating strategy recommendation: {str(e)}"