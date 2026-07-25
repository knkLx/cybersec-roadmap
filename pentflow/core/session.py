"""Session management - save/resume pentest progress"""
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Any

from config import SESSIONS_DIR


@dataclass
class Finding:
    id: str
    title: str
    severity: str  # critical, high, medium, low, info
    category: str
    target: str
    description: str
    evidence: str = ""
    remediation: str = ""
    cvss: float = 0.0
    cwe: str = ""
    references: list = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ScanResult:
    module: str
    target: str
    data: dict = field(default_factory=dict)
    findings: list = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, error
    started_at: str = ""
    completed_at: str = ""
    error: str = ""


@dataclass
class Session:
    target: str
    session_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    status: str = "active"  # active, paused, completed
    phases: dict = field(default_factory=dict)
    findings: list = field(default_factory=list)
    notes: str = ""
    github_repo: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.session_id:
            clean_target = self.target.replace("https://", "").replace("http://", "").replace("/", "_").rstrip("_")
            self.session_id = f"{clean_target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.updated_at = datetime.now().isoformat()

    def add_finding(self, finding: Finding):
        self.findings.append(finding)
        self.updated_at = datetime.now().isoformat()

    def get_findings_by_severity(self, severity: str) -> list:
        return [f for f in self.findings if f.severity == severity]

    def summary(self) -> dict:
        return {
            "target": self.target,
            "session_id": self.session_id,
            "status": self.status,
            "total_findings": len(self.findings),
            "critical": len(self.get_findings_by_severity("critical")),
            "high": len(self.get_findings_by_severity("high")),
            "medium": len(self.get_findings_by_severity("medium")),
            "low": len(self.get_findings_by_severity("low")),
            "info": len(self.get_findings_by_severity("info")),
        }

    def save(self):
        self.updated_at = datetime.now().isoformat()
        path = SESSIONS_DIR / f"{self.session_id}.json"
        path.write_text(json.dumps(asdict(self), indent=2, default=str))

    @classmethod
    def load(cls, session_id: str) -> "Session":
        path = SESSIONS_DIR / f"{session_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Session {session_id} not found")
        data = json.loads(path.read_text())
        return cls(**data)

    @classmethod
    def list_sessions(cls) -> list:
        sessions = []
        for f in SESSIONS_DIR.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                sessions.append({
                    "session_id": data.get("session_id"),
                    "target": data.get("target"),
                    "status": data.get("status"),
                    "created_at": data.get("created_at"),
                    "findings": len(data.get("findings", [])),
                })
            except Exception:
                continue
        return sorted(sessions, key=lambda x: x["created_at"], reverse=True)
