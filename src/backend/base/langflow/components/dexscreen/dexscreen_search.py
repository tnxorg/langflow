import requests
from langchain.tools import StructuredTool
from langchain_core.tools import ToolException
from loguru import logger
from pydantic import BaseModel, Field

from langflow.base.langchain_utilities.model import LCToolComponent
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

class SearchSchema(BaseModel):
    """Schema for the search tool."""
    search_query: str = Field(..., description="Query for searching pairs")

class SearchTool(LCToolComponent):
    """Tool for searching pairs."""
    
    display_name = "DexScreen Search"
    description = "Search for pairs matching query in DexScreener API"
    icon = "trending-up"
    name = "DexScreenSearch"
    
    BASE_URL = "https://api.dexscreener.com"

    inputs = [
        MessageTextInput(
            name="search_query",
            display_name="Search Query",
            required=False,
            info="Query for searching pairs",
        ),
    ]

    def run_model(self) -> list[Data]:
        return self._search_pairs(
            self.search_query,
        )

    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="search_pairs",
            description="Search for pairs matching query in DexScreener API.",
            func=self._search_pairs,
            args_schema=SearchSchema,
        )

    def _search_pairs(self, search_query: str) -> list[Data]:
        """Search for pairs matching the query."""
        try:
            if not search_query:
                raise ValueError("search_query is required")
            
            response = requests.get(f"{self.BASE_URL}/latest/dex/search", params={"q": search_query})
            response.raise_for_status()
            
            result = response.json()
            return [Data(data=pair) for pair in result.get("pairs", [])]
            
        except Exception as e:
            error_message = f"Error searching pairs: {e}"
            logger.debug(error_message)
            self.status = error_message
            raise ToolException(error_message) from e 