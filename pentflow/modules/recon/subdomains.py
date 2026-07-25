"""Subdomain enumeration from multiple sources"""
import asyncio
import aiohttp
from config import COMMON_SUBDOMAINS


class SubdomainEnumerator:
    def __init__(self, domain: str):
        self.domain = domain
        self.subdomains = set()

    async def _from_crtsh(self) -> set:
        url = f"https://crt.sh/?q=%25.{self.domain}&output=json"
        results = set()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for entry in data:
                            name = entry.get("name_value", "")
                            for sub in name.split("\n"):
                                sub = sub.strip().lower()
                                if sub.endswith(f".{self.domain}") or sub == self.domain:
                                    results.add(sub)
        except Exception:
            pass
        return results

    async def _from_alienvault(self) -> set:
        results = set()
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://otx.alienvault.com/api/v1/indicators/domain/{self.domain}/passive_dns"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for r in data.get("passive_dns", []):
                            h = r.get("hostname", "")
                            if h.endswith(f".{self.domain}"):
                                results.add(h)
        except Exception:
            pass
        return results

    async def _from_threatcrowd(self) -> set:
        results = set()
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={self.domain}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for sub in data.get("subdomains", []):
                            results.add(sub.strip().lower())
        except Exception:
            pass
        return results

    async def _dns_bruteforce(self) -> set:
        import socket
        results = set()
        for sub in COMMON_SUBDOMAINS:
            domain = f"{sub}.{self.domain}"
            try:
                loop = asyncio.get_event_loop()
                await loop.getaddrinfo(domain, None, family=socket.AF_INET)
                results.add(domain)
            except (socket.gaierror, OSError):
                pass
        return results

    async def enumerate(self) -> list:
        tasks = [
            self._from_crtsh(),
            self._from_alienvault(),
            self._from_threatcrowd(),
            self._dns_bruteforce(),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, set):
                self.subdomains.update(r)
        return sorted(self.subdomains)
