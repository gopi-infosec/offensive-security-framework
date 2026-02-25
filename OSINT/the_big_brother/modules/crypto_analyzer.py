import requests
import datetime

def analyze_crypto(address: str, coin: str):
    """
    Analyzes a crypto address for balance and activity.
    Supports BTC and ETH via free public APIs.
    """
    results = {
        "coin": coin,
        "address": address,
        "balance": 0,
        "total_received": 0,
        "tx_count": 0,
        "last_seen": "Never",
        "error": None
    }
    
    try:
        if coin.lower() == "btc":
            # using blockchain.info API
            url = f"https://blockchain.info/rawaddr/{address}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # satoshis to BTC
                results["balance"] = data.get("final_balance", 0) / 100000000
                results["total_received"] = data.get("total_received", 0) / 100000000
                results["tx_count"] = data.get("n_tx", 0)
                
                txs = data.get("txs", [])
                if txs:
                    last_time = txs[0].get("time") # timestamp
                    if last_time:
                        results["last_seen"] = datetime.datetime.fromtimestamp(last_time).strftime('%Y-%m-%d %H:%M:%S')
            else:
                 results["error"] = f"API returned {resp.status_code}"
                 
        elif coin.lower() == "eth":
            # using blockcypher for ETH (rate limited but works for demo)
            # or could use etherscan if key provided, but we want zero-conf
            # Let's try blockchain.info/eth is not standard.
            # Using blockcypher
            url = f"https://api.blockcypher.com/v1/eth/main/addrs/{address}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # wei to ETH
                results["balance"] = data.get("balance", 0) / 10**18
                results["total_received"] = data.get("total_received", 0) / 10**18
                results["tx_count"] = data.get("n_tx", 0)
                
                # Check for last tx if available in basic view
                # Blockcypher might not return txs list in summary unless asked
                # but 'n_tx' confirms activity
                results["last_seen"] = "Check Explorer" # Simplified for this API
            else:
                 results["error"] = f"API returned {resp.status_code}"
    
    except Exception as e:
        results["error"] = str(e)
        
    return results
