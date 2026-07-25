"""DNS reconnaissance"""
import asyncio
import socket
from typing import Optional


class DNSRecon:
    def __init__(self, domain: str):
        self.domain = domain

    async def _resolve(self, record_type: str) -> list:
        try:
            loop = asyncio.get_event_loop()
            results = []
            # Use basic resolution
            info = await loop.getaddrinfo(self.domain, None, family=socket.AF_INET)
            for res in info:
                ip = res[4][0]
                if ip not in results:
                    results.append(ip)
            return results
        except Exception:
            return []

    async def _check_zone_transfer(self) -> dict:
        """Check for DNS zone transfer vulnerability"""
        results = {"vulnerable": False, "records": []}
        try:
            import subprocess
            proc = await asyncio.create_subprocess_exec(
                "host", "-t", "AXFR", self.domain,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            output = stdout.decode()
            if "transfer of" in output.lower() and "failed" not in output.lower():
                results["vulnerable"] = True
                results["records"] = [line for line in output.split("\n") if line.strip()]
        except Exception:
            pass
        return results

    async def _check_wildcard(self) -> bool:
        """Check if domain uses wildcard DNS"""
        try:
            loop = asyncio.get_event_loop()
            fake = f"nonexistent12345.{self.domain}"
            await loop.getaddrinfo(fake, None, family=socket.AF_INET)
            return True
        except (socket.gaierror, OSError):
            return False

    async def recon(self) -> dict:
        ips = await self._resolve("A")
        zone = await self._check_zone_transfer()
        wildcard = await self._check_wildcard()

        return {
            "domain": self.domain,
            "ips": ips,
            "zone_transfer": zone,
            "wildcard": wildcard,
            "records": {
                "A": ips,
            }
        }
