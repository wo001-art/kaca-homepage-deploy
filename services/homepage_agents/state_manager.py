#!/usr/bin/env python3
"""프로젝트 상태 관리 (JSON 기반).

프로젝트 디렉토리 구조:
    C:/Users/Administrator/Documents/ClaudeCodeHub/homepage-projects/{slug}/
    ├── project_state.json
    ├── research/
    ├── planning/
    ├── design/
    ├── frontend/
    ├── backend/
    └── reports/
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path


PROJECTS_ROOT = Path("C:/Users/Administrator/Documents/ClaudeCodeHub/homepage-projects")

CHECKLIST_FILE = Path(__file__).resolve().parent / "package_checklist.json"

PACKAGE_TIERS = ["basic", "standard", "premium"]

PHASES = ["intake", "research", "planning", "design", "frontend", "backend", "review", "deploy", "done"]

AGENT_KEYS = ["research", "planning", "design", "frontend", "backend"]

APPROVAL_TYPES = ["estimate", "sitemap", "design", "final"]

SUBDIRS = [
    "research",
    "planning",
    "design/components",
    "design/mockups",
    "frontend/nextjs-app",
    "backend",
    "reports",
]


def _slugify(name: str) -> str:
    """프로젝트명을 URL-safe slug로 변환."""
    slug = re.sub(r"[^\w가-힣-]", "-", name.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "project"


class StateManager:
    """프로젝트 상태 CRUD.

    사용법:
        sm = StateManager("kaca-2026")          # 기존 프로젝트 로드
        sm = StateManager.create("KACA 홈페이지", form_data)  # 신규 생성
        sm.update_agent("research", status="done", summary="...")
        sm.advance_phase("planning")
        sm.save()
    """

    def __init__(self, slug: str):
        self.slug = slug
        self.project_dir = PROJECTS_ROOT / slug
        self.state_file = self.project_dir / "project_state.json"
        if self.state_file.exists():
            self.state = json.loads(self.state_file.read_text(encoding="utf-8"))
        else:
            raise FileNotFoundError(f"프로젝트 없음: {self.state_file}")

    @classmethod
    def create(cls, project_name: str, form_data: dict | None = None,
               estimate: dict | None = None, slug: str | None = None) -> "StateManager":
        """신규 프로젝트 생성 + 디렉토리 구조 초기화."""
        slug = slug or _slugify(project_name)
        project_dir = PROJECTS_ROOT / slug

        # 디렉토리 생성
        for subdir in SUBDIRS:
            (project_dir / subdir).mkdir(parents=True, exist_ok=True)

        now = datetime.now().isoformat(timespec="seconds")

        state = {
            "project_id": slug,
            "project_name": project_name,
            "phase": "intake",
            "package_tier": None,
            "package_label": None,
            "package_pages": None,
            "package_checklist": {},
            "package_not_included": [],
            "created_at": now,
            "updated_at": now,
            "form_data": form_data or {},
            "estimate": estimate or {},
            "agents": {
                key: {"status": "pending", "output_files": [], "summary": None}
                for key in AGENT_KEYS
            },
            "approvals": [
                {"type": t, "status": "pending", "approved_at": None}
                for t in APPROVAL_TYPES
            ],
        }

        state_file = project_dir / "project_state.json"
        state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

        return cls(slug)

    # ── 조회 ──

    @property
    def phase(self) -> str:
        return self.state["phase"]

    @property
    def project_name(self) -> str:
        return self.state["project_name"]

    def agent(self, name: str) -> dict:
        return self.state["agents"][name]

    def approval(self, approval_type: str) -> dict:
        for a in self.state["approvals"]:
            if a["type"] == approval_type:
                return a
        raise KeyError(f"승인 타입 없음: {approval_type}")

    def summary(self) -> dict:
        """Discord 보고용 요약."""
        agents_summary = {
            k: v["status"] for k, v in self.state["agents"].items()
        }
        pending_approvals = [
            a["type"] for a in self.state["approvals"] if a["status"] == "pending"
        ]
        result = {
            "project": self.state["project_name"],
            "phase": self.state["phase"],
            "agents": agents_summary,
            "pending_approvals": pending_approvals,
        }
        if self.state.get("package_tier"):
            verify = self.verify_package_checklist()
            result["package"] = {
                "tier": verify["tier"],
                "progress": f"{verify['done']}/{verify['total']}",
                "rate": verify["rate"],
                "missing_count": len(verify["missing"]),
            }
        return result

    # ── 수정 ──

    def advance_phase(self, new_phase: str) -> None:
        """프로젝트 단계 전환."""
        if new_phase not in PHASES:
            raise ValueError(f"유효하지 않은 단계: {new_phase}. 가능: {PHASES}")
        self.state["phase"] = new_phase
        self._touch()

    def update_agent(self, agent_name: str, **kwargs) -> None:
        """에이전트 상태 업데이트.

        kwargs: status, summary, output_files (list)
        """
        if agent_name not in self.state["agents"]:
            raise KeyError(f"에이전트 없음: {agent_name}")
        agent = self.state["agents"][agent_name]
        for key in ("status", "summary"):
            if key in kwargs:
                agent[key] = kwargs[key]
        if "output_files" in kwargs:
            agent["output_files"] = kwargs["output_files"]
        elif "add_file" in kwargs:
            agent["output_files"].append(kwargs["add_file"])
        self._touch()

    def set_approval(self, approval_type: str, status: str) -> None:
        """승인 상태 변경 (pending/approved/rejected)."""
        for a in self.state["approvals"]:
            if a["type"] == approval_type:
                a["status"] = status
                if status == "approved":
                    a["approved_at"] = datetime.now().isoformat(timespec="seconds")
                self._touch()
                return
        raise KeyError(f"승인 타입 없음: {approval_type}")

    def update_estimate(self, estimate: dict) -> None:
        """견적 정보 갱신."""
        self.state["estimate"] = estimate
        self._touch()

    # ── 패키지 체크리스트 ──

    def set_package(self, tier: str) -> dict:
        """패키지 설정 + 체크리스트 자동 로드.

        Args:
            tier: "basic" | "standard" | "premium"

        Returns:
            {"tier": str, "checklist_count": int, "items": list[str]}
        """
        tier = tier.lower()
        if tier not in PACKAGE_TIERS:
            raise ValueError(f"유효하지 않은 패키지: {tier}. 가능: {PACKAGE_TIERS}")

        checklist_data = json.loads(CHECKLIST_FILE.read_text(encoding="utf-8"))
        pkg = checklist_data[tier]

        # 체크리스트 초기화 (모두 미완료)
        checklist = {}
        for key, item in pkg["checklist"].items():
            checklist[key] = {
                "label": item["label"],
                "scope": item["scope"],
                "done": False,
                "done_at": None,
                "done_by": None,
            }

        self.state["package_tier"] = tier
        self.state["package_label"] = pkg["label"]
        self.state["package_pages"] = pkg["pages"]
        self.state["package_checklist"] = checklist
        self.state["package_not_included"] = pkg.get("not_included", [])
        self._touch()

        return {
            "tier": tier,
            "checklist_count": len(checklist),
            "items": [v["label"] for v in checklist.values()],
        }

    def mark_checklist(self, key: str, agent: str = None) -> bool:
        """체크리스트 항목 완료 처리.

        Args:
            key: 체크리스트 항목 키 (예: "page_main", "func_responsive")
            agent: 완료 처리한 에이전트명

        Returns:
            True if marked, False if already done or key not found
        """
        checklist = self.state.get("package_checklist", {})
        if key not in checklist:
            return False
        if checklist[key]["done"]:
            return False
        checklist[key]["done"] = True
        checklist[key]["done_at"] = datetime.now().isoformat(timespec="seconds")
        checklist[key]["done_by"] = agent
        self._touch()
        return True

    def verify_package_checklist(self) -> dict:
        """패키지 체크리스트 대조 결과 반환.

        Returns:
            {
                "tier": str,
                "total": int,
                "done": int,
                "rate": float,  # 0.0 ~ 1.0
                "missing": [{"key": str, "label": str, "scope": str}],
                "completed": [{"key": str, "label": str}],
                "not_included": list[str],
                "ready_to_deploy": bool
            }
        """
        tier = self.state.get("package_tier")
        if not tier:
            return {"tier": None, "error": "패키지 미설정. set_package() 필요."}

        checklist = self.state.get("package_checklist", {})
        total = len(checklist)
        done_items = []
        missing_items = []

        for key, item in checklist.items():
            if item["done"]:
                done_items.append({"key": key, "label": item["label"]})
            else:
                missing_items.append({
                    "key": key,
                    "label": item["label"],
                    "scope": item["scope"],
                })

        done_count = len(done_items)
        rate = done_count / total if total > 0 else 0.0

        return {
            "tier": tier,
            "total": total,
            "done": done_count,
            "rate": round(rate, 2),
            "missing": missing_items,
            "completed": done_items,
            "not_included": self.state.get("package_not_included", []),
            "ready_to_deploy": len(missing_items) == 0,
        }

    @property
    def package_tier(self) -> str | None:
        return self.state.get("package_tier")

    @property
    def package_not_included(self) -> list:
        return self.state.get("package_not_included", [])

    # ── 저장 ──

    def save(self) -> Path:
        """상태 파일 저장."""
        self.state_file.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return self.state_file

    def _touch(self) -> None:
        self.state["updated_at"] = datetime.now().isoformat(timespec="seconds")

    # ── 유틸리티 ──

    @staticmethod
    def list_projects() -> list[dict]:
        """모든 프로젝트 목록 반환."""
        projects = []
        if not PROJECTS_ROOT.exists():
            return projects
        for d in sorted(PROJECTS_ROOT.iterdir()):
            state_file = d / "project_state.json"
            if state_file.exists():
                state = json.loads(state_file.read_text(encoding="utf-8"))
                projects.append({
                    "slug": d.name,
                    "name": state.get("project_name", d.name),
                    "phase": state.get("phase", "unknown"),
                    "updated_at": state.get("updated_at", ""),
                })
        return projects

    def get_path(self, *parts) -> str:
        """프로젝트 디렉토리 기준 경로."""
        return str(self.project_dir / Path(*parts))
