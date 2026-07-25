"""Bug Bounty Scope Checker — verifica que el target esté en scope antes de escanear"""
import aiohttp
from urllib.parse import urlparse
from core.session import Finding


# Known bug bounty programs and their scopes
BUG_BOUNTY_PROGRAMS = {
    "shopify.com": {
        "name": "Shopify",
        "platform": "HackerOne",
        "scope": ["*.shopify.com", "shopify.com"],
        "out_of_scope": ["*.myshopify.com", "partners.shopify.com"],
        "url": "https://hackerone.com/shopify",
    },
    "slack.com": {
        "name": "Slack",
        "platform": "HackerOne",
        "scope": ["*.slack.com", "slack.com", "api.slack.com"],
        "out_of_scope": ["*.slack-status.com"],
        "url": "https://hackerone.com/slack",
    },
    "starbucks.com": {
        "name": "Starbucks",
        "platform": "HackerOne",
        "scope": ["*.starbucks.com", "starbucks.com"],
        "out_of_scope": [],
        "url": "https://hackerone.com/starbucks",
    },
    "automattic.com": {
        "name": "Automattic",
        "platform": "HackerOne",
        "scope": ["*.wordpress.com", "*.wordpress.org", "*.automattic.com", "akismet.com"],
        "out_of_scope": [],
        "url": "https://hackerone.com/automattic",
    },
    "gitlab.com": {
        "name": "GitLab",
        "platform": "HackerOne",
        "scope": ["*.gitlab.com", "gitlab.com"],
        "out_of_scope": ["*.gitlab.io"],
        "url": "https://hackerone.com/gitlab",
    },
}


class ScopeChecker:
    def __init__(self, target: str):
        self.target = target
        self.domain = self._extract_domain(target)

    def _extract_domain(self, target: str) -> str:
        """Extract root domain from target"""
        parsed = urlparse(target if target.startswith("http") else f"https://{target}")
        host = parsed.hostname or target
        # Remove www.
        if host.startswith("www."):
            host = host[4:]
        return host.lower()

    def _check_program_scope(self, domain: str) -> dict:
        """Check if domain matches any known bug bounty program"""
        for program_domain, program_info in BUG_BOUNTY_PROGRAMS.items():
            # Check if target matches program
            if domain == program_domain or domain.endswith(f".{program_domain}"):
                # Check out of scope
                for oos in program_info["out_of_scope"]:
                    oos_pattern = oos.replace("*", "")
                    if domain.endswith(oos_pattern.lstrip(".")):
                        return {
                            "in_scope": False,
                            "program": program_info["name"],
                            "reason": f"Domain is out of scope: {oos}",
                            "url": program_info["url"],
                        }

                return {
                    "in_scope": True,
                    "program": program_info["name"],
                    "platform": program_info["platform"],
                    "url": program_info["url"],
                }

        return {"in_scope": None, "program": "Unknown", "reason": "Not a recognized bug bounty program"}

    async def check_headers(self) -> dict:
        """Check target for security.txt and bug bounty policy"""
        result = {"has_security_txt": False, "has_policy": False, "urls": []}
        base_url = self.target if self.target.startswith("http") else f"https://{self.target}"

        check_urls = [
            "/.well-known/security.txt",
            "/security.txt",
            "/.well-known/openid-configuration",
        ]

        async with aiohttp.ClientSession() as session:
            for path in check_urls:
                try:
                    url = f"{base_url}{path}"
                    async with session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=8),
                        ssl=False,
                        allow_redirects=True,
                    ) as resp:
                        if resp.status == 200:
                            body = await resp.text()
                            if "security" in path:
                                result["has_security_txt"] = True
                                result["urls"].append(url)
                            if "hackerone" in body.lower() or "bugbounty" in body.lower() or "responsible disclosure" in body.lower():
                                result["has_policy"] = True
                except Exception:
                    pass

        return result

    async def check(self) -> list:
        findings = []

        # Check known programs
        program_check = self._check_program_scope(self.domain)

        if program_check["in_scope"] is True:
            findings.append(Finding(
                id="SCOPE-IN-SCOPE",
                title=f"In Bug Bounty Scope: {program_check['program']}",
                severity="info",
                category="Scope Check",
                target=self.domain,
                description=f"Target is in scope for {program_check['program']} bug bounty program on {program_check.get('platform', 'Unknown')}",
                evidence=f"Program: {program_check['program']}\nURL: {program_check.get('url', 'N/A')}",
                remediation="Review program rules before scanning. Use responsible disclosure.",
            ))
        elif program_check["in_scope"] is False:
            findings.append(Finding(
                id="SCOPE-OUT-OF-SCOPE",
                title=f"OUT OF SCOPE: {program_check['program']}",
                severity="critical",
                category="Scope Check",
                target=self.domain,
                description=f"Target is OUT OF SCOPE for {program_check['program']}. DO NOT scan.",
                evidence=f"Reason: {program_check['reason']}",
                remediation="STOP. This target is explicitly excluded from the bug bounty program.",
            ))
        else:
            findings.append(Finding(
                id="SCOPE-UNKNOWN",
                title="Unknown Bug Bounty Scope",
                severity="info",
                category="Scope Check",
                target=self.domain,
                description="Target is not a recognized bug bounty program. Ensure you have authorization before scanning.",
                evidence="Not found in known bug bounty program database",
                remediation="Verify authorization before testing. Check for security.txt.",
            ))

        # Check for security.txt
        headers_check = await self.check_headers()
        if headers_check["has_security_txt"]:
            findings.append(Finding(
                id="SCOPE-SECURITY-TXT",
                title="security.txt Found",
                severity="info",
                category="Scope Check",
                target=self.domain,
                description="Target has security.txt with disclosure policy information",
                evidence=f"URLs: {', '.join(headers_check['urls'])}",
            ))

        return findings
