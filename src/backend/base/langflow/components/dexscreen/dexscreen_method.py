from enum import Enum

class DexScreenMethod(Enum):
    GET_TOKEN_PROFILES = "get_token_profiles"  # /token-profiles/latest/v1
    GET_BOOSTED_TOKENS = "get_boosted_tokens"  # /token-boosts/latest/v1
    GET_TOP_BOOSTED_TOKENS = "get_top_boosted_tokens"  # /token-boosts/top/v1
    GET_TOKEN_ORDERS = "get_token_orders"  # /orders/v1/{chainId}/{tokenAddress}
    GET_PAIRS = "get_pairs"  # /latest/dex/pairs/{chainId}/{pairId}
    GET_PAIRS_BY_TOKEN = "get_pairs_by_token"  # /latest/dex/tokens/{tokenAddresses}
    SEARCH_PAIRS = "search_pairs"  # /latest/dex/search 