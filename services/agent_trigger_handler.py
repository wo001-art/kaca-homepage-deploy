#!/usr/bin/env python3
"""팀에이전트 트리거 핸들러.

Discord 메시지에서 "[팀에이전트 트리거]"를 감지하면 오케스트레이터를 호출.
Claude 메인 에이전트가 이 모듈을 import하여 사용.

사용법 (메인 에이전트):
    from agent_trigger_handler import handle_agent_trigger
    result = handle_agent_trigger(message_text, notion_page_id)
"""
import json
import sys
import re
from pathlib import Path

# 서비스 경로 추가
SERVICES_DIR = Path(__file__).resolve().parent
if str(SERVICES_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICES_DIR))

from homepage_agents.homepage_orchestrator import orchestrate
from homepage_agents.wf_client import call_notion


def extract_trigger_data(message: str) -> dict | None:
    """Discord 메시지에서 트리거 데이터 추출.

    Returns:
        dict with project_name, client_name, page_id etc. or None
    """
    if "[팀에이전트 트리거]" not in message:
        return None

    data = {}
    patterns = {
        "project_name": r"프로젝트:\s*(.+)",
        "client_name": r"고객:\s*(.+)",
        "project_type": r"유형:\s*(.+)",
        "page_count": r"페이지:\s*(\d+)",
        "page_id": r"페이지ID:\s*([a-f0-9-]+)",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, message)
        if match:
            val = match.group(1).strip()
            if key == "page_count":
                val = int(val)
            data[key] = val

    return data if data.get("page_id") else None


def get_full_form_data(page_id: str) -> dict:
    """Notion 페이지에서 전체 폼 데이터 로드."""
    import urllib.request

    NOTION_TOKEN = "NOTION_TOKEN_REDACTED"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    url = f"https://api.notion.com/v1/pages/{page_id}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {NOTION_TOKEN}")
    req.add_header("Notion-Version", "2022-06-28")

    try:
        with urllib.request.urlopen(req) as resp:
            page = json.load(resp)
    except Exception as e:
        return {"error": str(e)}

    props = page.get("properties", {})
    form_data = {}

    # 속성별 값 추출
    prop_map = {
        "프로젝트명": "project_name",
        "고객명": "client_name",
        "담당자": "contact_person",
        "연락처": "phone",
        "이메일": "email",
        "프로젝트유형": "project_type",
        "디자인등급": "design_grade",
        "페이지수": "page_count",
        "콘텐츠제공": "content_provision",
        "참고사이트": "reference_site",
        "비고": "notes",
    }

    for notion_key, form_key in prop_map.items():
        val = props.get(notion_key)
        if not val:
            continue
        t = val.get("type", "")
        if t == "title":
            form_data[form_key] = val["title"][0]["plain_text"] if val["title"] else ""
        elif t == "rich_text":
            form_data[form_key] = val["rich_text"][0]["plain_text"] if val["rich_text"] else ""
        elif t == "select":
            form_data[form_key] = val["select"]["name"] if val["select"] else ""
        elif t == "status":
            form_data[form_key] = val["status"]["name"] if val["status"] else ""
        elif t == "number":
            form_data[form_key] = val["number"]
        elif t == "multi_select":
            form_data[form_key] = [s["name"] for s in val["multi_select"]]
        elif t == "url":
            form_data[form_key] = val["url"] or ""
        elif t == "email":
            form_data[form_key] = val["email"] or ""
        elif t == "phone_number":
            form_data[form_key] = val["phone_number"] or ""

    # 필요기능 (multi_select)
    feat_val = props.get("필요기능")
    if feat_val and feat_val.get("type") == "multi_select":
        form_data["features"] = [s["name"] for s in feat_val["multi_select"]]

    form_data["notion_page_id"] = page_id
    return form_data


def handle_agent_trigger(message: str) -> dict:
    """메인 진입점: 트리거 메시지 → 오케스트레이터 호출.

    Returns:
        orchestrate() 결과 dict
    """
    trigger_data = extract_trigger_data(message)
    if not trigger_data:
        return {"status": "error", "message": "트리거 데이터 없음"}

    page_id = trigger_data["page_id"]

    # Notion에서 전체 폼 데이터 로드
    form_data = get_full_form_data(page_id)
    if "error" in form_data:
        return {"status": "error", "message": f"Notion 조회 실패: {form_data['error']}"}

    # 오케스트레이터 init 호출
    project_name = form_data.get("project_name", trigger_data.get("project_name", "미정"))
    result = orchestrate(
        "init",
        project_name=project_name,
        form_data=form_data,
    )

    return result


if __name__ == "__main__":
    # 테스트용
    test_msg = """🚀 [팀에이전트 트리거] 승인 감지!

프로젝트: 테스트 프로젝트
고객: 테스트 고객
유형: 맞춤형
페이지: 7
페이지ID: abc12345-1234-1234-1234-123456789012

→ 팀에이전트 자동 시작합니다."""

    data = extract_trigger_data(test_msg)
    print(json.dumps(data, ensure_ascii=False, indent=2))
