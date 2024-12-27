import requests
from langchain.tools import StructuredTool
from langchain_core.tools import ToolException
from loguru import logger
from pydantic import BaseModel

from langflow.base.langchain_utilities.model import LCToolComponent
from langflow.field_typing import Tool
from langflow.schema import Data

class TokenProfilesSchema(BaseModel):
    """Schema for the token profiles tool."""
    pass  # No parameters needed for this endpoint

class TokenProfilesTool(LCToolComponent):
    """Tool for getting the latest token profiles."""
    
    display_name = "DexScreen Token Profiles"
    description = "Get the latest token profiles from DexScreener API"
    icon = "trending-up"
    name = "DexScreenTokenProfiles"
    
    BASE_URL = "https://api.dexscreener.com"

    def run_model(self) -> list[Data]:
        return self._get_token_profiles()

    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="get_token_profiles",
            description="Get the latest token profiles from DexScreener API.",
            func=self._get_token_profiles,
            args_schema=TokenProfilesSchema,
        )

    def _get_token_profiles(self) -> list[Data]:
        """Get the latest token profiles."""
        try:
            response = requests.get(f"{self.BASE_URL}/token-profiles/latest/v1")
            response.raise_for_status()
            
            result = response.json()
            return [Data(data=profile) for profile in result]
            
        except Exception as e:
            error_message = f"Error retrieving token profiles: {e}"
            logger.debug(error_message)
            self.status = error_message
            raise ToolException(error_message) from e 