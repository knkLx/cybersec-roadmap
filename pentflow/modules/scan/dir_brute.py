"""Directory and file bruteforce discovery"""
import asyncio
import aiohttp
from urllib.parse import urljoin
from core.session import Finding


# Common paths for web applications
COMMON_DIRS = [
    "/", "/admin", "/admin/", "/login", "/dashboard", "/panel",
    "/api", "/api/v1", "/api/v2", "/graphql", "/swagger",
    "/.env", "/.git", "/.git/config", "/.git/HEAD", "/.svn",
    "/robots.txt", "/sitemap.xml", "/.well-known/security.txt",
    "/wp-admin", "/wp-login.php", "/wp-content", "/wp-includes",
    "/backup", "/backups", "/config", "/configuration",
    "/debug", "/console", "/phpinfo.php", "/info.php",
    "/server-status", "/server-info",
    "/test", "/testing", "/staging", "/dev", "/development",
    "/uploads", "/upload", "/files", "/media", "/static",
    "/assets", "/images", "/img", "/css", "/js",
    "/cgi-bin", "/scripts", "/bin", "/lib",
    "/tmp", "/temp", "/cache",
    "/docs", "/documentation", "/help",
    "/api/docs", "/api/swagger.json", "/api/swagger.yaml",
    "/graphql/console",
    "/.DS_Store", "/Thumbs.db",
    "/crossdomain.xml", "/clientaccesspolicy.xml",
    "/elmah.axd", "/trace.axd",
    "/actuator", "/actuator/health", "/actuator/env",
    "/metrics", "/prometheus",
]

# Tech-specific paths
TECH_PATHS = {
    "wordpress": ["/wp-json/wp/v2/users", "/xmlrpc.php", "/wp-json/"],
    "laravel": ["/.env", "/storage/logs/laravel.log", "/telescope"],
    "django": ["/admin/", "/django-admin/", "/static/admin/"],
    "spring": ["/actuator", "/actuator/env", "/actuator/health"],
    "express": ["/api/", "/graphql"],
    "rails": ["/rails/mailers", "/rails/info"],
    "next": ["/_next/data/", "/api/"],
    "nuxt": ["/_nuxt/", "/api/"],
}


class DirectoryBruteforcer:
    def __init__(self, target: str, threads: int = 20):
        self.target = target
        self.base_url = target if target.startswith("http") else f"https://{target}"
        self.threads = threads
        self.found = []

    async def _check_path(self, session: aiohttp.ClientSession, path: str) -> dict:
        url = urljoin(self.base_url, path)
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=8),
                allow_redirects=False,
                ssl=False,
            ) as resp:
                if resp.status not in [404, 405, 406, 500, 502, 503]:
                    return {
                        "url": url,
                        "path": path,
                        "status": resp.status,
                        "size": len(await resp.text()),
                        "redirect": resp.headers.get("Location", ""),
                    }
        except Exception:
            pass
        return None

    async def _bruteforce_batch(self, paths: list) -> list:
        results = []
        connector = aiohttp.TCPConnector(limit=self.threads)
        async with aiohttp.ClientSession(connector=connector) as session:
            semaphore = asyncio.Semaphore(self.threads)

            async def limited_check(path):
                async with semaphore:
                    return await self._check_path(session, path)

            tasks = [limited_check(p) for p in paths]
            for result in await asyncio.gather(*tasks, return_exceptions=True):
                if result and isinstance(result, dict):
                    results.append(result)
        return results

    async def scan(self, technologies: list = None) -> list:
        findings = []

        # Build path list
        paths = list(COMMON_DIRS)

        # Add tech-specific paths
        if technologies:
            tech_str = " ".join(technologies).lower()
            for tech, extra_paths in TECH_PATHS.items():
                if tech in tech_str:
                    paths.extend(extra_paths)

        # Remove duplicates
        paths = list(set(paths))

        # Run bruteforce
        results = await self._bruteforce_batch(paths)
        self.found = results

        # Create findings
        for r in results:
            severity = "info"
            if r["status"] in [200, 301, 302]:
                path = r["path"].lower()
                if any(s in path for s in [".env", ".git", "backup", "config", "debug", ".svn"]):
                    severity = "high"
                elif any(s in path for s in ["admin", "dashboard", "panel", "console"]):
                    severity = "medium"
                elif any(s in path for s in ["phpinfo", "server-status", "actuator", "swagger"]):
                    severity = "medium"

            findings.append(Finding(
                id=f"DIR-{r['status']}-{r['path'].replace('/', '-').strip('-')[:30]}",
                title=f"Directory found: {r['path']} ({r['status']})",
                severity=severity,
                category="Directory Discovery",
                target=r["url"],
                description=f"Accessible path found: {r['path']} (HTTP {r['status']})",
                evidence=f"Status: {r['status']}, Size: {r['size']} bytes",
            ))

        return findings
