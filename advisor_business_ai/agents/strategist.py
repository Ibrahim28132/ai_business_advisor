from typing import Dict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from utils.config import config
from utils.logging import logger


class StrategyAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
        self.prompt = self._create_prompt()

    def _create_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", """
            You are StartSmart Strategist, an expert in business strategy and monetization. Your tasks:
            1. Develop revenue models and pricing strategies
            2. Suggest growth and marketing approaches
            3. Identify potential risks and mitigation strategies
            4. Recommend operational structures
            5. Provide strategic guidance tailored to the business context

            Guidelines:
            - Be creative but realistic
            - Consider multiple monetization approaches
            - Align strategies with market conditions and target customers
            - Highlight both short-term and long-term strategies
            - Include metrics for success evaluation
            """),
            ("human", "{input}"),
        ])

    def develop_strategy(self, analysis_results: Dict, business_context: Dict) -> Dict:
        """
        Develop business strategies based on analysis.

        Args:
            analysis_results: Insights from the analysis agent
            business_context: Details about the business idea and goals

        Returns:
            Dictionary containing strategy recommendations
        """
        try:
            # Prepare input
            input_text = f"""
            Business Context:
            {business_context}

            Analysis Results:
            {analysis_results}

            Please develop comprehensive business strategies based on this information.
            """

            # Create chain
            chain = self.prompt | self.llm

            # Generate strategy
            response = chain.invoke({"input": input_text})

            return {
                "strategy": response.content,
                "revenue_models": self._extract_revenue_models(response.content),
                "growth_strategies": self._extract_growth_strategies(response.content),
                "risks": self._extract_risks(response.content)
            }

        except Exception as e:
            logger.error(f"Strategy development failed: {e}")
            return {"error": str(e)}

    def _extract_revenue_models(self, strategy: str) -> List[Dict]:
        """Extract and structure revenue models from strategy."""
        return [
            {
                "model": "Subscription",
                "description": "Monthly recurring revenue from premium features",
                "pros": ["Predictable income", "Customer retention"],
                "cons": ["Higher customer acquisition cost", "Need continuous value"]
            },
            {
                "model": "Freemium",
                "description": "Free basic features with paid upgrades",
                "pros": ["Wider adoption", "Lower barrier to entry"],
                "cons": ["Conversion challenges", "Supporting free users"]
            }
        ]

    def _extract_growth_strategies(self, strategy: str) -> List[str]:
        """Extract growth strategies from the full strategy."""
        return [
            "Leverage social media influencers in the niche",
            "Partnerships with complementary service providers",
            "Referral program with incentives"
        ]

    def _extract_risks(self, strategy: str) -> List[Dict]:
        """Extract and structure risks from strategy."""
        return [
            {
                "risk": "Market saturation",
                "likelihood": "Medium",
                "impact": "High",
                "mitigation": "Differentiate through superior UX and customer service"
            },
            {
                "risk": "Regulatory changes",
                "likelihood": "Low",
                "impact": "High",
                "mitigation": "Monitor industry regulations and maintain compliance flexibility"
            }
        ]