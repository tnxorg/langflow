import requests
from langchain.tools import StructuredTool
from langchain_core.tools import ToolException
from loguru import logger

from langflow.base.langchain_utilities.model import LCToolComponent
from langflow.field_typing import Tool
from langflow.inputs import DropdownInput, MessageTextInput
from langflow.schema import Data

from .dexscreen_method import DexScreenMethod
from .models import (
    TokenProfile,
    BoostedToken,
    TokenOrder,
    Pair,
    DexScreenSchema,
)

class DexScreenToolComponent(LCToolComponent):
    display_name = "DexScreen"
    description = """Uses DexScreener API to access token and pair information from various DEXes."""
    icon = "trending-up"
    name = "DexScreenTool"

    BASE_URL = "https://api.dexscreener.com"

    inputs = [
        MessageTextInput(
            name="chain_id",
            display_name="Chain ID",
            info="Chain ID for pair lookup (e.g., solana)",
        ),
        MessageTextInput(
            name="pair_id",
            display_name="Pair ID",
            info="Pair address for lookup",
        ),
        MessageTextInput(
            name="token_addresses",
            display_name="Token Addresses",
            info="Comma-separated token addresses (max 30)",
        ),
        MessageTextInput(
            name="search_query",
            display_name="Search Query",
            info="Query for searching pairs",
        ),
        DropdownInput(
            name="method",
            display_name="Data Method",
            info="The type of data to retrieve",
            options=list(DexScreenMethod),
            value="get_token_profiles",
        ),
    ]

    def run_model(self) -> list[Data]:
        return self._dexscreen_tool(
            self.chain_id,
            self.pair_id,
            self.token_addresses,
            self.search_query,
            self.method,
        )

    def build_tool(self) -> Tool:
        return StructuredTool.from_function(
            name="dexscreen",
            description="Access token and pair information from various DEXes using DexScreener API.",
            func=self._dexscreen_tool,
            args_schema=DexScreenSchema,
        )

    def _dexscreen_tool(
        self,
        chain_id: str = "",
        pair_id: str = "",
        token_addresses: str = "",
        search_query: str = "",
        method: DexScreenMethod = DexScreenMethod.GET_TOKEN_PROFILES,
    ) -> list[Data]:
        try:
            if method == DexScreenMethod.GET_TOKEN_PROFILES:
                response = requests.get(f"{self.BASE_URL}/token-profiles/latest/v1")
                response.raise_for_status()
                result = [TokenProfile(**profile) for profile in response.json()]

            elif method == DexScreenMethod.GET_BOOSTED_TOKENS:
                response = requests.get(f"{self.BASE_URL}/token-boosts/latest/v1")
                response.raise_for_status()
                result = [BoostedToken(**token) for token in response.json()]

            elif method == DexScreenMethod.GET_TOP_BOOSTED_TOKENS:
                response = requests.get(f"{self.BASE_URL}/token-boosts/top/v1")
                response.raise_for_status()
                result = [BoostedToken(**token) for token in response.json()]

            elif method == DexScreenMethod.GET_TOKEN_ORDERS:
                if not chain_id or not token_addresses:
                    raise ValueError("Both chain_id and token_addresses are required for GET_TOKEN_ORDERS")
                response = requests.get(f"{self.BASE_URL}/orders/v1/{chain_id}/{token_addresses}")
                response.raise_for_status()
                result = [TokenOrder(**order) for order in response.json()]

            elif method == DexScreenMethod.GET_PAIRS:
                if not chain_id or not pair_id:
                    raise ValueError("Both chain_id and pair_id are required for GET_PAIRS")
                response = requests.get(f"{self.BASE_URL}/latest/dex/pairs/{chain_id}/{pair_id}")
                response.raise_for_status()
                result = [Pair(**pair) for pair in response.json().get("pairs", [])]

            elif method == DexScreenMethod.GET_PAIRS_BY_TOKEN:
                if not token_addresses:
                    raise ValueError("token_addresses is required for GET_PAIRS_BY_TOKEN")
                addresses_list = [addr.strip() for addr in token_addresses.split(",") if addr.strip()]
                if len(addresses_list) > 30:
                    raise ValueError("Maximum of 30 token addresses allowed")
                addresses = ",".join(addresses_list)
                response = requests.get(f"{self.BASE_URL}/latest/dex/tokens/{addresses}")
                response.raise_for_status()
                result = [Pair(**pair) for pair in response.json().get("pairs", [])]

            elif method == DexScreenMethod.SEARCH_PAIRS:
                if not search_query:
                    raise ValueError("search_query is required for SEARCH_PAIRS")
                response = requests.get(f"{self.BASE_URL}/latest/dex/search", params={"q": search_query})
                response.raise_for_status()
                result = [Pair(**pair) for pair in response.json().get("pairs", [])]

            else:
                raise ValueError(f"Unknown method: {method}")

            return [Data(data=item.dict()) for item in result]

        except Exception as e:
            error_message = f"Error retrieving data from DexScreener API: {e}"
            logger.debug(error_message)
            self.status = error_message
            raise ToolException(error_message) from e 