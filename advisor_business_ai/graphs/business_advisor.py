from typing import Dict, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
from agents.planner import PlannerAgent
from agents.researcher import ResearchAgent
from agents.analyst import AnalysisAgent
from agents.strategist import StrategyAgent
from agents.writer import WriterAgent
from agents.critic import CriticAgent
from utils.config import config
from utils.logging import logger


class BusinessAdvisorState(TypedDict):
    user_input: str
    business_context: Dict[str, Any]
    plan: Optional[Dict]
    research: Optional[Dict]
    analysis: Optional[Dict]
    strategy: Optional[Dict]
    business_plan: Optional[Dict]
    review: Optional[Dict]
    iteration_count: int


class BusinessAdvisorGraph:
    def __init__(self):
        self.planner = PlannerAgent()
        self.researcher = ResearchAgent()  # Ensure this is ResearchAgent, not WebSearchTool
        self.analyst = AnalysisAgent()
        self.strategist = StrategyAgent()
        self.writer = WriterAgent()
        self.critic = CriticAgent()
        self.workflow = StateGraph(BusinessAdvisorState)

        self.workflow.add_node("planner", self._plan_workflow)
        self.workflow.add_node("researcher", self._conduct_research)
        self.workflow.add_node("analyst", self._analyze_data)
        self.workflow.add_node("strategist", self._develop_strategy)
        self.workflow.add_node("writer", self._create_plan)
        self.workflow.add_node("critic", self._review_plan)

        self.workflow.add_edge("planner", "researcher")
        self.workflow.add_edge("researcher", "analyst")
        self.workflow.add_edge("analyst", "strategist")
        self.workflow.add_edge("strategist", "writer")
        self.workflow.add_edge("writer", "critic")

        self.workflow.add_conditional_edges(
            "critic",
            self._should_iterate,
            {"continue": "planner", "end": END}
        )

        self.workflow.set_entry_point("planner")
        self.app = self.workflow.compile()

    def _plan_workflow(self, state: BusinessAdvisorState) -> Dict:
        user_input = state.get("user_input", "")
        chat_history = state.get("chat_history", [])
        plan = self.planner.plan(user_input, chat_history)
        return {"plan": plan, "iteration_count": state.get("iteration_count", 0)}

    def _conduct_research(self, state: BusinessAdvisorState) -> Dict:
        plan = state["plan"]
        research_tasks = [t for t in plan["tasks"] if plan["agent_assignments"][t] == "research_agent"]
        research_results = {}
        for task in research_tasks:
            result = self.researcher.conduct_research(task)  # Call conduct_research on ResearchAgent
            research_results[task] = result
        return {"research": research_results}

    def _analyze_data(self, state: BusinessAdvisorState) -> Dict:
        research_data = state["research"]
        business_context = state.get("business_context", {})
        analysis_results = {}
        for task, data in research_data.items():
            result = self.analyst.analyze(data, business_context)
            analysis_results[task] = result
        return {"analysis": analysis_results}

    def _develop_strategy(self, state: BusinessAdvisorState) -> Dict:
        analysis_data = state["analysis"]
        business_context = state.get("business_context", {})
        strategy_results = self.strategist.develop_strategy(analysis_data, business_context)
        return {"strategy": strategy_results}

    def _create_plan(self, state: BusinessAdvisorState) -> Dict:
        all_data = {
            "research": state["research"],
            "analysis": state["analysis"],
            "strategy": state["strategy"],
            "context": state.get("business_context", {})
        }
        plan = self.writer.create_business_plan(all_data)
        return {"business_plan": plan}

    def _review_plan(self, state: BusinessAdvisorState) -> Dict:
        plan = state["business_plan"]
        review = self.critic.review_plan(plan)
        return {
            "review": review,
            "business_plan": plan,
            "iteration_count": state.get("iteration_count", 0) + 1
        }

    def _should_iterate(self, state: BusinessAdvisorState) -> str:
        rating = state["review"].get("rating", 0)
        iteration_count = state.get("iteration_count", 0)
        max_iterations = 3
        return "continue" if rating < 8 and iteration_count < max_iterations else "end"

    def run(self, user_input: str, business_context: Optional[Dict] = None) -> Dict:
        try:
            initial_state = BusinessAdvisorState(
                user_input=user_input,
                business_context=business_context or {},
                plan=None,
                research=None,
                analysis=None,
                strategy=None,
                business_plan=None,
                review=None,
                iteration_count=0
            )
            result = self.app.invoke(initial_state)
            return {
                "business_plan": result["business_plan"],
                "review": result["review"],
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Business advisor workflow failed: {e}")
            return {"error": str(e), "status": "failed"}