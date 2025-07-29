from typing import Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents import create_tool_calling_agent
from langchain_core.tools import tool
from utils.config import config
from utils.logging import logger


class PlannerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
        self.prompt = self._create_prompt()
        self.tools = []

    def _create_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", """
            You are StartSmart Planner, an expert in business planning and strategy. Your role is to:
            1. Analyze the user's business idea and goals
            2. Break down the requirements into specific tasks
            3. Delegate tasks to the appropriate specialized agents
            4. Coordinate the overall workflow

            Follow these steps:
            - First, understand the business idea, target market, and user's goals
            - Then, identify what information is needed (market size, competition, trends, etc.)
            - Create a step-by-step plan to gather and analyze this information
            - Assign tasks to the research, analysis, and strategy agents
            - Finally, ensure all pieces come together for the business plan

            Be thorough but efficient. Ask clarifying questions if needed.
            """),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

    def plan(self, user_input: str, chat_history: Optional[List] = None) -> Dict:
        """
        Create an execution plan for validating and developing the business idea.

        Args:
            user_input: The user's business idea or request
            chat_history: Previous conversation context

        Returns:
            Dictionary containing:
            - tasks: List of tasks to be performed
            - agent_assignments: Which agent should handle each task
            - expected_outputs: What each task should produce
        """
        try:
            # Create conversation chain
            agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
            agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

            # Prepare inputs
            inputs = {"input": user_input}
            if chat_history:
                inputs["chat_history"] = chat_history

            # Generate plan
            response = agent_executor.invoke(inputs)

            # Parse the response into structured plan
            plan = self._parse_response(response["output"])

            return plan

        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return {"error": str(e)}

    def _parse_response(self, response: str) -> Dict:
        """Parse the LLM response into a structured plan."""
        # This would involve more sophisticated parsing in a real implementation
        # For now, we'll return a simplified structure
        return {
            "tasks": [
                "Market research",
                "Competitor analysis",
                "Target customer profiling",
                "Revenue model suggestions",
                "Risk assessment"
            ],
            "agent_assignments": {
                "Market research": "research_agent",
                "Competitor analysis": "research_agent",
                "Target customer profiling": "analysis_agent",
                "Revenue model suggestions": "strategy_agent",
                "Risk assessment": "strategy_agent"
            },
            "expected_outputs": {
                "Market research": "Market size, trends, growth potential",
                "Competitor analysis": "List of competitors, their strengths/weaknesses",
                "Target customer profiling": "Customer demographics, needs, behaviors",
                "Revenue model suggestions": "Possible monetization strategies",
                "Risk assessment": "Key risks and mitigation strategies"
            }
        }