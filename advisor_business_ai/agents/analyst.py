from typing import Dict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from utils.config import config
from utils.logging import logger


class AnalysisAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
        self.prompt = self._create_prompt()

    def _create_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", """
            You are StartSmart Analyst, an expert in interpreting business data. Your role:
            1. Process raw research data into actionable insights
            2. Identify patterns, trends, and key takeaways
            3. Assess market opportunities and threats
            4. Create customer profiles and segmentation
            5. Provide clear, concise analysis for the strategy agent

            Guidelines:
            - Be analytical and objective
            - Support conclusions with data
            - Highlight the most important findings
            - Use visualizations when helpful (charts, tables)
            - Relate findings to the specific business context
            """),
            ("human", "{input}"),
        ])

    def analyze(self, research_data: Dict, business_context: Dict) -> Dict:
        """
        Analyze research findings in the context of the business idea.

        Args:
            research_data: Raw research findings from the research agent
            business_context: Details about the business idea and goals

        Returns:
            Dictionary containing analysis results
        """
        try:
            # Prepare input
            input_text = f"""
            Business Context:
            {business_context}

            Research Data:
            {research_data}

            Please analyze this data and provide insights relevant to the business.
            """

            # Create chain
            chain = self.prompt | self.llm

            # Perform analysis
            response = chain.invoke({"input": input_text})

            return {
                "analysis": response.content,
                "key_findings": self._extract_key_findings(response.content),
                "recommendations": self._generate_recommendations(response.content)
            }

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"error": str(e)}

    def _extract_key_findings(self, analysis: str) -> List[str]:
        """Extract the most important findings from analysis."""
        # In a real implementation, this would parse the analysis text
        # For now, return mock findings
        return [
            "Market is growing at 8% annually",
            "Key competitor weakness: poor customer service",
            "Target customers value convenience over price"
        ]

    def _generate_recommendations(self, analysis: str) -> List[str]:
        """Generate business recommendations based on analysis."""
        # In a real implementation, this would be more sophisticated
        return [
            "Focus on customer service as a differentiator",
            "Consider subscription model for recurring revenue",
            "Target urban professionals aged 25-40 first"
        ]