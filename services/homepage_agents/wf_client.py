#!/usr/bin/env python3
"""n8n WF 웹훅 호출 유틸리티.

에이전트가 외부 작업을 n8n WF 경유로 수행할 때 사용.
직접 MCP/Playwright/WebSearch 호출을 대체한다.

사용법:
    from homepage_agents.wf_client import call_wf

    # 사이트 분석 요청
    result = call_wf("site-analyzer", {"url": "https://example.com"})

    # Notion 작업
    result = call_wf("notion-api", {"action": "create", "database": "worklog", ...})
"""
import json
import subprocess
import sys
from pathlib import Path

# n8n 웹훅 베이스 URL
N8N_WEBHOOK_BASE = "https://n8n.wookvan.com/webhook"

# WF 엔드포인트 매핑 (WF 이름 → 웹훅 경로)
# 제안서 승인 후 실제 WF가 생성되면 여기에 추가
WF_ENDPOINTS = {
    # 기존 WF
    "notion-api": "notion-api",
    "win-message-gate": "win-message-gate",
    # 홈페이지 에이전트용 WF (제안서 승인 후 추가 예정)
    "site-analyzer": "hp-site-analyzer",
    "trend-crawler": "hp-trend-crawler",
    "html-screenshot": "hp-html-screenshot",
    "lighthouse": "hp-lighthouse",
    "vercel-deploy": "hp-vercel-deploy",
    "contact-form": "hp-contact-form",
}


def call_wf(wf_name: str, payload: dict, timeout: int = 120) -> dict:
    """n8n WF 웹훅 호출.

    Args:
        wf_name: WF 이름 (WF_ENDPOINTS 키 또는 직접 webhook 경로)
        payload: 요청 데이터 (JSON)
        timeout: 타임아웃 (초)

    Returns:
        {"success": True, "data": ...} 또는 {"success": False, "error": ...}
    """
    endpoint = WF_ENDPOINTS.get(wf_name, wf_name)
    url = f"{N8N_WEBHOOK_BASE}/{endpoint}"

    # curl로 호출 (requests 의존성 없이 동작)
    cmd = [
        "curl", "-s", "-w", "\n%{http_code}",
        "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload, ensure_ascii=False),
        "--max-time", str(timeout),
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout + 10
        )
        output = result.stdout.strip()
        if not output:
            return {"success": False, "error": f"빈 응답. stderr: {result.stderr[:200]}"}

        # 마지막 줄 = HTTP 상태코드
        lines = output.rsplit("\n", 1)
        body = lines[0] if len(lines) > 1 else ""
        status_code = int(lines[-1]) if lines[-1].isdigit() else 0

        if 200 <= status_code < 300:
            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                data = {"raw": body}
            return {"success": True, "data": data, "status": status_code}
        else:
            return {"success": False, "error": f"HTTP {status_code}", "body": body[:500]}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"타임아웃 ({timeout}초)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def call_notion(action: str, **kwargs) -> dict:
    """Notion 작업 단축 함수.

    사용법:
        call_notion("create", database="worklog", data={"Name": "제목"})
        call_notion("query", database="worklog", filter={"Status": "진행중"})
        call_notion("get", page_id="abc123")
    """
    payload = {"action": action, **kwargs}
    return call_wf("notion-api", payload)


def send_discord(message: str, channel_id: str, sender: str = "main",
                 client_id: str = "win-home", thread_id: str | None = None) -> dict:
    """Discord 메시지 전송 (메인 에이전트 전용).

    서브에이전트는 이 함수를 호출하면 안 됨 (훅에서 차단됨).
    """
    payload = {
        "message": message,
        "channelId": channel_id,
        "sender": sender,
        "client_id": client_id,
    }
    if thread_id:
        payload["threadId"] = thread_id
    return call_wf("win-message-gate", payload)
