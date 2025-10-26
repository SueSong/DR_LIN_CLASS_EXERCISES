"""
LLM-Powered Trading Agent
Integrates with OpenAI/Anthropic for intelligent trading decisions
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime
import os

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# LLM imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from tools.schemas import (
    RecommendationInput, RecommendationOutput, TradingRecommendation,
    TransactionType, ToolStatus
)
from tools.registry import (
    register_trading_tool, ToolCategory, ToolPermission, PermissionLevel
)
from tools.reliability import with_retry, TradingRetryConfigs

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class TradingLLMAgent:
    """LLM-powered trading agent for market analysis and recommendations"""
    
    def __init__(self, provider: str = "openai", model: str = None):
        self.provider = provider.lower()
        self.model = model
        
        if self.provider == "openai" and OPENAI_AVAILABLE:
            self.client = openai.AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.model = model or "gpt-4-turbo-preview"
        elif self.provider == "anthropic" and ANTHROPIC_AVAILABLE:
            self.client = anthropic.AsyncAnthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            self.model = model or "claude-3-sonnet-20240229"
        else:
            logger.warning(f"LLM provider {provider} not available, using mock responses")
            self.client = None
            self.model = "mock"
    
    async def analyze_market_and_recommend(
        self,
        market_data: Dict[str, Any],
        portfolio_data: Dict[str, Any],
        cash_balance: Decimal,
        risk_tolerance: str = "moderate",
        investment_goals: List[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze market conditions and portfolio to generate trading recommendations
        """
        
        with tracer.start_as_current_span("llm_market_analysis") as span:
            span.set_attribute("llm.provider", self.provider)
            span.set_attribute("llm.model", self.model)
            span.set_attribute("portfolio.positions", len(portfolio_data.get("positions", [])))
            span.set_attribute("cash_balance", float(cash_balance))
            
            try:
                # Prepare context for LLM
                context = self._prepare_analysis_context(
                    market_data, portfolio_data, cash_balance, risk_tolerance, investment_goals
                )
                
                # Get LLM analysis
                if self.client:
                    analysis = await self._get_llm_analysis(context)
                else:
                    analysis = self._get_mock_analysis(context)
                
                # Parse recommendations
                recommendations = self._parse_recommendations(analysis, cash_balance)
                
                span.set_attribute("recommendations.count", len(recommendations))
                span.set_attribute("status", "success")
                
                return {
                    "status": ToolStatus.SUCCESS,
                    "recommendations": recommendations,
                    "market_analysis": analysis.get("market_analysis", ""),
                    "portfolio_analysis": analysis.get("portfolio_analysis", ""),
                    "risk_assessment": analysis.get("risk_assessment", ""),
                    "cash_allocation": analysis.get("recommended_cash_allocation", Decimal("10")),
                    "timestamp": datetime.utcnow()
                }
                
            except Exception as e:
                span.set_attribute("status", "error")
                span.set_attribute("error.message", str(e))
                span.set_status(Status(StatusCode.ERROR, str(e)))
                
                logger.error(f"LLM analysis failed: {e}")
                return {
                    "status": ToolStatus.ERROR,
                    "error_message": str(e),
                    "recommendations": [],
                    "timestamp": datetime.utcnow()
                }
    
    def _prepare_analysis_context(
        self,
        market_data: Dict[str, Any],
        portfolio_data: Dict[str, Any],
        cash_balance: Decimal,
        risk_tolerance: str,
        investment_goals: List[str]
    ) -> Dict[str, Any]:
        """Prepare context data for LLM analysis"""
        
        return {
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "market_data": market_data,
            "portfolio": {
                "positions": portfolio_data.get("positions", []),
                "total_value": portfolio_data.get("total_value", 0),
                "cash_balance": float(cash_balance),
                "cash_percentage": float(cash_balance / (portfolio_data.get("total_value", cash_balance) or cash_balance) * 100)
            },
            "risk_tolerance": risk_tolerance,
            "investment_goals": investment_goals or ["growth", "diversification"],
            "constraints": {
                "target_cash_percentage": 10,  # Keep 10% cash
                "max_position_size": 20,  # Max 20% in any single stock
                "min_trade_amount": 1000  # Minimum $1000 per trade
            }
        }
    
    async def _get_llm_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get analysis from LLM provider"""
        
        system_prompt = """You are an expert financial advisor and portfolio manager. 
        Analyze the provided market data and portfolio information to make intelligent trading recommendations.
        
        Your analysis should include:
        1. Market Analysis: Current market conditions and trends
        2. Portfolio Analysis: Current portfolio strengths and weaknesses
        3. Risk Assessment: Risk factors and mitigation strategies
        4. Trading Recommendations: Specific buy/sell recommendations with reasoning
        
        For each recommendation, provide:
        - Symbol
        - Action (BUY or SELL)
        - Amount or quantity
        - Reasoning
        - Confidence score (0.0 to 1.0)
        - Priority (1-10, where 1 is highest priority)
        
        Respond in JSON format with the following structure:
        {
            "market_analysis": "string",
            "portfolio_analysis": "string", 
            "risk_assessment": "string",
            "recommended_cash_allocation": number,
            "recommendations": [
                {
                    "symbol": "string",
                    "action": "BUY|SELL",
                    "amount": number,
                    "reasoning": "string",
                    "confidence": number,
                    "priority": number
                }
            ]
        }
        """
        
        user_prompt = f"""
        Please analyze the following market and portfolio data:
        
        {json.dumps(context, indent=2, default=str)}
        
        Provide your analysis and trading recommendations in the specified JSON format.
        """
        
        if self.provider == "openai":
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent financial advice
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
        elif self.provider == "anthropic":
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            content = response.content[0].text
        
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
        # Parse JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("Could not parse LLM response as JSON")
    
    def _get_mock_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock analysis for testing when LLM is not available"""
        
        portfolio_value = context["portfolio"]["total_value"]
        cash_balance = context["portfolio"]["cash_balance"]
        cash_percentage = context["portfolio"]["cash_percentage"]
        
        # Mock recommendations based on simple rules
        recommendations = []
        
        # If cash percentage is too high, recommend buying
        if cash_percentage > 15:
            recommendations.append({
                "symbol": "AAPL",
                "action": "BUY",
                "amount": min(5000, cash_balance * 0.1),
                "reasoning": "Strong technology stock with consistent growth. Cash allocation is high, good time to invest.",
                "confidence": 0.8,
                "priority": 1
            })
        
        # If cash percentage is too low, recommend selling
        if cash_percentage < 5:
            recommendations.append({
                "symbol": "TSLA",
                "action": "SELL",
                "amount": 3000,
                "reasoning": "High volatility stock, selling to increase cash reserves for stability.",
                "confidence": 0.7,
                "priority": 2
            })
        
        return {
            "market_analysis": "Market showing mixed signals with technology stocks performing well. Overall sentiment is cautiously optimistic.",
            "portfolio_analysis": f"Portfolio is currently valued at ${portfolio_value:,.2f} with {cash_percentage:.1f}% in cash. Diversification could be improved.",
            "risk_assessment": "Moderate risk level. Consider rebalancing to maintain target cash allocation of 10%.",
            "recommended_cash_allocation": 10.0,
            "recommendations": recommendations
        }
    
    def _parse_recommendations(self, analysis: Dict[str, Any], cash_balance: Decimal) -> List[Dict[str, Any]]:
        """Parse and validate LLM recommendations"""
        
        recommendations = []
        raw_recommendations = analysis.get("recommendations", [])
        
        for i, rec in enumerate(raw_recommendations):
            try:
                # Validate and convert recommendation
                symbol = rec.get("symbol", "").upper()
                action = rec.get("action", "").upper()
                amount = rec.get("amount", 0)
                quantity = rec.get("quantity")
                
                if not symbol or action not in ["BUY", "SELL"]:
                    continue
                
                # Ensure we have either amount or quantity
                if not amount and not quantity:
                    continue
                
                recommendation = TradingRecommendation(
                    symbol=symbol,
                    action=TransactionType(action),
                    amount=Decimal(str(amount)) if amount else None,
                    quantity=Decimal(str(quantity)) if quantity else None,
                    reasoning=rec.get("reasoning", "No reasoning provided"),
                    confidence=Decimal(str(min(1.0, max(0.0, rec.get("confidence", 0.5))))),
                    priority=max(1, min(10, rec.get("priority", 5)))
                )
                
                recommendations.append(recommendation.dict())
                
            except Exception as e:
                logger.warning(f"Failed to parse recommendation {i}: {e}")
                continue
        
        # Sort by priority
        recommendations.sort(key=lambda x: x["priority"])
        
        return recommendations

