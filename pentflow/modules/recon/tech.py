"""Technology fingerprinting"""
import aiohttp
from config import TECH_SIGNATURES


class TechDetector:
    def __init__(self, target: str):
        self.target = target

    async def detect(self) -> list:
        url = self.target if self.target.startswith("http") else f"https://{self.target}"
        found = set()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                    timeout=aiohttp.ClientTimeout(total=15),
                    allow_redirects=True,
                    ssl=False,
                ) as resp:
                    headers = {k.lower(): v for k, v in resp.headers.items()}
                    body = await resp.text()
                    combined = f"{headers.get('server', '')} {headers.get('x-powered-by', '')}".lower()
                    body_lower = body.lower()
                    for tech, sigs in TECH_SIGNATURES.items():
                        if any(s.lower() in combined for s in sigs) or any(s.lower() in body_lower for s in sigs):
                            found.add(tech)
        except Exception:
            pass
        return sorted(found)
