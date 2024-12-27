from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from datetime import datetime

class BaseResponse(BaseModel):
    """Base response model for all GMGN API responses"""
    code: int = Field(description="Response code, 0 indicates success")
    msg: str = Field(description="Response message")
    data: Dict = Field(description="Response data")

class TokenRank(BaseModel):
    """Model for token rank information"""
    id: int
    chain: str
    address: str
    symbol: str
    logo: Optional[str]
    price: float
    price_change_percent: float
    swaps: int
    volume: float
    liquidity: float
    market_cap: float
    hot_level: int
    pool_creation_timestamp: int
    holder_count: int
    twitter_username: Optional[str]
    website: Optional[str]
    telegram: Optional[str]
    open_timestamp: int
    price_change_percent1m: float
    price_change_percent5m: float
    price_change_percent1h: float
    buys: int
    sells: int
    initial_liquidity: float
    is_show_alert: bool
    top_10_holder_rate: float
    renounced_mint: int
    renounced_freeze_account: int
    burn_ratio: str
    burn_status: str
    launchpad: Optional[str]
    dev_token_burn_amount: Optional[float]
    dev_token_burn_ratio: Optional[float]

class TrendingResponse(BaseResponse):
    """Response model for trending tokens"""
    data: Dict[str, List[TokenRank]]

class TokenPoolInfo(BaseModel):
    """Model for token pool information"""
    address: str
    pool_address: str
    quote_address: str
    quote_symbol: str
    liquidity: str
    base_reserve: str
    quote_reserve: str
    initial_liquidity: str
    initial_base_reserve: str
    initial_quote_reserve: str
    creation_timestamp: int
    base_reserve_value: str
    quote_reserve_value: str
    quote_vault_address: str
    base_vault_address: str
    creator: str

class TokenPoolResponse(BaseResponse):
    """Response model for token pool information"""
    data: TokenPoolInfo

class TokenStats(BaseModel):
    """Model for token statistics"""
    signal_count: int
    degen_call_count: int
    top_rat_trader_count: int
    top_smart_degen_count: int
    top_fresh_wallet_count: int
    top_rat_trader_amount_percentage: float
    top_trader_smart_degen_count: int
    top_trader_fresh_wallet_count: int
    bluechip_owner_count: int
    bluechip_owner_percentage: float

class TokenStatsResponse(BaseResponse):
    """Response model for token statistics"""
    data: TokenStats

class TokenInfo(BaseModel):
    """Model for token information"""
    address: str
    symbol: str
    name: str
    decimals: int
    logo: Optional[str]
    biggest_pool_address: str
    open_timestamp: int
    holder_count: int
    circulating_supply: str
    total_supply: str
    max_supply: str
    liquidity: str
    creation_timestamp: int

class TokenInfoResponse(BaseResponse):
    """Response model for token information"""
    data: TokenInfo

class TokenDevInfo(BaseModel):
    """Model for token developer information"""
    address: str
    creator_address: str
    creator_token_balance: str
    creator_token_status: str
    twitter_name_change_history: List[str]
    top_10_holder_rate: str
    dexscr_ad: int
    dexscr_update_link: int
    cto_flag: int

class TokenDevInfoResponse(BaseResponse):
    """Response model for token developer information"""
    data: TokenDevInfo

class TokenSecurityInfo(BaseModel):
    """Model for token security information"""
    address: str
    is_show_alert: bool
    top_10_holder_rate: str
    renounced_mint: bool
    renounced_freeze_account: bool
    burn_ratio: str
    burn_status: str
    dev_token_burn_amount: str
    dev_token_burn_ratio: str

class TokenSecurityResponse(BaseResponse):
    """Response model for token security information"""
    data: TokenSecurityInfo

class TokenLaunchpadInfo(BaseModel):
    """Model for token launchpad information"""
    address: str
    launchpad: Optional[str]
    launchpad_status: int
    launchpad_progress: str
    description: Optional[str]

class TokenLaunchpadResponse(BaseResponse):
    """Response model for token launchpad information"""
    data: TokenLaunchpadInfo

class TradeHistory(BaseModel):
    """Model for trade history"""
    maker: str
    base_amount: str
    quote_amount: str
    quote_symbol: str
    amount_usd: str
    timestamp: int
    event: str
    tx_hash: str
    price_usd: str
    total_trade: int
    id: str
    is_following: int
    is_open_or_close: int
    maker_tags: List[str]
    maker_token_tags: List[str]

class TokenTradeHistoryResponse(BaseResponse):
    """Response model for token trade history"""
    data: Dict[str, List[TradeHistory]]

class TokenLink(BaseModel):
    """Model for token links"""
    address: str
    gmgn: str
    geckoterminal: str
    twitter_username: Optional[str]
    website: Optional[str]
    telegram: Optional[str]
    discord: Optional[str]
    description: Optional[str]
    verify_status: int

class TokenLinkResponse(BaseResponse):
    """Response model for token links"""
    data: TokenLink

class TagWalletCount(BaseModel):
    """Model for tag wallet count"""
    chain: str
    token_address: str
    smart_wallets: int
    fresh_wallets: int
    renowned_wallets: int
    creator_wallets: int
    sniper_wallets: int
    rat_trader_wallets: int
    following_wallets: int
    whale_wallets: int
    top_wallets: int

class TagWalletCountResponse(BaseResponse):
    """Response model for tag wallet count"""
    data: TagWalletCount 