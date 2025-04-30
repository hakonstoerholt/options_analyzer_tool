"""
Prompt templates for the Gemini API.
"""

def get_prompt_template(template_type: str) -> str:
    """
    Get a prompt template for the Gemini API.
    
    Args:
        template_type: Type of prompt template to retrieve
        
    Returns:
        Prompt template as a string
    """
    templates = {
        'cash_secured_put': '''
            You are a professional options trader and financial advisor.
            
            I'm analyzing cash secured puts for {stock_info['name']} ({stock_info['symbol']}) which is currently trading at ${stock_info['current_price']:.2f}.
            
            Here are the top opportunities I've identified:
            {strategy_results}
            
            Additional context: {additional_context}
            
            Please provide me with:
            1. A brief analysis of the stock's current situation and whether selling puts makes sense right now
            2. An assessment of the risk/reward for the top opportunities
            3. Any specific strikes/expirations that look particularly attractive and why
            4. Considerations about implied volatility compared to historical norms if possible
            5. Any key risks or things to watch out for
            
            Keep your answer concise but informative. Use plain language that an intermediate options trader would understand.
        ''',
        
        'covered_call': '''
            You are a professional options trader and financial advisor.
            
            I'm analyzing covered calls for {stock_info['name']} ({stock_info['symbol']}) which is currently trading at ${stock_info['current_price']:.2f}.
            
            Here are the top opportunities I've identified:
            {strategy_results}
            
            Additional context: {additional_context}
            
            Please provide me with:
            1. A brief analysis of the stock's current situation and whether selling covered calls makes sense right now
            2. An assessment of the risk/reward for the top opportunities
            3. Any specific strikes/expirations that look particularly attractive and why
            4. Considerations about potential missed upside vs. premium collected
            5. Any key risks or things to watch out for
            
            Keep your answer concise but informative. Use plain language that an intermediate options trader would understand.
        ''',
        
        'strategy_recommendation': '''
            You are a professional options trader and financial advisor.
            
            I'm looking at {stock_info['name']} ({stock_info['symbol']}) which is currently trading at ${stock_info['current_price']:.2f}.
            
            Key information about the stock:
            - Sector: {stock_info['sector']}
            - Industry: {stock_info['industry']}
            - Beta: {stock_info['beta']}
            - P/E Ratio: {stock_info['pe_ratio']}
            
            Volatility metrics:
            {volatility_metrics}
            
            Based on this information, please recommend:
            1. 2-3 options strategies that might be appropriate right now and why
            2. For each strategy, what strikes and expirations might make sense
            3. Key risks or conditions that might affect these strategies
            
            Keep your answer concise but informative. Use plain language that an intermediate options trader would understand.
        '''
    }
    
    return templates.get(template_type, "No template found for the specified type.")