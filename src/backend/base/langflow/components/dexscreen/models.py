from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class TokenProfile(BaseModel):
    url: str
    chainId: str
    tokenAddress: str
    icon: Optional[str]
    header: Optional[str]
    description: Optional[str]
    links: Optional[List[Dict[str, str]]]

class BoostedToken(BaseModel):
    url: str
    chainId: str
    tokenAddress: str
    amount: float
    totalAmount: float
    icon: Optional[str]
    header: Optional[str]
    description: Optional[str]
    links: Optional[List[Dict[str, str]]]

class TokenOrder(BaseModel):
    type: str  # enum: tokenProfile, communityTakeover, tokenAd, trendingBarAd
    status: str  # enum: processing, cancelled, on-hold, approved, rejected
    paymentTimestamp: int

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

class DexScreenSchema(BaseModel):
    chain_id: Optional[str] = Field(None, description="Chain ID for pair lookup (e.g., solana)")
    pair_id: Optional[str] = Field(None, description="Pair address for lookup")
    token_addresses: Optional[str] = Field(None, description="Comma-separated token addresses (max 30)")
    search_query: Optional[str] = Field(None, description="Query for searching pairs") 