import aiohttp
from typing import List, Dict

class CORSChecker:
    def __init__(self, target_url: str):
        self.target_url = target_url

    async def check(self) -> List[Dict]:
        vulnerabilities = []

        test_origins = [
            "https://evil.com",
            "null",
            "https://attacker.target.com"
        ]

        try:
            async with aiohttp.ClientSession() as session:
                for origin in test_origins:

                    headers = {"Origin": origin}

                    async with session.get(
                        self.target_url,
                        headers=headers,
                        timeout=10
                    ) as response:

                        acao = response.headers.get(
                            "Access-Control-Allow-Origin", ""
                        )

                        acc = response.headers.get(
                            "Access-Control-Allow-Credentials", ""
                        )

                        # wildcard
                        if acao == "*":
                            vulnerabilities.append({
                                "title": "CORS wildcard origin",
                                "severity": "medium",
                                "description": "Server allows any origin (*)",
                                "evidence": acao
                            })

                        # reflected origin
                        if acao == origin and origin != "":
                            vulnerabilities.append({
                                "title": "Reflected CORS origin",
                                "severity": "high" if acc == "true" else "medium",
                                "description": "Origin is reflected in ACAO header",
                                "origin_tested": origin,
                                "credentials": acc
                            })

                        # null origin allowed
                        if acao == "null":
                            vulnerabilities.append({
                                "title": "Null origin allowed",
                                "severity": "medium",
                                "description": "Server allows Origin: null"
                            })

        except Exception as e:
            print(f"CORS check error: {e}")

        return vulnerabilities
