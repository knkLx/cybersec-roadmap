import asyncio
import aiohttp
from utils.config import USER_AGENT


async def from_crtsh(domain: str) -> list[str]:
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    subdomains = set()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for entry in data:
                        name = entry.get("name_value", "")
                        for sub in name.split("\n"):
                            sub = sub.strip().lower()
                            if sub.endswith(f".{domain}") or sub == domain:
                                subdomains.add(sub)
    except Exception as e:
        print(f"[!] crt.sh error: {e}")
    return sorted(subdomains)


async def from_apis(domain: str) -> list[str]:
    subdomains = set()
    async with aiohttp.ClientSession() as session:
        # AlienVault OTX
        try:
            url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
            headers = {"User-Agent": USER_AGENT}
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for record in data.get("passive_dns", []):
                        hostname = record.get("hostname", "")
                        if hostname.endswith(f".{domain}"):
                            subdomains.add(hostname)
        except Exception:
            pass

        # ThreatCrowd
        try:
            url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={domain}"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for sub in data.get("subdomains", []):
                        subdomains.add(sub.strip().lower())
        except Exception:
            pass

    return sorted(subdomains)


async def enumerate(domain: str) -> list[str]:
    results = await asyncio.gather(
        from_crtsh(domain),
        from_apis(domain),
        return_exceptions=True,
    )
    all_subs = set()
    for result in results:
        if isinstance(result, list):
            all_subs.update(result)
    return sorted(all_subs)
