import requests
from langchain.tools import StructuredTool
from langchain_core.tools import ToolException
from loguru import logger
from pydantic import BaseModel, Field

from langflow.base.langchain_utilities.model import LCToolComponent
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

class PairsSchema(BaseModel):
    """Schema for the pairs tool."""
    chain_id: str = Field(..., description="Chain ID for pair lookup (e.g., solana)")
    pair_id: str = Field(..., description="Pair address for lookup")

class PairsTool(LCToolComponent):
    """Tool for getting pair information by chain and pair address."""
    
    display_name = "DexScreen Pairs"
    description = "Get pair information by chain ID and pair address from DexScreener API"
    icon = "trending-up"
    name = "DexScreenPairs"
    
    BASE_URL = "https://api.dexscreener.com"

    inputs = [
        MessageTextInput(
            name="chain_id",
            display_name="Chain ID",
            required=False,
            info="Chain ID for pair lookup (e.g., solana)",
        ),
        MessageTextInput(
            name="pair_id",
            display_name="Pair Address",
            required=False,
            info="Pair address for lookup",
        ),
    ]

    def run_model(self) -> list[Data]:
        return self._get_pairs(
            self.chain_id,
            self.pair_id,
        )

    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="get_pairs",
            description="Get pair information by chain ID and pair address from DexScreener API.",
            func=self._get_pairs,
            args_schema=PairsSchema,
        )

    def _get_pairs(self, chain_id: str, pair_id: str) -> list[Data]:
        """Get pairs by chain ID and pair address."""
        try:
            if not chain_id or not pair_id:
                raise ValueError("Both chain_id and pair_id are required")
            
            response = requests.get(f"{self.BASE_URL}/latest/dex/pairs/{chain_id}/{pair_id}")
            response.raise_for_status()
            
            result = response.json()
            return [Data(data=pair) for pair in result.get("pairs", [])]
            
        except Exception as e:
            error_message = f"Error retrieving pairs: {e}"
            logger.debug(error_message)
            self.status = error_message
            raise ToolException(error_message) from e 