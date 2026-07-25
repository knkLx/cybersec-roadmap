"""Security header analysis"""
import aiohttp
from core.session import Finding

SECURITY_HEADERS = {
    "Strict-Transport-Security": {"severity": "high", "cwe": "CWE-523", "desc": "HSTS not set"},
    "Content-Security-Policy": {"severity": "medium", "cwe": "CWE-693", "desc": "CSP not set"},
    "X-Frame-Options": {"severity": "medium", "cwe": "CWE-1021", "desc": "Clickjacking protection missing"},
    "X-Content-Type-Options": {"severity": "low", "cwe": "CWE-693", "desc": "MIME sniffing not prevented"},
    "X-XSS-Protection": {"severity": "info", "cwe": "CWE-79", "desc": "XSS filter not set"},
    "Referrer-Policy": {"severity": "low", "cwe": "CWE-200", "desc": "Referrer policy not set"},
    "Permissions-Policy": {"severity": "low", "cwe": "CWE-693", "desc": "Permissions policy not set"},
}

DANGEROUS_HEADERS = {
    "X-Powered-By": {"severity": "info", "desc": "Server technology disclosed"},
    "Server": {"severity": "info", "desc": "Server version disclosed"},
    "X-AspNet-Version": {"severity": "info", "desc": "ASP.NET version disclosed"},
    "X-AspNetMvc-Version": {"severity": "info", "desc": "ASP.NET MVC version disclosed"},
}


class HeaderAnalyzer:
    def __init__(self, target: str):
        self.target = target

    async def analyze(self) -> list:
        findings = []
        url = self.target if self.target.startswith("http") else f"https://{self.target}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=aiohttp.ClientTimeout(total=15),
                    ssl=False,
                ) as resp:
                    headers = {k.lower(): v for k, v in resp.headers.items()}

                    # Check missing security headers
                    for header, info in SECURITY_HEADERS.items():
                        if header.lower() not in headers:
                            findings.append(Finding(
                                id=f"HEADER-MISSING-{header.upper()}",
                                title=f"Missing {header}",
                                severity=info["severity"],
                                category="Security Headers",
                                target=url,
                                description=info["desc"],
                                cwe=info["cwe"],
                                remediation=f"Add '{header}' header to HTTP responses",
                            ))

                    # Check dangerous headers
                    for header, info in DANGEROUS_HEADERS.items():
                        if header.lower() in headers:
                            value = headers[header.lower()]
                            findings.append(Finding(
                                id=f"HEADER-DISCLOSED-{header.upper()}",
                                title=f"Information Disclosure: {header}",
                                severity=info["severity"],
                                category="Information Disclosure",
                                target=url,
                                description=f"{info['desc']}: {value}",
                                evidence=f"{header}: {value}",
                                remediation=f"Remove or obfuscate '{header}' header",
                            ))

                    # Check for missing cookie security
                    for cookie_header in ["set-cookie"]:
                        if cookie_header in headers:
                            cookie_val = headers[cookie_header]
                            if "secure" not in cookie_val.lower():
                                findings.append(Finding(
                                    id="COOKIE-NO-SECURE",
                                    title="Cookie without Secure flag",
                                    severity="medium",
                                    category="Cookie Security",
                                    target=url,
                                    description="Cookie set without Secure flag",
                                    evidence=cookie_val[:200],
                                    remediation="Add 'Secure' flag to cookies",
                                ))
                            if "httponly" not in cookie_val.lower():
                                findings.append(Finding(
                                    id="COOKIE-NO-HTTPOONLY",
                                    title="Cookie without HttpOnly flag",
                                    severity="medium",
                                    category="Cookie Security",
                                    target=url,
                                    description="Cookie set without HttpOnly flag",
                                    evidence=cookie_val[:200],
                                    remediation="Add 'HttpOnly' flag to cookies",
                                ))

        except Exception as e:
            findings.append(Finding(
                id="HEADER-SCAN-ERROR",
                title="Header scan error",
                severity="info",
                category="Scan Error",
                target=url,
                description=str(e),
            ))

        return findings
