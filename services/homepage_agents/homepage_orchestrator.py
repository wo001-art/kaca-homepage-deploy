#!/usr/bin/env python3
"""PM 오케스트레이터 — 팀에이전트 총괄 진입점.

팀에이전트가 직접 DB를 확인하여 승인된 건을 감지하고, 제작을 시작한다.
n8n WF 없이 오케스트레이터가 자율적으로 동작.

사용법:
    # DB에서 승인건 확인 → 자동 시작
    result = orchestrate("check_approved")

    # 프로젝트 시작 (수동)
    result = orchestrate("init", project_name="KACA 홈페이지", form_data={...})

    # 상태 확인
    result = orchestrate("status", project_slug="kaca-2026")

    # 승인 처리 후 다음 단계 진행
    result = orchestrate("approve", project_slug="kaca-2026", approval_type="estimate")

    # 특정 에이전트 실행
    result = orchestrate("dispatch", project_slug="kaca-2026", agent="research")
"""
import json
import sys
import urllib.request
from pathlib import Path

# 패키지 경로 설정
SERVICES_DIR = Path(__file__).resolve().parent.parent
if str(SERVICES_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICES_DIR))

from homepage_agents.state_manager import StateManager, PROJECTS_ROOT
from homepage_agents.wf_client import call_wf, call_notion

# 프롬프트 디렉토리
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

# Notion API 설정
NOTION_TOKEN = "NOTION_TOKEN_REDACTED"
NOTION_API = "https://api.notion.com/v1"
ESTIMATE_DB_ID = "3ddbf37e258c49418bf03698bc1d928a"

# 에이전트 → 프롬프트 파일 매핑
AGENT_PROMPTS = {
    "pm": "pm_agent.md",
    "research": "research_agent.md",
    "planning": "planning_ux_agent.md",
    "design": "design_agent.md",
    "frontend": "frontend_agent.md",
    "backend": "backend_agent.md",
}

# 단계 → 에이전트 매핑
PHASE_AGENTS = {
    "research": ["research"],
    "planning": ["planning"],
    "design": ["design"],
    "frontend": ["frontend", "backend"],  # 동시 진행
    "backend": ["frontend", "backend"],
    "review": [],  # PM이 직접 검수
}

# 단계 → 필요 승인
PHASE_APPROVALS = {
    "research": "estimate",
    "design": "sitemap",
    "frontend": "design",
    "deploy": "final",
}


def load_prompt(agent_name: str) -> str:
    """에이전트 프롬프트 파일 로드."""
    filename = AGENT_PROMPTS.get(agent_name)
    if not filename:
        raise ValueError(f"알 수 없는 에이전트: {agent_name}")
    prompt_path = PROMPTS_DIR / filename
    return prompt_path.read_text(encoding="utf-8")


def orchestrate(action: str, **kwargs) -> dict:
    """PM 오케스트레이션 진입점.

    Args:
        action: "init" | "dispatch" | "status" | "approve" | "list"
        **kwargs: 액션별 파라미터

    Returns:
        {"status": "success|error|waiting_approval", "message": "...", ...}
    """
    handlers = {
        "check_approved": _handle_check_approved,
        "init": _handle_init,
        "dispatch": _handle_dispatch,
        "status": _handle_status,
        "approve": _handle_approve,
        "list": _handle_list,
        "set_package": _handle_set_package,
        "verify_package": _handle_verify_package,
    }
    handler = handlers.get(action)
    if not handler:
        return {"status": "error", "message": f"알 수 없는 액션: {action}. 가능: {list(handlers.keys())}"}
    return handler(**kwargs)


def _notion_api(method: str, path: str, body: dict = None) -> dict:
    """Notion API 호출 헬퍼."""
    url = f"{NOTION_API}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {NOTION_TOKEN}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Notion-Version", "2022-06-28")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def _extract_page_props(page: dict) -> dict:
    """Notion 페이지 properties를 평탄한 dict로 변환."""
    props = page.get("properties", {})
    flat = {"id": page["id"]}
    for key, val in props.items():
        t = val.get("type", "")
        if t == "title":
            flat[key] = val["title"][0]["plain_text"] if val["title"] else ""
        elif t == "rich_text":
            flat[key] = val["rich_text"][0]["plain_text"] if val["rich_text"] else ""
        elif t == "select":
            flat[key] = val["select"]["name"] if val["select"] else ""
        elif t == "status":
            flat[key] = val["status"]["name"] if val["status"] else ""
        elif t == "multi_select":
            flat[key] = [s["name"] for s in val["multi_select"]]
        elif t == "number":
            flat[key] = val["number"]
        elif t == "url":
            flat[key] = val["url"] or ""
        elif t == "email":
            flat[key] = val["email"] or ""
        elif t == "phone_number":
            flat[key] = val["phone_number"] or ""
        elif t == "date":
            flat[key] = val["date"]["start"] if val["date"] else ""
    return flat


