import asyncio
from typing import Optional


COMMON_PORTS = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    80: "http", 110: "pop3", 135: "rpc", 139: "netbios",
    143: "imap", 443: "https", 445: "smb", 993: "imaps",
    995: "pop3s", 1433: "mssql", 3306: "mysql", 3389: "rdp",
    5432: "postgresql", 5900: "vnc", 8080: "http-alt", 8443: "https-alt",
    27017: "mongodb",
}


async def scan_port(host: str, port: int, timeout: float = 2.0) -> Optional[dict]:
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )
        writer.close()
        await writer.wait_closed()
        return {"port": port, "state": "open", "service": COMMON_PORTS.get(port, "?")}
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return None


async def scan(host: str, ports: list[int] | None = None, concurrency: int = 100) -> list[dict]:
    if ports is None:
        ports = list(COMMON_PORTS.keys())

    sem = asyncio.Semaphore(concurrency)

    async def bounded_scan(port: int):
        async with sem:
            return await scan_port(host, port)

    tasks = [bounded_scan(p) for p in ports]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]
