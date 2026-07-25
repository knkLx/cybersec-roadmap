"""Endpoint and directory discovery"""
import asyncio
import aiohttp
from config import COMMON_PATHS, COMMON_SUBDOMAINS


class EndpointDiscovery:
    def __init__(self, target: str):
        self.target = target

    async def discover(self, subdomains: list = None, paths: list = None) -> list:
        if paths is None:
            paths = COMMON_PATHS

        base_url = self.target if self.target.startswith("http") else f"https://{self.target}"
        base_url = base_url.rstrip("/")

        targets = [base_url]
        if subdomains:
            for sub in subdomains[:20]:
                t = f"https://{sub}"
                if t not in targets:
                    targets.append(t)

        found = []
        async with aiohttp.ClientSession() as session:
            sem = asyncio.Semaphore(20)

            async def check(base, path):
                async with sem:
                    url = f"{base}{path}"
                    try:
                        async with session.get(
                            url,
                            headers={"User-Agent": "Mozilla/5.0"},
                            timeout=aiohttp.ClientTimeout(total=8),
                            allow_redirects=False,
                            ssl=False,
                        ) as resp:
                            if resp.status not in (404, 405, 502, 503, 500):
                                found.append({
                                    "url": url,
                                    "status": resp.status,
                                    "size": len(await resp.read()),
                                })
                    except Exception:
                        pass

            tasks = []
            for base in targets[:10]:
                for path in paths:
                    tasks.append(check(base, path))
            await asyncio.gather(*tasks)

        return found