def _handle_check_approved(**_) -> dict:
    """DB에서 승인건 확인 → 제작중으로 변경 → 프로젝트 자동 생성.

    팀에이전트가 직접 DB를 확인하여 승인된 건을 감지하고 작업을 시작한다.
    n8n WF 폴링 없이 오케스트레이터가 자율적으로 동작.
    """
    # 1. 견적 DB에서 상태=승인 인 건 조회
    query_body = {
        "filter": {
            "property": "상태",
            "status": {"equals": "승인"}
        },
        "page_size": 10
    }

    try:
        result = _notion_api("POST", f"/databases/{ESTIMATE_DB_ID}/query", query_body)
    except Exception as e:
        return {"status": "error", "message": f"DB 조회 실패: {e}"}

    pages = result.get("results", [])
    if not pages:
        return {"status": "no_approved", "message": "승인된 건이 없습니다.", "count": 0}

    # 2. 각 승인건 처리
    started = []
    for page in pages:
        flat = _extract_page_props(page)
        page_id = flat["id"]
        project_name = flat.get("프로젝트명", "미정")

        # 상태를 '제작중'으로 변경
        try:
            _notion_api("PATCH", f"/pages/{page_id}", {
                "properties": {
                    "상태": {"status": {"name": "제작중"}}
                }
            })
        except Exception as e:
            started.append({"page_id": page_id, "error": f"상태 변경 실패: {e}"})
            continue

        # form_data 구성
        form_data = {
            "project_name": project_name,
            "client_name": flat.get("고객명", ""),
            "contact_person": flat.get("담당자", ""),
            "phone": flat.get("연락처", ""),
            "email": flat.get("이메일", ""),
            "project_type": flat.get("프로젝트유형", "기본형"),
            "design_grade": flat.get("디자인등급", "맞춤"),
            "page_count": flat.get("페이지수", 5),
            "features": flat.get("필요기능", []),
            "content_provision": flat.get("콘텐츠제공", "고객제공"),
            "reference_site": flat.get("참고사이트", ""),
            "notes": flat.get("비고", ""),
            "notion_page_id": page_id,
        }

        # 프로젝트 생성 (init)
        init_result = _handle_init(
            project_name=project_name,
            form_data=form_data,
        )

        # 견적 승인 처리 (이미 고객이 승인했으므로)
        if init_result.get("project_slug"):
            slug = init_result["project_slug"]
            _handle_approve(project_slug=slug, approval_type="estimate")

        started.append({
            "page_id": page_id,
            "project_name": project_name,
            "slug": init_result.get("project_slug"),
            "status": "started",
        })

    return {
        "status": "success",
        "message": f"승인건 {len(started)}개 처리 완료",
        "projects": started,
        "count": len(started),
    }


def _handle_init(project_name: str, form_data: dict = None,
                 estimate: dict = None, slug: str = None, **_) -> dict:
    """신규 프로젝트 생성."""
    sm = StateManager.create(project_name, form_data=form_data,
                             estimate=estimate, slug=slug)

    # 견적 자동 산출 (estimate_calculator 연동)
    if form_data and not estimate:
        try:
            from estimate_calculator import calculate_estimate
            estimate = calculate_estimate(form_data)
            sm.update_estimate(estimate)
            sm.save()
        except ImportError:
            pass

    # 패키지 자동 추론 (페이지 수 기반)
    pkg_tier = None
    if form_data:
        page_count = form_data.get("page_count", 5)
        features = form_data.get("features", [])
        if isinstance(page_count, str):
            page_count = int(page_count) if page_count.isdigit() else 5
        has_premium_features = any(f in features for f in ["회원로그인", "결제", "다국어"])
        if has_premium_features or page_count >= 10:
            pkg_tier = "premium"
        elif page_count >= 7 or any(f in features for f in ["갤러리", "공지사항", "검색", "Band"]):
            pkg_tier = "standard"
        else:
            pkg_tier = "basic"
        sm.set_package(pkg_tier)
        sm.save()

    return {
        "status": "success",
        "message": f"프로젝트 생성 완료: {project_name} ({sm.slug})",
        "project_slug": sm.slug,
        "project_dir": str(sm.project_dir),
        "phase": sm.phase,
        "package_tier": pkg_tier,
        "next_action": "견적 승인 대기 (approve estimate)",
    }


