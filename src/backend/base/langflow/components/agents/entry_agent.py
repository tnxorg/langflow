from langflow.components.langchain_utilities.tool_calling import ToolCallingAgentComponent
from langflow.components.agents.agent import AgentComponent
# from backend.base.langflow.inputs.inputs import DataInput


class EntryAgentComponent(AgentComponent):
    display_name: str = "Entry Agent"
    description: str = "An agent designed to utilize various tools seamlessly within workflows."
    icon = "bot"
    name = "EntryAgent"

    inputs = [
        *AgentComponent.inputs
    ]


