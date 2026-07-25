"""General vulnerability scanner"""
import aiohttp
import re
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from core.session import Finding


class VulnScanner:
    def __init__(self, target: str):
        self.target = target

    async def _check_open_redirect(self, url: str) -> list:
        findings = []
        redirect_params = ["url", "redirect", "next", "return", "goto", "dest", "redir"]
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        for param in redirect_params:
            if param in params or not params:
                test_url = f"{url}{'&' if '?' in url else '?'}{param}=https://evil.com"
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            test_url,
                            timeout=aiohttp.ClientTimeout(total=8),
                            allow_redirects=False,
                            ssl=False,
                        ) as resp:
                            location = resp.headers.get("Location", "")
                            if "evil.com" in location:
                                findings.append(Finding(
                                    id=f"VULN-OPEN-REDIRECT-{param.upper()}",
                                    title=f"Open Redirect via {param} parameter",
                                    severity="medium",
                                    category="Open Redirect",
                                    target=test_url,
                                    description=f"Parameter '{param}' redirects to external URL",
                                    evidence=f"Redirect to: {location}",
                                    cwe="CWE-601",
                                    remediation="Validate and sanitize redirect URLs",
                                ))
                except Exception:
                    pass
        return findings

    async def _check_cors(self, url: str) -> list:
        findings = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.options(
                    url,
                    headers={
                        "Origin": "https://evil.com",
                        "Access-Control-Request-Method": "GET",
                    },
                    timeout=aiohttp.ClientTimeout(total=8),
                    ssl=False,
                ) as resp:
                    acao = resp.headers.get("Access-Control-Allow-Origin", "")
                    if acao == "*" or "evil.com" in acao:
                        findings.append(Finding(
                            id="VULN-CORS-MISCONFIG",
                            title="CORS Misconfiguration",
                            severity="medium",
                            category="CORS",
                            target=url,
                            description="Server reflects arbitrary Origin in CORS headers",
                            evidence=f"ACAO: {acao}",
                            cwe="CWE-942",
                            remediation="Whitelist trusted origins only",
                        ))
        except Exception:
            pass
        return findings

    async def _check_clickjacking(self, url: str) -> list:
        findings = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=8),
                    ssl=False,
                ) as resp:
                    xfo = resp.headers.get("X-Frame-Options", "").lower()
                    csp = resp.headers.get("Content-Security-Policy", "").lower()
                    if not xfo and "frame-ancestors" not in csp:
                        findings.append(Finding(
                            id="VULN-CLICKJACKING",
                            title="Clickjacking vulnerability",
                            severity="medium",
                            category="Clickjacking",
                            target=url,
                            description="Page can be embedded in iframes",
                            cwe="CWE-1021",
                            remediation="Set X-Frame-Options or CSP frame-ancestors",
                        ))
        except Exception:
            pass
        return findings

    async def _check_sensitive_endpoints(self, endpoints: list) -> list:
        findings = []
        sensitive_patterns = {
            r"/admin": "Admin panel accessible",
            r"/debug": "Debug endpoint accessible",
            r"/api/.*key": "API key endpoint accessible",
            r"/graphql": "GraphQL endpoint accessible",
            r"/swagger": "API documentation exposed",
            r"/actuator": "Actuator endpoint accessible",
        }

        for ep in endpoints:
            url = ep.get("url", "")
            for pattern, desc in sensitive_patterns.items():
                if re.search(pattern, url, re.IGNORECASE):
                    findings.append(Finding(
                        id=f"VULN-SENSITIVE-{url.split('/')[-1].upper()}",
                        title=desc,
                        severity="low",
                        category="Sensitive Endpoint",
                        target=url,
                        description=f"{desc}: {url}",
                        evidence=f"HTTP {ep.get('status', '?')}",
                    ))
        return findings

    async def scan(self, endpoints: list = None, technologies: list = None) -> list:
        findings = []
        base_url = self.target if self.target.startswith("http") else f"https://{self.target}"

        # Open redirect
        redirect_findings = await self._check_open_redirect(base_url)
        findings.extend(redirect_findings)

        # CORS
        cors_findings = await self._check_cors(base_url)
        findings.extend(cors_findings)

        # Clickjacking
        cj_findings = await self._check_clickjacking(base_url)
        findings.extend(cj_findings)

        # Sensitive endpoints
        if endpoints:
            se_findings = await self._check_sensitive_endpoints(endpoints)
            findings.extend(se_findings)

        return findings