def _handle_dispatch(project_slug: str, agent: str = None, **kwargs) -> dict:
    """에이전트 디스패치 정보 반환.

    실제 Task tool 호출은 메인 에이전트 또는 PM 에이전트가 수행.
    이 함수는 디스패치에 필요한 정보(프롬프트, 컨텍스트)를 준비.
    """
    sm = StateManager(project_slug)

    # 에이전트 미지정 시 현재 phase 기반 결정
    if not agent:
        agents = PHASE_AGENTS.get(sm.phase, [])
        if not agents:
            return {
                "status": "error",
                "message": f"현재 단계({sm.phase})에 디스패치할 에이전트 없음",
            }
        agent = agents[0]

    # 승인 체크
    required_approval = PHASE_APPROVALS.get(sm.phase)
    if required_approval:
        approval = sm.approval(required_approval)
        if approval["status"] != "approved":
            return {
                "status": "waiting_approval",
                "message": f"{required_approval} 승인 필요 (현재: {approval['status']})",
                "approval_type": required_approval,
            }

    # 프롬프트 로드
    prompt = load_prompt(agent)

    # 컨텍스트 구성
    context = {
        "project_slug": project_slug,
        "project_dir": str(sm.project_dir),
        "phase": sm.phase,
        "form_data": sm.state.get("form_data", {}),
        "agent_status": {k: v["status"] for k, v in sm.state["agents"].items()},
    }

    # 패키지 컨텍스트 주입
    if sm.package_tier:
        verify = sm.verify_package_checklist()
        context["package"] = {
            "tier": sm.package_tier,
            "label": sm.state.get("package_label", ""),
            "pages": sm.state.get("package_pages"),
            "checklist": sm.state.get("package_checklist", {}),
            "not_included": sm.package_not_included,
            "progress": f"{verify['done']}/{verify['total']}",
            "missing": verify["missing"],
        }

    # 이전 에이전트 산출물 경로
    prev_outputs = {}
    for key, agent_state in sm.state["agents"].items():
        if agent_state["output_files"]:
            prev_outputs[key] = agent_state["output_files"]
    context["previous_outputs"] = prev_outputs

    # 에이전트 상태 업데이트
    sm.update_agent(agent, status="in_progress")
    sm.save()

    return {
        "status": "ready",
        "agent": agent,
        "prompt": prompt,
        "context": context,
        "message": f"{agent} 에이전트 디스패치 준비 완료",
        "model": "haiku" if agent == "research" else "sonnet",
    }


def _handle_status(project_slug: str, **_) -> dict:
    """프로젝트 상태 조회."""
    sm = StateManager(project_slug)
    summary = sm.summary()

    # 진행률 계산
    total = len(sm.state["agents"])
    done = sum(1 for v in sm.state["agents"].values() if v["status"] == "done")
    progress = f"{done}/{total}"

    # 다음 할 일
    next_action = _determine_next_action(sm)

    return {
        "status": "success",
        "summary": summary,
        "progress": progress,
        "next_action": next_action,
        "message": _format_status_message(sm, progress, next_action),
    }


def _handle_approve(project_slug: str, approval_type: str, **_) -> dict:
    """승인 처리 + 다음 단계 진행."""
    sm = StateManager(project_slug)
    sm.set_approval(approval_type, "approved")

    # 승인 후 phase 전환
    phase_map = {
        "estimate": "research",
        "sitemap": "design",
        "design": "frontend",
        "final": "deploy",
    }
    next_phase = phase_map.get(approval_type)
    if next_phase:
        sm.advance_phase(next_phase)

    sm.save()

    return {
        "status": "success",
        "message": f"{approval_type} 승인 완료 → {sm.phase} 단계로 전환",
        "phase": sm.phase,
        "next_action": f"{sm.phase} 에이전트 디스패치 (dispatch)",
    }


