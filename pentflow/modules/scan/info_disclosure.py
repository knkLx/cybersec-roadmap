"""Information disclosure scanner"""
import asyncio
import aiohttp
from core.session import Finding


class InfoDisclosureScanner:
    def __init__(self, target: str):
        self.target = target

    async def scan(self, endpoints: list = None) -> list:
        findings = []
        base_url = self.target if self.target.startswith("http") else f"https://{self.target}"

        disclosure_paths = [
            ("/.env", "Environment file exposed", "high", "CWE-200"),
            ("/.git/config", "Git configuration exposed", "critical", "CWE-200"),
            ("/.git/HEAD", "Git repository exposed", "critical", "CWE-200"),
            ("/.svn/entries", "SVN repository exposed", "high", "CWE-200"),
            ("/robots.txt", "Robots.txt with sensitive paths", "info", "CWE-200"),
            ("/sitemap.xml", "Sitemap exposing structure", "info", "CWE-200"),
            ("/.DS_Store", "macOS metadata file exposed", "medium", "CWE-200"),
            ("/server-status", "Apache server status exposed", "medium", "CWE-200"),
            ("/server-info", "Apache server info exposed", "medium", "CWE-200"),
            ("/.htaccess", "Htaccess file accessible", "high", "CWE-200"),
            ("/web.config", "Web.config file accessible", "high", "CWE-200"),
            ("/crossdomain.xml", "Cross-domain policy file", "info", "CWE-200"),
            ("/backup.zip", "Backup file found", "critical", "CWE-530"),
            ("/backup.tar.gz", "Backup archive found", "critical", "CWE-530"),
            ("/dump.sql", "Database dump found", "critical", "CWE-530"),
            ("/.env.local", "Local environment file", "high", "CWE-200"),
            ("/.env.production", "Production env file", "critical", "CWE-200"),
            ("/phpinfo.php", "PHP info page exposed", "medium", "CWE-200"),
            ("/trace.axd", "ASP.NET trace exposed", "medium", "CWE-200"),
            ("/elmah.axd", "ELMAH error log exposed", "medium", "CWE-200"),
        ]

        async with aiohttp.ClientSession() as session:
            sem = asyncio.Semaphore(15)

            async def check(path, desc, severity, cwe):
                async with sem:
                    url = f"{base_url}{path}"
                    try:
                        async with session.get(
                            url,
                            headers={"User-Agent": "Mozilla/5.0"},
                            timeout=aiohttp.ClientTimeout(total=8),
                            allow_redirects=False,
                            ssl=False,
                        ) as resp:
                            if resp.status == 200:
                                body = await resp.read()
                                if len(body) > 0:
                                    findings.append(Finding(
                                        id=f"INFO-{path.replace('/', '-').strip('-').upper()}",
                                        title=desc,
                                        severity=severity,
                                        category="Information Disclosure",
                                        target=url,
                                        description=f"{desc} at {url}",
                                        evidence=f"Status: {resp.status}, Size: {len(body)} bytes",
                                        cwe=cwe,
                                        remediation=f"Restrict access to {path}",
                                    ))
                    except Exception:
                        pass

            tasks = [check(p, d, s, c) for p, d, s, c in disclosure_paths]
            await asyncio.gather(*tasks)

        return findings
