"""Nuclei integration - run Nuclei templates against targets"""
import asyncio
import json
import os
from pathlib import Path
from core.session import Finding


class NucleiScanner:
    def __init__(self, target: str):
        self.target = target
        self.nuclei_path = self._find_nuclei()

    def _find_nuclei(self) -> str:
        """Find nuclei binary"""
        candidates = [
            os.path.expanduser("~/.local/bin/nuclei"),
            "/usr/local/bin/nuclei",
            "/usr/bin/nuclei",
        ]
        for c in candidates:
            if os.path.isfile(c) and os.access(c, os.X_OK):
                return c
        return "nuclei"  # fallback to PATH

    async def scan(
        self,
        templates: list = None,
        severity: str = "low,medium,high,critical",
        rate_limit: int = 150,
        concurrency: int = 25,
        timeout: int = 120,  # Reduced from 600 to 120s
        tags: list = None,
        exclude_tags: list = None,
    ) -> list:
        """Run nuclei against target"""
        findings = []

        cmd = [
            self.nuclei_path,
            "-u", self.target,
            "-jsonl",
            "-severity", severity,
            "-rate-limit", str(rate_limit),
            "-concurrency", str(concurrency),
            "-timeout", "10",
            "-no-color",
            "-silent",
        ]

        if templates:
            for t in templates:
                cmd.extend(["-t", t])
        else:
            # Use default templates directory
            templates_dir = os.path.expanduser("~/nuclei-templates")
            if os.path.isdir(templates_dir):
                cmd.extend(["-t", templates_dir])

        if tags:
            cmd.extend(["-tags", ",".join(tags)])

        if exclude_tags:
            cmd.extend(["-exclude-tags", ",".join(exclude_tags)])

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            output = stdout.decode(errors="ignore")

            for line in output.strip().split("\n"):
                if not line.strip():
                    continue
                try:
                    result = json.loads(line)
                    finding = self._parse_result(result)
                    if finding:
                        findings.append(finding)
                except json.JSONDecodeError:
                    continue

        except asyncio.TimeoutError:
            findings.append(Finding(
                id="NUCLEI-TIMEOUT",
                title="Nuclei scan timed out",
                severity="info",
                category="Scan Error",
                target=self.target,
                description=f"Nuclei scan exceeded {timeout}s timeout",
            ))
        except FileNotFoundError:
            findings.append(Finding(
                id="NUCLEI-NOT-FOUND",
                title="Nuclei binary not found",
                severity="info",
                category="Scan Error",
                target=self.target,
                description="Nuclei binary not found. Install from: https://github.com/projectdiscovery/nuclei",
            ))
        except Exception as e:
            findings.append(Finding(
                id="NUCLEI-ERROR",
                title="Nuclei scan error",
                severity="info",
                category="Scan Error",
                target=self.target,
                description=str(e),
            ))

        return findings

    def _parse_result(self, result: dict) -> Finding:
        """Parse nuclei JSON result into a Finding"""
        info = result.get("info", {})
        template_id = result.get("template-id", "unknown")
        matched_at = result.get("matched-at", result.get("host", ""))
        severity = info.get("severity", "info").lower()
        name = info.get("name", template_id)
        description = info.get("description", "")
        reference = info.get("reference", [])
        tags = info.get("tags", "")
        classification = result.get("classification", {})
        cwe = classification.get("cwe-id", [])
        cvss_score = classification.get("cvss-score", 0)

        # Map nuclei severity to our severity
        severity_map = {
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low",
            "info": "info",
            "unknown": "info",
        }
        our_severity = severity_map.get(severity, "info")

        # Build evidence
        evidence_parts = [f"Template: {template_id}"]
        if matched_at:
            evidence_parts.append(f"Matched at: {matched_at}")
        if result.get("matcher-name"):
            evidence_parts.append(f"Matcher: {result['matcher-name']}")
        if result.get("extracted-results"):
            evidence_parts.append(f"Extracted: {', '.join(result['extracted-results'][:5])}")
        if result.get("curl-command"):
            evidence_parts.append(f"curl: {result['curl-command'][:200]}")

        return Finding(
            id=f"NUCLEI-{template_id.upper()}",
            title=name,
            severity=our_severity,
            category="Nuclei",
            target=matched_at or self.target,
            description=description or f"Nuclei template '{template_id}' matched",
            evidence="\n".join(evidence_parts),
            cwe=cwe[0] if isinstance(cwe, list) and cwe else str(cwe) if cwe else "",
            cvss=cvss_score if isinstance(cvss_score, (int, float)) else 0,
            references=reference if isinstance(reference, list) else [reference] if reference else [],
        )

    async def scan_with_tags(self, tags: str) -> list:
        """Scan with specific tags (e.g., 'cve,xss,sqli')"""
        return await self.scan(tags=tags.split(","))

    async def scan_critical_only(self) -> list:
        """Scan for critical and high severity only"""
        return await self.scan(severity="high,critical")

    async def scan_by_template(self, template_path: str) -> list:
        """Scan with a specific template or directory"""
        return await self.scan(templates=[template_path])
