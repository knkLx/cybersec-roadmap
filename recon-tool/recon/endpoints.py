import asyncio
import aiohttp
from utils.config import USER_AGENT

COMMON_PATHS = [
    "/", "/admin", "/login", "/register", "/api", "/robots.txt",
    "/sitemap.xml", "/.env", "/.git/config", "/wp-admin",
    "/wp-login.php", "/administrator", "/backup", "/config",
    "/debug", "/test", "/staging", "/dev", "/graphql",
    "/swagger", "/api/v1", "/api/v2", "/health", "/status",
    "/actuator", "/console", "/phpmyadmin", "/adminer",
    "/.well-known/security.txt", "/favicon.ico", "/crossdomain.xml",
    "/clientaccesspolicy.xml", "/.htaccess", "/web.config",
]


async def discover(target: str, paths: list[str] | None = None) -> list[str]:
    if paths is None:
        paths = COMMON_PATHS

    base_url = target if target.startswith("http") else f"https://{target}"
    base_url = base_url.rstrip("/")

    found = []
    async with aiohttp.ClientSession() as session:
        sem = asyncio.Semaphore(20)

        async def check(path: str):
            async with sem:
                url = f"{base_url}{path}"
                try:
                    async with session.get(
                        url,
                        headers={"User-Agent": USER_AGENT},
                        timeout=aiohttp.ClientTimeout(total=10),
                        allow_redirects=False,
                        ssl=False,
                    ) as resp:
                        if resp.status not in (404, 405, 502, 503):
                            found.append(f"{url} [{resp.status}]")
                except Exception:
                    pass

        tasks = [check(p) for p in paths]
        await asyncio.gather(*tasks)

    return found
