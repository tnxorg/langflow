import requests
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field
from langflow.custom import Component
from langflow.io import (
    Output,
    StrInput,
)
from langflow.schema import Data

class TokenProfile(BaseModel):
    url: str
    chainId: str
    tokenAddress: str
    icon: Optional[str]
    header: Optional[str]
    description: Optional[str]
    links: Optional[List[Dict[str, str]]]

class PairToken(BaseModel):
    address: str
    name: str
    symbol: str

class PairLiquidity(BaseModel):
    usd: float
    base: float
    quote: float

class PairInfo(BaseModel):
    imageUrl: Optional[str]
    websites: Optional[List[Dict[str, str]]]
    socials: Optional[List[Dict[str, str]]]

class PairBoosts(BaseModel):
    active: int

class Pair(BaseModel):
    chainId: str
    dexId: str
    url: str
    pairAddress: str
    labels: Optional[List[str]]
    baseToken: PairToken
    quoteToken: PairToken
    priceNative: str
    priceUsd: str
    liquidity: PairLiquidity
    fdv: float
    marketCap: float
    pairCreatedAt: int
    info: Optional[PairInfo]
    boosts: Optional[PairBoosts]

class DexScreenAPI(Component):
    """
    A component for interacting with the DexScreener API.
    """
    display_name: str = "DexScreen API"
    description: str = "Component for interacting with the DexScreener API"
    name = "DexScreenAPI"
    
    output_types: list[str] = ["Data"]
    documentation: str = "https://docs.dexscreener.com/api/reference"
    
    BASE_URL = "https://api.dexscreener.com"

    inputs = [
        StrInput(
            name="chain_id",
            display_name="Chain ID",
            required=False,
            info="Chain ID for pair lookup (e.g., solana)",
        ),
        StrInput(
            name="pair_id",
            display_name="Pair ID",
            required=False,
            info="Pair address for lookup",
        ),
        StrInput(
            name="token_addresses",
            display_name="Token Addresses",
            required=False,
            info="Comma-separated token addresses (max 30)",
        ),
        StrInput(
            name="search_query",
            display_name="Search Query",
            required=False,
            info="Query for searching pairs",
        ),
    ]

    outputs = [
        Output(display_name="Data", name="data", method="build"),
    ]
    
    def __init__(self, **kwargs: Any):
        """Initialize the DexScreen API component."""
        super().__init__(**kwargs)
        self.session = requests.Session()
    
    def get_latest_token_profiles(self) -> List[TokenProfile]:
        """Get the latest token profiles."""
        response = self.session.get(f"{self.BASE_URL}/token-profiles/latest/v1")
        response.raise_for_status()
        return [TokenProfile(**profile) for profile in response.json()]
    
    def get_pairs_by_chain_and_address(self) -> List[Pair]:
        """Get pairs by chain ID and pair address."""
        if not self.chain_id or not self.pair_id:
            raise ValueError("Both chain_id and pair_id are required")
        
        response = self.session.get(f"{self.BASE_URL}/latest/dex/pairs/{self.chain_id}/{self.pair_id}")
        response.raise_for_status()
        data = response.json()
        return [Pair(**pair) for pair in data.get("pairs", [])]
    
    def get_pairs_by_token_addresses(self) -> List[Pair]:
        """Get pairs by token addresses (up to 30 addresses)."""
        if not self.token_addresses:
            raise ValueError("Token addresses are required")
        
        # Split comma-separated addresses and remove whitespace
        addresses_list = [addr.strip() for addr in self.token_addresses.split(",") if addr.strip()]
        
        if len(addresses_list) > 30:
            raise ValueError("Maximum of 30 token addresses allowed")
        
        addresses = ",".join(addresses_list)
        response = self.session.get(f"{self.BASE_URL}/latest/dex/tokens/{addresses}")
        response.raise_for_status()
        data = response.json()
        return [Pair(**pair) for pair in data.get("pairs", [])]
    
    def search_pairs(self) -> List[Pair]:
        """Search for pairs matching the query."""
        if not self.search_query:
            raise ValueError("Search query is required")
            
        response = self.session.get(f"{self.BASE_URL}/latest/dex/search", params={"q": self.search_query})
        response.raise_for_status()
        data = response.json()
        return [Pair(**pair) for pair in data.get("pairs", [])]

    def build(self) -> Data:
        """Build and execute the component based on provided parameters."""
        try:
            if self.chain_id and self.pair_id:
                result = self.get_pairs_by_chain_and_address()
            elif self.token_addresses:
                result = self.get_pairs_by_token_addresses()
            elif self.search_query:
                result = self.search_pairs()
            else:
                result = self.get_latest_token_profiles()
            return Data(data=result)
        except Exception as e:
            raise ValueError(f"Error fetching data from DexScreener API: {str(e)}") 