import requests
from langchain.tools import StructuredTool
from langchain_core.tools import ToolException
from loguru import logger
from pydantic import BaseModel, Field

from langflow.base.langchain_utilities.model import LCToolComponent
from langflow.field_typing import Tool
from langflow.inputs import MessageTextInput
from langflow.schema import Data

class OrdersSchema(BaseModel):
    """Schema for the token orders tool."""
    chain_id: str = Field(..., description="Chain ID (e.g., solana)")
    token_address: str = Field(..., description="Token address to check orders for")

class OrdersTool(LCToolComponent):
    """Tool for checking token orders."""
    
    display_name = "DexScreen Token Orders"
    description = "Check orders paid for a token in DexScreener API"
    icon = "trending-up"
    name = "DexScreenOrders"
    
    BASE_URL = "https://api.dexscreener.com"

    inputs = [
        MessageTextInput(
            name="chain_id",
            display_name="Chain ID",
            required=False,
            info="Chain ID (e.g., solana)",
        ),
        MessageTextInput(
            name="token_address",
            display_name="Token Address",
            required=False,
            info="Token address to check orders for",
        ),
    ]

    def run_model(self) -> list[Data]:
        return self._get_orders(
            self.chain_id,
            self.token_address,
        )

    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="get_token_orders",
            description="Check orders paid for a token in DexScreener API.",
            func=self._get_orders,
            args_schema=OrdersSchema,
        )

    def _get_orders(self, chain_id: str, token_address: str) -> list[Data]:
        """Get orders for a token."""
        try:
            if not chain_id or not token_address:
                raise ValueError("Both chain_id and token_address are required")
            
            response = requests.get(f"{self.BASE_URL}/orders/v1/{chain_id}/{token_address}")
            response.raise_for_status()
            
            result = response.json()
            return [Data(data=order) for order in result]
            
        except Exception as e:
            error_message = f"Error retrieving token orders: {e}"
            logger.debug(error_message)
            self.status = error_message
            raise ToolException(error_message) from e 