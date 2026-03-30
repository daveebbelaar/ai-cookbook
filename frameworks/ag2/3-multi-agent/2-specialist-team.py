"""
AG2 Specialist Team: Production Multi-Agent Pattern

A practical example: a team of specialists collaborating to analyze
a business problem and produce actionable recommendations.

This pattern shows:
- Agents with distinct roles and expertise
- Tool registration across multiple agents
- GroupChat with termination control
- Clean output extraction
"""

import os
from typing import Annotated
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, LLMConfig

load_dotenv()


# --- Shared Tools ---

def analyze_metrics(
    metric_name: Annotated[str, "Name of the metric to analyze (e.g., churn, revenue, nps)"],
) -> str:
    """Analyze a business metric and return insights."""
    metrics = {
        "churn": "Monthly churn rate: 4.2% (up from 3.8%). Main drivers: poor onboarding, pricing.",
        "churn_rate": "Monthly churn rate: 4.2% (up from 3.8%). Main drivers: poor onboarding, pricing.",
        "revenue": "MRR: $2.1M. Growth: 12% QoQ. Top segment: Enterprise (58% of revenue).",
        "nps": "NPS score: 42 (down from 48). Detractors cite slow support response times.",
        "conversion": "Trial-to-paid: 18%. Bottleneck: day 3-5 activation drop-off.",
        "support": "Avg response time: 4.2 hours. Resolution rate: 87%. Backlog: 142 tickets.",
    }
    return metrics.get(metric_name.lower(), f"No data available for '{metric_name}'")


def main():
    llm_config = LLMConfig({
        "model": "gpt-4o-mini",
        "api_key": os.getenv("OPENAI_API_KEY"),
    })

    data_analyst = AssistantAgent(
        name="DataAnalyst",
        system_message=(
            "You are a data analyst. Use the analyze_metrics tool to pull "
            "relevant data. Identify patterns and anomalies in the numbers."
        ),
        llm_config=llm_config,
    )
    strategist = AssistantAgent(
        name="Strategist",
        system_message=(
            "You are a business strategist. Based on data insights, "
            "propose 3-5 actionable recommendations with expected impact."
        ),
        llm_config=llm_config,
    )
    reviewer = AssistantAgent(
        name="Reviewer",
        system_message=(
            "You ensure recommendations are practical and data-backed. "
            "Challenge weak arguments. Say TERMINATE when the plan is solid."
        ),
        llm_config=llm_config,
    )
    user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,  # Must be > 0 to execute tool calls in GroupChat
        code_execution_config=False,
        is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
    )

    # Register tools — decorator pattern
    @user_proxy.register_for_execution()
    @data_analyst.register_for_llm(description="Analyze business metrics")
    def analyze_metrics_tool(
        metric_name: Annotated[str, "Metric name"],
    ) -> str:
        return analyze_metrics(metric_name)

    # Create the team
    groupchat = GroupChat(
        agents=[user_proxy, data_analyst, strategist, reviewer],
        messages=[],
        max_round=12,
        speaker_selection_method="auto",
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    run_response = user_proxy.run(
        manager,
        message=(
            "Our churn rate has increased and NPS is dropping. "
            "Analyze the relevant metrics and create an action plan "
            "to improve retention over the next quarter."
        ),
    )
    run_response.process()

    # Extract the final recommendation
    print("\n" + "=" * 60)
    print("Final Recommendation:")
    print("=" * 60)
    print(run_response.summary)


if __name__ == "__main__":
    main()