def _handle_list(**_) -> dict:
    """전체 프로젝트 목록."""
    projects = StateManager.list_projects()
    return {
        "status": "success",
        "projects": projects,
        "count": len(projects),
        "message": f"프로젝트 {len(projects)}개" if projects else "진행 중인 프로젝트 없음",
    }


def _handle_set_package(project_slug: str, tier: str, **_) -> dict:
    """프로젝트 패키지 설정."""
    sm = StateManager(project_slug)
    result = sm.set_package(tier)
    sm.save()
    return {
        "status": "success",
        "message": f"패키지 설정 완료: {tier} ({result['checklist_count']}개 항목)",
        **result,
    }


def _handle_verify_package(project_slug: str, **_) -> dict:
    """패키지 체크리스트 검증."""
    sm = StateManager(project_slug)
    verify = sm.verify_package_checklist()

    if verify.get("error"):
        return {"status": "error", "message": verify["error"]}

    # 보고용 메시지 포맷
    lines = [
        f"**패키지 검증: {verify['tier'].upper()}**",
        f"진행률: {verify['done']}/{verify['total']} ({int(verify['rate']*100)}%)",
    ]
    if verify["missing"]:
        lines.append(f"\n**미완료 ({len(verify['missing'])}개):**")
        for item in verify["missing"]:
            lines.append(f"  - [{item['scope']}] {item['label']}")
    if verify["not_included"]:
        lines.append(f"\n**미포함 항목**: {', '.join(verify['excluded'])}")
    lines.append(f"\n**배포 가능**: {'Yes' if verify['ready_to_deploy'] else 'No'}")

    return {
        "status": "success",
        "message": "\n".join(lines),
        **verify,
    }


def _determine_next_action(sm: StateManager) -> str:
    """다음 할 일 결정."""
    phase = sm.phase

    # 승인 대기 확인
    required = PHASE_APPROVALS.get(phase)
    if required:
        approval = sm.approval(required)
        if approval["status"] != "approved":
            return f"대표님 {required} 승인 대기"

    # 에이전트 상태 확인
    agents = PHASE_AGENTS.get(phase, [])
    for agent_name in agents:
        agent = sm.agent(agent_name)
        if agent["status"] == "pending":
            return f"{agent_name} 에이전트 디스패치"
        elif agent["status"] == "in_progress":
            return f"{agent_name} 에이전트 작업 중"

    # 현재 phase 완료 → 다음 phase
    return f"{phase} 단계 완료, 다음 단계로 전환"


def _format_status_message(sm: StateManager, progress: str, next_action: str) -> str:
    """Discord 보고용 상태 메시지 포맷."""
    agents = sm.state["agents"]
    status_icons = {"pending": "⏳", "in_progress": "🔄", "done": "✅", "error": "❌"}

    lines = [
        f"**[{sm.project_name}] 프로젝트 현황**",
        f"단계: {sm.phase} | 진행률: {progress}",
        "",
    ]
    for key, agent in agents.items():
        icon = status_icons.get(agent["status"], "❓")
        summary = f" — {agent['summary']}" if agent.get("summary") else ""
        lines.append(f"{icon} {key}: {agent['status']}{summary}")

    # 패키지 체크리스트
    if sm.package_tier:
        verify = sm.verify_package_checklist()
        lines.append(f"\n**패키지**: {sm.package_tier.upper()} ({verify['done']}/{verify['total']})")
        if verify["missing"]:
            missing_labels = [m["label"] for m in verify["missing"][:5]]
            lines.append(f"  미완료: {', '.join(missing_labels)}")
            if len(verify["missing"]) > 5:
                lines.append(f"  ... 외 {len(verify['missing'])-5}개")

    # 대기 중인 승인
    pending = [a["type"] for a in sm.state["approvals"] if a["status"] == "pending"]
    if pending:
        lines.append(f"\n**대기 승인**: {', '.join(pending)}")

    lines.append(f"\n**다음**: {next_action}")
    return "\n".join(lines)


# CLI 실행 지원
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python homepage_orchestrator.py <action> [--key=value ...]")
        print("액션: init, dispatch, status, approve, list")
        sys.exit(1)

    action = sys.argv[1]
    kwargs = {}
    for arg in sys.argv[2:]:
        if arg.startswith("--"):
            key, _, value = arg[2:].partition("=")
            kwargs[key] = value

    result = orchestrate(action, **kwargs)
    print(json.dumps(result, ensure_ascii=False, indent=2))
