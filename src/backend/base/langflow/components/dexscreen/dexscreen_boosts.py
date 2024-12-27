import requests
from enum import Enum
from langchain.tools import StructuredTool
from langchain_core.tools import ToolException
from loguru import logger
from pydantic import BaseModel, Field

from langflow.base.langchain_utilities.model import LCToolComponent
from langflow.field_typing import Tool
from langflow.inputs import DropdownInput
from langflow.schema import Data

class BoostType(str, Enum):
    LATEST = "latest"
    TOP = "top"

class BoostsSchema(BaseModel):
    """Schema for the token boosts tool."""
    boost_type: BoostType = Field(default=BoostType.LATEST, description="Type of boost data to retrieve (latest or top)")

class BoostsTool(LCToolComponent):
    """Tool for getting token boosts."""
    
    display_name = "DexScreen Token Boosts"
    description = "Get latest or top boosted tokens from DexScreener API"
    icon = "trending-up"
    name = "DexScreenBoosts"
    
    BASE_URL = "https://api.dexscreener.com"

    inputs = [
        DropdownInput(
            name="boost_type",
            display_name="Boost Type",
            info="Type of boost data to retrieve",
            options=list(BoostType),
            value=BoostType.LATEST.value,
        ),
    ]

    def run_model(self) -> list[Data]:
        return self._get_boosts(
            self.boost_type,
        )

    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="get_token_boosts",
            description="Get latest or top boosted tokens from DexScreener API.",
            func=self._get_boosts,
            args_schema=BoostsSchema,
        )

    def _get_boosts(self, boost_type: BoostType = BoostType.LATEST) -> list[Data]:
        """Get token boosts."""
        try:
            endpoint = boost_type.value
            response = requests.get(f"{self.BASE_URL}/token-boosts/{endpoint}/v1")
            response.raise_for_status()
            
            result = response.json()
            return [Data(data=boost) for boost in result]
            
        except Exception as e:
            error_message = f"Error retrieving token boosts: {e}"
            logger.debug(error_message)
            self.status = error_message
            raise ToolException(error_message) from e 