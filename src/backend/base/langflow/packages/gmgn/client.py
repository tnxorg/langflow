from urllib.parse import urlencode
import requests
import json
import os
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from .models import (
    TrendingResponse, TokenPoolResponse, TokenStatsResponse,
    TokenInfoResponse, TokenDevInfoResponse, TokenSecurityResponse,
    TokenLaunchpadResponse, TokenTradeHistoryResponse, TokenLinkResponse,
    TagWalletCountResponse
)
from loguru import logger
import asyncio

class GmGnClient:
    """
    Client for interacting with GMGN.ai API with cookie management and proxy fallback
    """
    
    BASE_URL = "https://gmgn.ai"
    PROXY = "http://4357fc349e5869ec1222e54f258635df754e0315:custom_headers=true@api.zenrows.com:8001"
    CF_SCRAPER_URL = "http://localhost:3003/cf-clearance-scraper"
    
    def __init__(self):
        """Initialize the GMGN client with cookie management"""
        self.session = requests.Session()
        self.session.headers.update({
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        })
        # Initialize without cookies - they will be fetched when needed
        self.has_valid_cookies = False

    def prepare_cf_clearance(self):
        """
        Prepare CF clearance for the session
        """
        self._get_cf_clearance('https://gmgn.ai/defi/quotation/v1/tokens/sol')

    def _get_cf_clearance(self, url: str) -> bool:
        """
        Get new CF clearance cookies from scraper service
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.post(
                self.CF_SCRAPER_URL,
                headers={'Content-Type': 'application/json', 'Cache-Control': 'no-cache'},
                json={'url': url, 'mode': 'waf-session'}
            )
            if response.status_code != 200:
                logger.error(f"Failed to get CF clearance: {response.status_code}")
                return False
                
            data = response.json()
            
            # Set cookies from response
            for cookie in data.get('cookies', []):
                self.session.cookies.set(
                    cookie['name'],
                    cookie['value'],
                    domain=cookie['domain'],
                    path=cookie['path']
                )
            
            # Update headers from response
            if 'user-agent' in data.get('headers', {}):
                self.session.headers.update({'user-agent': data['headers']['user-agent']})
            
            self.has_valid_cookies = True
            return True
            
        except Exception as e:
            logger.error(f"Error getting CF clearance: {str(e)}")
            return False

    def _update_cookies_from_headers(self, headers: Dict):
        """Update session cookies from response headers"""
        if 'Zr-Set-Cookie' in headers:
            cookie_str = headers.get('Zr-Set-Cookie', '')
            if cookie_str:
                # Parse cookie string
                parts = cookie_str.split(';')
                if parts:
                    main_part = parts[0].strip()
                    if '=' in main_part:
                        name, value = main_part.split('=', 1)
                        # Use set instead of update to override existing cookie
                        self.session.cookies.set(name, value, domain='.gmgn.ai', path='/')
                        logger.debug(f"Set cookie: {name}={value}")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the GMGN API with automatic CF clearance refresh
        """
        url = f"{self.BASE_URL}{endpoint}"
        full_url = f"{url}?{urlencode(params)}" if params else url
        no_proxy_response = params.get("no_proxy", False) if params else False
        
        # Get initial CF clearance if needed
        if not self.has_valid_cookies:
            if not self._get_cf_clearance(full_url):
                raise Exception("Failed to get initial CF clearance")

        # First try: Use existing cookies without proxy
        try:
            response = self.session.get(full_url)
            if response.status_code == 200:
                return response.json()
            elif response.status_code in [403, 401]:  # CF challenge or unauthorized
                logger.error(f"CF challenge or unauthorized for {url}")
                # Try refreshing CF clearance
                if self._get_cf_clearance(full_url):
                    response = self.session.get(full_url)
                    if response.status_code == 200:
                        return response.json()
        except Exception as e:
            print(f"No proxy error: {e}")

        if no_proxy_response:
            raise Exception("Request failed without proxy")
        
        # Second try: Use proxy as fallback
        proxies = {"http": self.PROXY, "https": self.PROXY}
        try:
            response = requests.get(url, params=params, proxies=proxies, verify=False)
            if response.status_code == 200:
                self._update_cookies_from_headers(response.headers)
                return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch data: {str(e)}")
        
        raise Exception(f"Request failed with status code: {response.status_code}")
    
    def get_trending(self, time_frame: str = "1h", limit: int = 15, **kwargs) -> TrendingResponse:
        """
        Get trending tokens by time frame
        
        Args:
            time_frame (str): Time frame for trending data (e.g., "1h", "24h")
            limit (int): Number of trending tokens to return
            
        Returns:
            TrendingResponse: Trending tokens data including volume, price changes, and market metrics
        """
        endpoint = f"/defi/quotation/v1/rank/sol/swaps/{time_frame}"
        params = {
            "orderby": "swaps",
            "direction": "desc",
            "limit": limit,
            "filters[]": "not_risk"
        }
        params.update(kwargs)
        return TrendingResponse(**self._make_request(endpoint, params))
    
    def get_token_pool_info(self, token_address: str) -> Dict[str, Any]:
        """
        Get token pool information
        
        Args:
            token_address (str): The Solana token address
            
        Returns:
            TokenPoolResponse: Detailed information about the token's liquidity pool
        """
        endpoint = f"/api/v1/token_pool_info_sol/sol/{token_address}"
        return self._make_request(endpoint)
    
    def get_token_stats(self, token_address: str) -> TokenStatsResponse:
        """
        Get token statistics
        
        Args:
            token_address (str): The Solana token address
            
        Returns:
            TokenStatsResponse: Various statistics about the token including trader metrics
        """
        endpoint = f"/defi/quotation/v1/tokens/stats/sol/{token_address}"
        return TokenStatsResponse(**self._make_request(endpoint))
    
    def get_token_info(self, token_address: str) -> Dict[str, Any]:
        """
        Get token information
        
        Args:
            token_address (str): The Solana token address
            
        Returns:
            TokenInfoResponse: Basic information about the token including supply and decimals
        """
        endpoint = f"/api/v1/token_info/sol/{token_address}"
        return self._make_request(endpoint)
    
    def get_token_dev_info(self, token_address: str) -> Dict[str, Any]:
        """
        Get token developer information
        
        Args:
            token_address (str): The Solana token address
            
        Returns:
            TokenDevInfoResponse: Information about the token's developer and creator
        """
        endpoint = f"/api/v1/token_dev_info/sol/{token_address}"
        return self._make_request(endpoint)
    
    def get_token_security_info(self, token_address: str) -> Dict[str, Any]:
        """
        Get token security information
        
        Args:
            token_address (str): The Solana token address
            
        Returns:
            TokenSecurityResponse: Security-related information including mint authority and burn status
        """
        endpoint = f"/api/v1/token_security_sol/sol/{token_address}"
        return self._make_request(endpoint)
    
    def get_token_launchpad_info(self, token_address: str) -> Dict[str, Any]:
        """
        Get token launchpad information
        
        Args:
            token_address (str): The Solana token address
            
        Returns:
            TokenLaunchpadResponse: Information about the token's launch status and details
        """
        endpoint = f"/api/v1/token_launchpad_info/sol/{token_address}"
        return self._make_request(endpoint)
    
    def get_token_trade_history(
        self, token_address: str, limit: int = 100, maker: str = ""
    ) -> Dict[str, Any]:
        """
        Get token trade history
        
        Args:
            token_address (str): The Solana token address
            limit (int): Number of trades to return
            maker (str): Filter trades by maker address
            
        Returns:
            TokenTradeHistoryResponse: Historical trade data for the token
        """
        endpoint = f"/api/v1/token_trades/sol/{token_address}"
        params = {
            "limit": limit,
            "maker": maker
        }
        res = self._make_request(endpoint, params)
        return res
    
    def get_token_link(self, token_address: str) -> Dict[str, Any]:
        """
        Get token links
        
        Args:
            token_address (str): The Solana token address
            
        Returns:
            TokenLinkResponse: Various links related to the token (website, social media, etc.)
        """
        endpoint = f"/api/v1/token_link/sol/{token_address}"
        return self._make_request(endpoint)
    
    def get_kline(
        self, token_address: str, resolution: str = "5m",
        from_time: Union[int, datetime] = None,
        to_time: Union[int, datetime] = None
    ) -> Dict:
        """
        Get token kline/candlestick data
        
        Args:
            token_address (str): The Solana token address
            resolution (str): Kline interval (e.g., "5m", "1h", "1d")
            from_time (Union[int, datetime]): Start time for kline data
            to_time (Union[int, datetime]): End time for kline data
            
        Returns:
            Dict: Kline/candlestick data for the specified time range
        """
        endpoint = f"/api/v1/token_kline/sol/{token_address}"
        
        # Convert datetime objects to timestamps if needed
        if isinstance(from_time, datetime):
            from_time = int(from_time.timestamp())
        if isinstance(to_time, datetime):
            to_time = int(to_time.timestamp())
            
        params = {
            "resolution": resolution,
            "from": from_time,
            "to": to_time
        }
        return self._make_request(endpoint, params)
    
    def get_top_buyers(self, token_address: str) -> Dict:
        """
        Get top buyers information
        
        Args:
            token_address (str): The Solana token address
            
        Returns:
            Dict: Information about the token's top buyers and their trading patterns
        """
        endpoint = f"/defi/quotation/v1/tokens/top_buyers/sol/{token_address}"
        return self._make_request(endpoint)
    
    def get_rug_history(self, token_address: str) -> Dict:
        """
        Get rug pull history
        
        Args:
            token_address (str): The Solana token address
            
        Returns:
            Dict: Historical information about potential rug pulls
        """
        endpoint = f"/defi/quotation/v1/tokens/rug_history/sol/{token_address}"
        return self._make_request(endpoint)
    
    def get_tag_wallet_count(self, token_address: str) -> TagWalletCountResponse:
        """
        Get tag wallet count
        
        Args:
            token_address (str): The Solana token address
            
        Returns:
            TagWalletCountResponse: Count of different types of wallets holding the token
        """
        endpoint = f"/defi/quotation/v1/tokens/tag_wallet_count/sol/{token_address}"
        return TagWalletCountResponse(**self._make_request(endpoint)) 

    def _format_token_info(self, token_info: Dict) -> str:
        """Format token basic information into markdown"""
        return f"""### Basic Token Information
- **Symbol**: {token_info.get('symbol', 'N/A')}
- **Name**: {token_info.get('name', 'N/A')}
- **Address**: {token_info.get('address', 'N/A')}
- **Decimals**: {token_info.get('decimals', 'N/A')}
- **Logo**: {token_info.get('logo', 'N/A')}
- **Biggest Pool**: {token_info.get('biggest_pool_address', 'N/A')}
- **Open Timestamp**: <t:{token_info.get('open_timestamp', 0)}:F>
- **Creation Timestamp**: <t:{token_info.get('creation_timestamp', 0)}:F>
- **Holder Count**: {token_info.get('holder_count', 'N/A')}
- **Circulating Supply**: {token_info.get('circulating_supply', 'N/A')}
- **Total Supply**: {token_info.get('total_supply', 'N/A')}
- **Max Supply**: {token_info.get('max_supply', 'N/A')}
- **Liquidity**: {token_info.get('liquidity', 'N/A')} SOL"""

    def _format_pool_info(self, pool_info: Dict) -> str:
        """Format pool information into markdown"""
        return f"""### Pool Information
- **Pool Address**: {pool_info.get('pool_address', 'N/A')}
- **Quote Token**: {pool_info.get('quote_symbol', 'N/A')} ({pool_info.get('quote_address', 'N/A')})
- **Current Liquidity**: {pool_info.get('liquidity', 'N/A')} SOL
- **Initial Liquidity**: {pool_info.get('initial_liquidity', 'N/A')} SOL
- **Base Reserve**: {pool_info.get('base_reserve', 'N/A')}
- **Quote Reserve**: {pool_info.get('quote_reserve', 'N/A')}
- **Initial Base Reserve**: {pool_info.get('initial_base_reserve', 'N/A')}
- **Initial Quote Reserve**: {pool_info.get('initial_quote_reserve', 'N/A')}
- **Creation Time**: <t:{pool_info.get('creation_timestamp', 0)}:F>
- **Base Reserve Value**: {pool_info.get('base_reserve_value', 'N/A')}
- **Quote Reserve Value**: {pool_info.get('quote_reserve_value', 'N/A')}
- **Quote Vault**: {pool_info.get('quote_vault_address', 'N/A')}
- **Base Vault**: {pool_info.get('base_vault_address', 'N/A')}
- **Creator**: {pool_info.get('creator', 'N/A')}"""

    def _format_stats(self, stats: Dict) -> str:
        """Format token statistics into markdown"""
        return f"""### Trading Statistics
- **Signal Count**: {stats.get('signal_count', 0)}
- **Degen Call Count**: {stats.get('degen_call_count', 0)}
- **Top Rat Trader Count**: {stats.get('top_rat_trader_count', 0)}
- **Smart Degen Count**: {stats.get('top_smart_degen_count', 0)}
- **Fresh Wallet Count**: {stats.get('top_fresh_wallet_count', 0)}
- **Rat Trader Amount %**: {stats.get('top_rat_trader_amount_percentage', 0)}%
- **Smart Degen Trader Count**: {stats.get('top_trader_smart_degen_count', 0)}
- **Fresh Wallet Trader Count**: {stats.get('top_trader_fresh_wallet_count', 0)}
- **Bluechip Owner Count**: {stats.get('bluechip_owner_count', 0)}
- **Bluechip Owner %**: {stats.get('bluechip_owner_percentage', 0)}%"""

    def _format_dev_info(self, dev_info: Dict) -> str:
        """Format developer information into markdown"""
        twitter_history = "\n  ".join(dev_info.get('twitter_name_change_history', []) or ['No changes'])
        return f"""### Developer Information
- **Creator Address**: {dev_info.get('creator_address', 'N/A')}
- **Creator Balance**: {dev_info.get('creator_token_balance', 'N/A')}
- **Creator Status**: {dev_info.get('creator_token_status', 'N/A')}
- **Top 10 Holder Rate**: {dev_info.get('top_10_holder_rate', 'N/A')}
- **DexScr Ad**: {dev_info.get('dexscr_ad', 0)}
- **DexScr Update Link**: {dev_info.get('dexscr_update_link', 0)}
- **CTO Flag**: {dev_info.get('cto_flag', 0)}
- **Twitter Name History**:
  {twitter_history}"""

    def _format_security_info(self, security_info: Dict) -> str:
        """Format security information into markdown"""
        return f"""### Security Information
- **Alert Status**: {'⚠️ Warning' if security_info.get('is_show_alert') else '✅ Safe'}
- **Top 10 Holder Rate**: {security_info.get('top_10_holder_rate', 'N/A')}
- **Mint Authority Renounced**: {'✅ Yes' if security_info.get('renounced_mint') else '❌ No'}
- **Freeze Authority Renounced**: {'✅ Yes' if security_info.get('renounced_freeze_account') else '❌ No'}
- **Burn Ratio**: {security_info.get('burn_ratio', 'N/A')}
- **Burn Status**: {security_info.get('burn_status', 'N/A')}
- **Dev Token Burn Amount**: {security_info.get('dev_token_burn_amount', 'N/A')}
- **Dev Token Burn Ratio**: {security_info.get('dev_token_burn_ratio', 'N/A')}"""

    def _format_launchpad_info(self, launchpad_info: Dict) -> str:
        """Format launchpad information into markdown"""
        return f"""### Launchpad Information
- **Platform**: {launchpad_info.get('launchpad', 'N/A')}
- **Status**: {launchpad_info.get('launchpad_status', 'N/A')}
- **Progress**: {float(launchpad_info.get('launchpad_progress', 0)) * 100:.2f}%
- **Description**: {launchpad_info.get('description', 'N/A')}"""

    def _format_links(self, links: Dict) -> str:
        """Format token links into markdown"""
        return f"""### Token Links
- **GMGN**: {links.get('gmgn', 'N/A')}
- **GeckoTerminal**: {links.get('geckoterminal', 'N/A')}
- **Website**: {links.get('website', 'N/A')}
- **Twitter**: {links.get('twitter_username', 'N/A')}
- **Telegram**: {links.get('telegram', 'N/A')}
- **Discord**: {links.get('discord', 'N/A')}
- **GitHub**: {links.get('github', 'N/A')}
- **Medium**: {links.get('medium', 'N/A')}
- **Reddit**: {links.get('reddit', 'N/A')}
- **YouTube**: {links.get('youtube', 'N/A')}
- **TikTok**: {links.get('tiktok', 'N/A')}
- **Instagram**: {links.get('instagram', 'N/A')}
- **LinkedIn**: {links.get('linkedin', 'N/A')}
- **Facebook**: {links.get('facebook', 'N/A')}
- **BitBucket**: {links.get('bitbucket', 'N/A')}
- **Description**: {links.get('description', 'N/A')}
- **Verification Status**: {'✅ Verified' if links.get('verify_status') == 1 else '❌ Unverified'}"""

    def _format_wallet_analysis(self, wallet_count: Dict) -> str:
        """Format wallet analysis into markdown"""
        return f"""### Wallet Analysis
- **Smart Wallets**: {wallet_count.get('smart_wallets', 0)}
- **Fresh Wallets**: {wallet_count.get('fresh_wallets', 0)}
- **Renowned Wallets**: {wallet_count.get('renowned_wallets', 0)}
- **Creator Wallets**: {wallet_count.get('creator_wallets', 0)}
- **Sniper Wallets**: {wallet_count.get('sniper_wallets', 0)}
- **Rat Trader Wallets**: {wallet_count.get('rat_trader_wallets', 0)}
- **Following Wallets**: {wallet_count.get('following_wallets', 0)}
- **Whale Wallets**: {wallet_count.get('whale_wallets', 0)}
- **Top Wallets**: {wallet_count.get('top_wallets', 0)}"""

    def _format_recent_trades(self, trades: List[Dict]) -> str:
        """Format recent trades into markdown"""
        if not trades:
            return "### Recent Trades\nNo recent trades found."
        
        def safe_float(value: Any, default: float = 0.0) -> float:
            """Safely convert value to float, handling empty strings and None"""
            if not value:  # Handles empty string, None, and 0
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        trades_md = ["### Recent Trades"]
        for trade in trades[:10]:
            try:
                timestamp = trade.get('timestamp', 0)
                amount_usd = safe_float(trade.get('amount_usd'))
                price_usd = safe_float(trade.get('price_usd'))
                event = trade.get('event', 'unknown')
                maker = trade.get('maker', '')[:8]
                base_amount = safe_float(trade.get('base_amount'))
                quote_amount = safe_float(trade.get('quote_amount'))
                quote_symbol = trade.get('quote_symbol', 'SOL')
                
                # Get maker tags and handle empty lists
                maker_tags = trade.get('maker_tags', [])
                token_tags = trade.get('maker_token_tags', [])
                tags = ', '.join(filter(None, maker_tags + token_tags)) or 'No tags'
                
                # Format trade details with additional information
                trades_md.append(f"""- **{event.upper()}** by `{maker}...`
  - Time: <t:{timestamp}:R>
  - Amount: ${amount_usd:.2f} ({base_amount:.2f} tokens for {quote_amount:.6f} {quote_symbol})
  - Price: ${price_usd:.6f} per token
  - Tags: {tags}""")
            except Exception as e:
                logger.error(f"Error formatting trade: {str(e)}")
                continue
        
        return "\n".join(trades_md)

    def _format_rug_analysis(self, rug_data: Dict) -> str:
        """Format rug analysis into markdown"""
        if not rug_data:
            return "### Risk Assessment\nNo rug analysis data available."
        
        rug_ratio = rug_data.get('rug_ratio')
        holder_rugged = rug_data.get('holder_rugged_num')
        holder_total = rug_data.get('holder_token_num')
        
        if rug_ratio is None:
            return "### Risk Assessment\n✅ No signs of rug pull detected."
        
        return f"""### Risk Assessment
- **Rug Pull Ratio**: {rug_ratio}
- **Affected Holders**: {holder_rugged}/{holder_total}
- **Token Name**: {rug_data.get('name', 'N/A')}
- **Symbol**: {rug_data.get('symbol', 'N/A')}"""

    def _format_top_buyers(self, buyers_data: Dict) -> str:
        """Format top buyers analysis into markdown"""
        if not buyers_data or 'holders' not in buyers_data:
            return "### Top Buyers Analysis\nNo top buyers data available."
        
        holders = buyers_data.get('holders', {})
        status = holders.get('statusNow', {})
        
        return f"""### Top Buyers Analysis
- **Total Holders**: {holders.get('holder_count', 0)}
- **Current Status**:
  - Still Holding: {status.get('hold', 0)}
  - Bought More: {status.get('bought_more', 0)}
  - Partially Sold: {status.get('sold_part', 0)}
  - Fully Sold: {status.get('sold', 0)}
  - Buy Rate: {status.get('bought_rate', 'N/A')}
  - Holding Rate: {status.get('holding_rate', 'N/A')}
  - Top 10 Holder Rate: {status.get('top_10_holder_rate', 'N/A')}"""

    def _format_time(self, timestamp: int, format: str = "R") -> str:
        """Format timestamp into human readable format"""
        if not timestamp:
            return "N/A"
        dt = datetime.fromtimestamp(timestamp)
        if format == "R":
            now = datetime.now()
            diff = now - dt
            if diff.days > 0:
                return f"{diff.days} days ago"
            hours = diff.seconds // 3600
            if hours > 0:
                return f"{hours} hours ago"
            minutes = (diff.seconds % 3600) // 60
            if minutes > 0:
                return f"{minutes} minutes ago"
            return "just now"
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def _calculate_technical_indicators(self, candles: List[Dict]) -> Dict:
        """Calculate technical indicators from candle data"""
        if not candles:
            return {}

        # Extract price series
        closes = [c['close'] for c in candles]
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]
        
        # Find support and resistance levels using recent swing points
        def find_swing_points(prices: List[float], window: int = 5) -> tuple:
            supports = []
            resistances = []
            for i in range(window, len(prices) - window):
                if all(prices[i] <= prices[j] for j in range(i-window, i+window+1)):
                    supports.append(prices[i])
                if all(prices[i] >= prices[j] for j in range(i-window, i+window+1)):
                    resistances.append(prices[i])
            return supports, resistances

        # Calculate trend direction using linear regression
        def calculate_trend(prices: List[float]) -> str:
            if len(prices) < 2:
                return "Neutral"
            x = list(range(len(prices)))
            y = prices
            n = len(x)
            slope = (n * sum(x[i]*y[i] for i in range(n)) - sum(x)*sum(y)) / (n*sum(x[i]**2 for i in range(n)) - sum(x)**2)
            return "Uptrend 📈" if slope > 0 else "Downtrend 📉" if slope < 0 else "Neutral ↔️"

        # Find patterns
        def find_patterns(candles: List[Dict]) -> List[str]:
            patterns = []
            # Double top pattern
            if len(candles) > 20:
                highs = [c['high'] for c in candles[-20:]]
                if max(highs[:-10]) - max(highs[-10:]) < 0.01 * max(highs):
                    patterns.append("Potential Double Top")
            
            # Double bottom pattern
            if len(candles) > 20:
                lows = [c['low'] for c in candles[-20:]]
                if min(lows[-10:]) - min(lows[:-10]) < 0.01 * min(lows):
                    patterns.append("Potential Double Bottom")
            
            # Bull/Bear flag pattern
            if len(candles) > 10:
                recent_trend = calculate_trend([c['close'] for c in candles[-10:]])
                if recent_trend != "Neutral":
                    patterns.append(f"Potential {'Bull' if recent_trend == 'Uptrend 📈' else 'Bear'} Flag")
            
            return patterns

        # Calculate Fibonacci levels
        def calculate_fibonacci_levels(high: float, low: float) -> Dict[str, float]:
            diff = high - low
            return {
                "0.236": low + 0.236 * diff,
                "0.382": low + 0.382 * diff,
                "0.500": low + 0.500 * diff,
                "0.618": low + 0.618 * diff,
                "0.786": low + 0.786 * diff
            }

        # Calculate RSI
        def calculate_rsi(prices: List[float], periods: int = 14) -> float:
            if len(prices) < periods + 1:
                return 50
            
            deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            gains = [d if d > 0 else 0 for d in deltas]
            losses = [-d if d < 0 else 0 for d in deltas]
            
            avg_gain = sum(gains[-periods:]) / periods
            avg_loss = sum(losses[-periods:]) / periods
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

        # Get support and resistance levels
        supports, resistances = find_swing_points(lows), find_swing_points(highs)
        
        # Calculate Fibonacci levels from recent high/low
        recent_high = max(highs[-20:]) if len(highs) > 20 else max(highs)
        recent_low = min(lows[-20:]) if len(lows) > 20 else min(lows)
        fib_levels = calculate_fibonacci_levels(recent_high, recent_low)
        
        # Calculate RSI
        rsi = calculate_rsi(closes)
        
        return {
            "trend": calculate_trend(closes),
            "patterns": find_patterns(candles),
            "support_levels": sorted(set(supports[0])) if supports else [],
            "resistance_levels": sorted(set(resistances[0])) if resistances else [],
            "fibonacci_levels": fib_levels,
            "rsi": rsi
        }

    def _format_kline_data(self, kline_data: Dict, timeframe: str = "5m") -> str:
        """Format kline/candlestick data into markdown for price analysis"""
        if not kline_data or 'list' not in kline_data:
            return f"### Price Chart Analysis ({timeframe})\nNo price data available."

        candles = kline_data.get('list', [])
        if not candles:
            return f"### Price Chart Analysis ({timeframe})\nNo candlestick data available."

        try:
            # Convert string values to float and timestamp to int
            processed_candles = []
            for candle in candles:
                if all(k in candle for k in ['time', 'open', 'high', 'low', 'close', 'volume']):
                    processed_candles.append({
                        'time': int(int(candle['time']) / 1000),  # Convert milliseconds to seconds
                        'open': float(candle['open']),
                        'high': float(candle['high']),
                        'low': float(candle['low']),
                        'close': float(candle['close']),
                        'volume': float(candle['volume'])
                    })

            if not processed_candles:
                return f"### Price Chart Analysis ({timeframe})\nInvalid candle data format."

            # Calculate key metrics
            current_price = processed_candles[-1]['close']
            open_price = processed_candles[0]['open']
            highest_price = max(c['high'] for c in processed_candles)
            lowest_price = min(c['low'] for c in processed_candles)
            total_volume = sum(c['volume'] for c in processed_candles)
            
            # Calculate technical indicators
            indicators = self._calculate_technical_indicators(processed_candles)
            
            # Calculate price change
            price_change = ((current_price - open_price) / open_price) * 100
            
            # Analyze price movement patterns
            up_candles = sum(1 for c in processed_candles if c['close'] > c['open'])
            down_candles = sum(1 for c in processed_candles if c['close'] < c['open'])
            total_candles = len(processed_candles)
            
            # Format the analysis
            analysis = f"""### Price Chart Analysis ({timeframe})
#### Key Metrics
- **Current Price**: ${current_price:.6f} ({self._format_time(processed_candles[-1]['time'])})
- **Period Open**: ${open_price:.6f} ({self._format_time(processed_candles[0]['time'])})
- **Price Change**: {price_change:+.2f}%
- **Highest Price**: ${highest_price:.6f}
- **Lowest Price**: ${lowest_price:.6f}
- **Total Volume**: ${total_volume:.2f}

#### Technical Analysis
- **Trend Direction**: {indicators['trend']}
- **RSI (14)**: {indicators['rsi']:.2f} ({'Overbought' if indicators['rsi'] > 70 else 'Oversold' if indicators['rsi'] < 30 else 'Neutral'})
- **Identified Patterns**: {', '.join(indicators['patterns']) if indicators['patterns'] else 'No clear patterns'}

#### Support & Resistance
- **Key Support Levels**: {', '.join(f'${s:.6f}' for s in indicators['support_levels'][:3])}
- **Key Resistance Levels**: {', '.join(f'${r:.6f}' for r in indicators['resistance_levels'][:3])}

#### Fibonacci Retracement Levels
- **23.6%**: ${indicators['fibonacci_levels']['0.236']:.6f}
- **38.2%**: ${indicators['fibonacci_levels']['0.382']:.6f}
- **50.0%**: ${indicators['fibonacci_levels']['0.500']:.6f}
- **61.8%**: ${indicators['fibonacci_levels']['0.618']:.6f}
- **78.6%**: ${indicators['fibonacci_levels']['0.786']:.6f}

#### Market Analysis
- **Time Period**: {self._format_time(processed_candles[0]['time'], "F")} to {self._format_time(processed_candles[-1]['time'], "F")}
- **Number of Candles**: {total_candles}
- **Upward Movements**: {up_candles} ({(up_candles/total_candles)*100:.1f}%)
- **Downward Movements**: {down_candles} ({(down_candles/total_candles)*100:.1f}%)

#### Price Volatility
- **Price Range**: ${highest_price-lowest_price:.6f}
- **High-Low Spread**: {((highest_price-lowest_price)/lowest_price)*100:.2f}%
- **Average Volume**: ${total_volume/total_candles:.2f}

#### OHLC Data
Time | Open | High | Low | Close | Volume | Type
-----|------|------|-----|--------|---------|------
"""
            # Add all candles in OHLC format
            for candle in processed_candles:
                candle_type = "🟢" if candle['close'] >= candle['open'] else "🔴"
                analysis += f"{self._format_time(candle['time'], 'F')} | ${candle['open']:.6f} | ${candle['high']:.6f} | ${candle['low']:.6f} | ${candle['close']:.6f} | {candle['volume']:.2f} | {candle_type}\n"

            return analysis

        except Exception as e:
            logger.error(f"Error formatting kline data: {str(e)}")
            return f"### Price Chart Analysis ({timeframe})\nError processing price data."

    async def get_all_token_info_for_markdown(self, token_address: str) -> str:
        """
        Get all token information and format it into a comprehensive markdown report
        """
        # Convert synchronous methods to coroutines
        async def async_get(method, *args, **kwargs):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: method(*args, **kwargs))
        
        await async_get(self.prepare_cf_clearance)

        # Calculate time ranges
        now = int(datetime.now().timestamp())
        day_ago = now - 86400  # 24 hours
        four_hours_ago = now - 14400  # 4 hours

        tasks = [
            async_get(self.get_token_info, token_address),
            async_get(self.get_token_pool_info, token_address), 
            async_get(self.get_token_stats, token_address),
            async_get(self.get_token_dev_info, token_address),
            async_get(self.get_token_security_info, token_address),
            async_get(self.get_token_launchpad_info, token_address),
            async_get(self.get_token_link, token_address),
            async_get(self.get_tag_wallet_count, token_address),
            async_get(self.get_top_buyers, token_address),
            async_get(self.get_rug_history, token_address),
            async_get(self.get_token_trade_history, token_address, limit=20),
            async_get(self.get_kline, token_address, "5m", four_hours_ago, now),  # 4h chart with 5m candles
            async_get(self.get_kline, token_address, "4h", day_ago - (30 * 86400), now)  # 4h candles for the last 30 days
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        [token_info, pool_info, stats, dev_info, security_info, 
         launchpad_info, links, wallet_count, top_buyers, 
         rug_history, trade_history, kline_5m, kline_4h] = [
            result.get('data', {}) if isinstance(result, dict) else {} 
            for result in results
        ]

        sections = [
            f"# Token Analysis Report for {token_info.get('symbol', 'Unknown Token')}",
            self._format_token_info(token_info),
            self._format_pool_info(pool_info),
            self._format_security_info(security_info),
            self._format_dev_info(dev_info),
            self._format_stats(stats),
            self._format_wallet_analysis(wallet_count),
            self._format_launchpad_info(launchpad_info),
            self._format_links(links),
            "## Short-term Analysis (5m)",
            self._format_kline_data(kline_5m, "5m"),
            "## Long-term Analysis (4h)",
            self._format_kline_data(kline_4h, "4h"),
            self._format_recent_trades(trade_history.get('history', [])),
            self._format_rug_analysis(rug_history),
            self._format_top_buyers(top_buyers)
        ]

        return "\n\n".join(sections)