# Global LLM agent instance
_global_llm_agent = None

def get_llm_agent() -> TradingLLMAgent:
    """Get global LLM agent instance"""
    global _global_llm_agent
    if _global_llm_agent is None:
        provider = os.getenv("LLM_PROVIDER", "openai")
        _global_llm_agent = TradingLLMAgent(provider=provider)
    return _global_llm_agent

# Register as a tool in the registry
@register_trading_tool(
    name="get_trading_recommendations",
    description="Get AI-powered trading recommendations based on market analysis",
    category=ToolCategory.ANALYSIS,
    input_schema=RecommendationInput,
    output_schema=RecommendationOutput,
    permission=ToolPermission(
        level=PermissionLevel.TRADER,
        rate_limit_per_minute=5,  # Limited LLM calls
        sandbox_enabled=True
    ),
    tags=["ai", "recommendations", "analysis", "llm"],
    version="1.0.0"
)
@with_retry(TradingRetryConfigs.llm_request())
async def get_trading_recommendations(input_data: Dict[str, Any], trace_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get AI-powered trading recommendations
    Demonstrates Exercise 6 (Full Agent Flow)
    """
    
    with tracer.start_as_current_span("trading_recommendations_tool") as span:
        span.set_attribute("tool.name", "get_trading_recommendations")
        
        try:
            llm_agent = get_llm_agent()
            
            market_data = input_data.get("market_data", {})
            portfolio_data = input_data.get("portfolio_data", {})
            cash_balance = Decimal(str(input_data.get("cash_balance", 0)))
            risk_tolerance = input_data.get("risk_tolerance", "moderate")
            investment_goals = input_data.get("investment_goals", [])
            
            # Get recommendations from LLM
            result = await llm_agent.analyze_market_and_recommend(
                market_data=market_data,
                portfolio_data=portfolio_data,
                cash_balance=cash_balance,
                risk_tolerance=risk_tolerance,
                investment_goals=investment_goals
            )
            
            span.set_attribute("recommendations.count", len(result.get("recommendations", [])))
            span.set_attribute("status", "success")
            
            return result
            
        except Exception as e:
            span.set_attribute("status", "error")
            span.set_attribute("error.message", str(e))
            span.set_status(Status(StatusCode.ERROR, str(e)))
            
            logger.error(f"Trading recommendations tool failed: {e}")
            return {
                "status": ToolStatus.ERROR,
                "error_message": str(e),
                "recommendations": [],
                "timestamp": datetime.utcnow()
            }
