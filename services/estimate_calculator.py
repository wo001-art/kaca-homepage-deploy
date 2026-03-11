#!/usr/bin/env python3
"""
홈페이지 견적 자동 산출기
- 고객 폼 데이터 → 가견적 자동 계산 → Notion 견적 페이지 생성 → Discord 알림
- 사용법: python estimate_calculator.py input.json
- 또는: echo '{"project_name":"테스트",...}' | python estimate_calculator.py
"""
import json
import sys
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ── 설정 ──
NOTION_TOKEN = "NOTION_TOKEN_REDACTED"
NOTION_DB_ID = "3ddbf37e258c49418bf03698bc1d928a"
CUSTOMER_DB_ID = "181d1c3246a2462f97989cfcbde2a92d"
NOTION_API = "https://api.notion.com/v1"
N8N_WEBHOOK = "https://n8n.wookvan.com/webhook/win-message-gate"

# config_loader에서 client_id 가져오기
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import config_loader as cfg
    CLIENT_ID = cfg.client_id()
except Exception:
    CLIENT_ID = "win-home"

# 견적 알림 채널 (홈페이지 에이전트 스레드)
ESTIMATE_CHANNEL = "1475714595116290218"

# 견적서(배포) DB ID
ESTIMATE_DOC_DB = "31e765eb-4694-81c0-bfa6-d567dc3788f4"

# WOOKVAN 공급자 정보 (고정)
SUPPLIER_INFO = {
    "company": "우크반(WOOKVAN)",
    "representative": "한기홍",
    "phone": "010-0000-0000",
    "email": "wo.001@wookvan.com",
}

# ── 가격 테이블 (만원 단위) ──
BASE_PRICES = {
    "기본형":     {"기획": 10, "디자인": 25, "개발": 35, "인프라": 10},   # 합계 80만
    "맞춤형":     {"기획": 20, "디자인": 40, "개발": 45, "인프라": 15},   # 합계 120만
    "프리미엄형": {"기획": 30, "디자인": 70, "개발": 80, "인프라": 20},   # 합계 200만
}

# 유형별 기본 포함 기능 (추가 비용 없음)
INCLUDED_FEATURES = {
    "기본형":     ["문의폼", "갤러리", "SNS연동"],
    "맞춤형":     ["문의폼", "갤러리", "게시판", "SEO", "SNS연동", "관리자CMS"],
    "프리미엄형": ["문의폼", "갤러리", "게시판", "회원관리", "SEO", "SNS연동", "관리자CMS", "다국어"],
}

FEATURE_PRICES = {
    "회원관리": 30,
    "게시판": 10,
    "갤러리": 15,
    "문의폼": 5,
    "예약": 50,
    "결제": 80,
    "쇼핑몰": 100,
    "다국어": 30,
    "SEO": 20,
    "SNS연동": 10,
    "관리자CMS": 40,
}

PAGE_EXTRA_PRICE = 5     # 추가 페이지당 (만원)
CONTENT_AGENCY_PRICE = 5  # 콘텐츠 대행 페이지당 (만원)
BASE_PAGES = 5            # 기본 포함 페이지 수


def calculate_estimate(form_data):
    """폼 데이터로 가견적 산출"""
    project_type = form_data.get("project_type", "기본형")
    base = BASE_PRICES.get(project_type, BASE_PRICES["기본형"])

    # 기본 비용 (만원)
    planning = base["기획"]
    design = base["디자인"]
    development = base["개발"]
    infra = base["인프라"]

    # 추가 기능 비용 (기본 포함 기능은 제외)
    features = form_data.get("features", [])
    included = INCLUDED_FEATURES.get(project_type, [])
    feature_cost = 0
    feature_details = []
    for feat in features:
        if feat in included:
            feature_details.append(f"{feat}(포함)")
            continue
        price = FEATURE_PRICES.get(feat, 0)
        if price > 0:
            feature_cost += price
            feature_details.append(f"{feat}(+{price}만)")

    # 개발비에 기능 비용 합산
    development += feature_cost

    # 추가 페이지 비용
    page_count = form_data.get("page_count", 5)
    extra_pages = max(0, page_count - BASE_PAGES)
    if extra_pages > 0:
        design += extra_pages * PAGE_EXTRA_PRICE

    # 콘텐츠 대행 비용
    content_provision = form_data.get("content_provision", "고객제공")
    content_cost = 0
    if content_provision == "대행필요":
        content_cost = page_count * CONTENT_AGENCY_PRICE
        planning += content_cost
    elif content_provision == "혼합":
        content_cost = (page_count // 2) * CONTENT_AGENCY_PRICE
        planning += content_cost

    # 디자인 등급 가산
    design_grade = form_data.get("design_grade", "맞춤")
    if design_grade == "프리미엄":
        design = int(design * 1.5)
    elif design_grade == "템플릿":
        design = int(design * 0.6)

    # 유지보수 (월)
    maintenance = 5 if project_type in ["기본형", "맞춤형"] else 10

    # 합계 (만원 → 원)
    supply_total = (planning + design + development + infra) * 10000
    vat = int(supply_total * 0.1)
    grand_total = supply_total + vat

    return {
        "planning": planning * 10000,
        "design": design * 10000,
        "development": development * 10000,
        "infra": infra * 10000,
        "maintenance": maintenance * 10000,
        "supply_total": supply_total,
        "vat": vat,
        "grand_total": grand_total,
        "feature_details": feature_details,
        "content_cost": content_cost * 10000,
    }


def create_notion_page(form_data, estimate):
    """n8n notion-api WF를 통해 견적서 페이지 생성"""
    valid_until = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    features_str = ", ".join(form_data.get("features", []))

    # n8n notion-api 직접 지정 방식
    notion_data = {
        "action": "create",
        "database_id": NOTION_DB_ID,
        "data": {
            "프로젝트명": form_data.get("project_name", "미정"),
            "상태": "접수",
            "고객명": form_data.get("client_name", ""),
            "담당자": form_data.get("contact_person", ""),
            "연락처": form_data.get("phone", ""),
            "이메일": form_data.get("email", ""),
            "프로젝트유형": form_data.get("project_type", "기본형"),
            "페이지수": form_data.get("page_count", 5),
            "디자인등급": form_data.get("design_grade", "맞춤"),
            "필요기능": form_data.get("features", []),
            "콘텐츠제공": form_data.get("content_provision", "고객제공"),
            "도메인보유": form_data.get("has_domain", False),
            "호스팅보유": form_data.get("has_hosting", False),
            "참고사이트": form_data.get("reference_site", ""),
            "예산범위": form_data.get("budget_range", "미정"),
            "기획비": estimate["planning"],
            "디자인비": estimate["design"],
            "개발비": estimate["development"],
            "인프라비": estimate["infra"],
            "유지보수비": estimate["maintenance"],
            "비고": form_data.get("notes", ""),
        }
    }

    # 선택적 날짜 필드
    if form_data.get("deadline"):
        notion_data["data"]["희망납기"] = form_data["deadline"]

    try:
        resp = requests.post(
            "https://n8n.wookvan.com/webhook/notion-api",
            json=notion_data, timeout=60
        )
        if resp.status_code == 200:
            result = resp.json() if resp.text else {}
            # n8n WF 응답에서 페이지 URL 추출
            page_url = result.get("url", "")
            page_id = result.get("id", "")
            if not page_url and page_id:
                page_url = f"https://www.notion.so/{page_id.replace('-', '')}"
            return {"success": True, "page_id": page_id, "url": page_url}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

    # Fallback: Notion API 직접 호출
    return _create_notion_page_direct(form_data, estimate, valid_until)


def _create_notion_page_direct(form_data, estimate, valid_until):
    """Fallback: Notion API 직접 호출로 페이지 생성"""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    properties = {
        "프로젝트명": {"title": [{"text": {"content": form_data.get("project_name", "미정")}}]},
        "상태": {"select": {"name": "접수"}},
        "고객명": {"rich_text": [{"text": {"content": form_data.get("client_name", "")}}]},
        "담당자": {"rich_text": [{"text": {"content": form_data.get("contact_person", "")}}]},
        "연락처": {"phone_number": form_data.get("phone", "")},
        "프로젝트유형": {"select": {"name": form_data.get("project_type", "기본형")}},
        "페이지수": {"number": form_data.get("page_count", 5)},
        "디자인등급": {"select": {"name": form_data.get("design_grade", "맞춤")}},
        "콘텐츠제공": {"select": {"name": form_data.get("content_provision", "고객제공")}},
        "도메인보유": {"checkbox": form_data.get("has_domain", False)},
        "호스팅보유": {"checkbox": form_data.get("has_hosting", False)},
        "예산범위": {"select": {"name": form_data.get("budget_range", "미정")}},
        "기획비": {"number": estimate["planning"]},
        "디자인비": {"number": estimate["design"]},
        "개발비": {"number": estimate["development"]},
        "인프라비": {"number": estimate["infra"]},
        "유지보수비": {"number": estimate["maintenance"]},
        "견적유효기간": {"date": {"start": valid_until}},
    }

    if form_data.get("email"):
        properties["이메일"] = {"email": form_data["email"]}
    if form_data.get("reference_site"):
        properties["참고사이트"] = {"url": form_data["reference_site"]}
    if form_data.get("deadline"):
        properties["희망납기"] = {"date": {"start": form_data["deadline"]}}
    if form_data.get("features"):
        properties["필요기능"] = {"multi_select": [{"name": f} for f in form_data["features"]]}
    if form_data.get("notes"):
        properties["비고"] = {"rich_text": [{"text": {"content": form_data["notes"]}}]}

    payload = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": properties
    }

    resp = requests.post(f"{NOTION_API}/pages", headers=headers, json=payload, timeout=30)

    if resp.status_code == 200:
        page = resp.json()
        page_id = page["id"].replace("-", "")
        return {"success": True, "page_id": page["id"], "url": f"https://www.notion.so/{page_id}"}
    else:
        return {"success": False, "error": resp.text[:200]}


def _build_order_toggle(form_data, estimate, estimate_notion_result, order_num=1):
    """의뢰 건별 토글 블록 생성 (토글 제목 + 내부 콘텐츠)"""
    today = datetime.now().strftime("%Y-%m-%d")
    project_name = form_data.get("project_name", "미정")
    toggle_title = f"[{today}] {order_num}차 의뢰: {project_name}"

    # 토글 내부 children 블록들
    toggle_children = []

    # ── 프로젝트 개요 ──
    toggle_children.append({
        "object": "block", "type": "heading_3",
        "heading_3": {"rich_text": [{"text": {"content": "프로젝트 개요"}}]}
    })
    overview_lines = [
        f"프로젝트유형: {form_data.get('project_type', '기본형')}",
        f"페이지수: {form_data.get('page_count', 5)}페이지",
        f"디자인등급: {form_data.get('design_grade', '맞춤')}",
        f"콘텐츠제공: {form_data.get('content_provision', '고객제공')}",
        f"도메인보유: {'예' if form_data.get('has_domain') else '아니오'}",
        f"호스팅보유: {'예' if form_data.get('has_hosting') else '아니오'}",
    ]
    for line in overview_lines:
        toggle_children.append({
            "object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"text": {"content": line}}]}
        })

    # ── 필요 기능 ──
    features = form_data.get("features", [])
    if features:
        toggle_children.append({
            "object": "block", "type": "heading_3",
            "heading_3": {"rich_text": [{"text": {"content": "필요 기능"}}]}
        })
        for feat in features:
            price = FEATURE_PRICES.get(feat, 0)
            toggle_children.append({
                "object": "block", "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"text": {"content": f"{feat} (+{price}만원)" if price else feat}}]}
            })

    # ── 참고사이트 ──
    if form_data.get("reference_site"):
        toggle_children.append({
            "object": "block", "type": "heading_3",
            "heading_3": {"rich_text": [{"text": {"content": "참고사이트"}}]}
        })
        toggle_children.append({
            "object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"text": {"content": form_data["reference_site"], "link": {"url": form_data["reference_site"]}}}]}
        })

    # ── 견적 요약 ──
    toggle_children.append({
        "object": "block", "type": "heading_3",
        "heading_3": {"rich_text": [{"text": {"content": "견적 요약"}}]}
    })
    cost_lines = [
        f"기획비: {estimate['planning']:,}원",
        f"디자인비: {estimate['design']:,}원",
        f"개발비: {estimate['development']:,}원",
        f"인프라비: {estimate['infra']:,}원",
        f"공급가: {estimate['supply_total']:,}원",
        f"VAT: {estimate['vat']:,}원",
        f"총합계: {estimate['grand_total']:,}원",
        f"유지보수: {estimate['maintenance']:,}원/월",
    ]
    for line in cost_lines:
        toggle_children.append({
            "object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"text": {"content": line}}]}
        })

    # 견적서 링크
    if estimate_notion_result.get("success") and estimate_notion_result.get("url"):
        toggle_children.append({
            "object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"text": {"content": f"견적서: {estimate_notion_result['url']}", "link": {"url": estimate_notion_result["url"]}}}]}
        })

    # ── 작업 진행 로그 ──
    toggle_children.append({
        "object": "block", "type": "divider", "divider": {}
    })
    toggle_children.append({
        "object": "block", "type": "heading_3",
        "heading_3": {"rich_text": [{"text": {"content": "작업 진행 로그"}}]}
    })
    toggle_children.append({
        "object": "block", "type": "paragraph",
        "paragraph": {"rich_text": [{"text": {"content": f"[{today}] 견적 접수 완료"}}]}
    })

    # 토글 블록 (toggle heading_2)
    toggle_block = {
        "object": "block",
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"text": {"content": toggle_title}}],
            "is_toggleable": True,
            "children": toggle_children
        }
    }

    return toggle_block


def search_existing_customer(company_name):
    """고객 리스트 DB에서 상호로 기존 고객 검색

    Returns:
        dict: {"found": True, "page_id": "...", "url": "..."} 또는 {"found": False}
    """
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # 상호 필드(title)에서 검색
    payload = {
        "filter": {
            "property": "상호",
            "title": {
                "equals": company_name
            }
        },
        "page_size": 1
    }

    try:
        resp = requests.post(
            f"{NOTION_API}/databases/{CUSTOMER_DB_ID}/query",
            headers=headers, json=payload, timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            if results:
                page = results[0]
                page_id = page["id"]
                page_id_clean = page_id.replace("-", "")
                return {
                    "found": True,
                    "page_id": page_id,
                    "url": f"https://www.notion.so/{page_id_clean}",
                    "properties": page.get("properties", {})
                }
        return {"found": False}
    except Exception as e:
        print(f"고객 검색 실패: {e}", file=sys.stderr)
        return {"found": False, "error": str(e)}


def _count_existing_orders(page_id):
    """기존 고객 페이지의 본문 토글 블록 수를 세어 의뢰 차수 계산

    Returns:
        int: 기존 의뢰 수 (토글 heading_2 블록 수)
    """
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    try:
        resp = requests.get(
            f"{NOTION_API}/blocks/{page_id}/children?page_size=100",
            headers=headers, timeout=30
        )
        if resp.status_code == 200:
            blocks = resp.json().get("results", [])
            # 토글 heading_2 블록 수 = 기존 의뢰 수
            toggle_count = 0
            for block in blocks:
                if block.get("type") == "heading_2":
                    h2_data = block.get("heading_2", {})
                    if h2_data.get("is_toggleable", False):
                        toggle_count += 1
            return toggle_count
        return 0
    except Exception:
        return 0


def append_to_customer_page(page_id, form_data, estimate, estimate_notion_result):
    """기존 고객 페이지에 새 의뢰 토글 블록 추가 + 속성 업데이트

    Args:
        page_id: 기존 고객 Notion 페이지 ID
        form_data: 폼 데이터
        estimate: 견적 산출 결과
        estimate_notion_result: 견적서 페이지 생성 결과

    Returns:
        dict: {"success": True/False, ...}
    """
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # 기존 의뢰 수 확인 → N+1차 의뢰
    existing_count = _count_existing_orders(page_id)
    order_num = existing_count + 1

    # 1. 속성 업데이트 (작업상태, 의뢰내용 갱신, 견적서 링크 추가)
    today = datetime.now().strftime("%Y-%m-%d")
    project_name = form_data.get("project_name", "미정")
    new_order_summary = f"[{order_num}차] {form_data.get('project_type', '기본형')} / {form_data.get('page_count', 5)}페이지 / 총 {estimate['grand_total']:,}원"

    properties_update = {
        "작업상태": {"select": {"name": "접수"}},
        "의뢰내용": {"rich_text": [{"text": {"content": new_order_summary}}]},
    }

    # 견적서 링크 (최신 것으로 갱신)
    if estimate_notion_result.get("success") and estimate_notion_result.get("url"):
        estimate_url = estimate_notion_result["url"]
        properties_update["견적서"] = {
            "rich_text": [{"text": {"content": f"[{order_num}차] {estimate_url}", "link": {"url": estimate_url}}}]
        }

    try:
        # 속성 업데이트
        resp = requests.patch(
            f"{NOTION_API}/pages/{page_id}",
            headers=headers,
            json={"properties": properties_update},
            timeout=30
        )
        if resp.status_code != 200:
            return {"success": False, "error": f"속성 업데이트 실패: HTTP {resp.status_code}: {resp.text[:200]}"}

        # 2. 본문에 새 토글 블록 append
        toggle_block = _build_order_toggle(form_data, estimate, estimate_notion_result, order_num)

        resp2 = requests.patch(
            f"{NOTION_API}/blocks/{page_id}/children",
            headers=headers,
            json={"children": [toggle_block]},
            timeout=30
        )
        if resp2.status_code == 200:
            page_id_clean = page_id.replace("-", "")
            return {
                "success": True,
                "page_id": page_id,
                "url": f"https://www.notion.so/{page_id_clean}",
                "order_num": order_num,
                "is_existing": True
            }
        else:
            return {"success": False, "error": f"토글 추가 실패: HTTP {resp2.status_code}: {resp2.text[:200]}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def create_customer_page(form_data, estimate, estimate_notion_result):
    """고객 리스트 DB에 신규 고객 페이지 생성 (속성 + 토글 블록 본문)"""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # 속성 입력
    properties = {
        "상호": {"title": [{"text": {"content": form_data.get("client_name", form_data.get("project_name", "미정"))}}]},
        "서비스유형": {"select": {"name": "홈페이지"}},
        "작업상태": {"select": {"name": "접수"}},
        "의뢰일": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
        "의뢰내용": {"rich_text": [{"text": {"content": f"{form_data.get('project_type', '기본형')} / {form_data.get('page_count', 5)}페이지 / 총 {estimate['grand_total']:,}원"}}]},
    }

    if form_data.get("contact_person"):
        properties["담당자"] = {"rich_text": [{"text": {"content": form_data["contact_person"]}}]}
    if form_data.get("phone"):
        properties["연락처"] = {"phone_number": form_data["phone"]}
    if form_data.get("email"):
        properties["이메일"] = {"email": form_data["email"]}
    if form_data.get("customer_type"):
        properties["고객유형"] = {"select": {"name": form_data["customer_type"]}}
    if form_data.get("business_number"):
        properties["사업자번호"] = {"rich_text": [{"text": {"content": form_data["business_number"]}}]}
    if form_data.get("address"):
        properties["주소"] = {"rich_text": [{"text": {"content": form_data["address"]}}]}
    if form_data.get("notes"):
        properties["비고"] = {"rich_text": [{"text": {"content": form_data["notes"]}}]}

    # 견적서 링크
    if estimate_notion_result.get("success") and estimate_notion_result.get("url"):
        properties["견적서"] = {"rich_text": [{"text": {"content": estimate_notion_result["url"], "link": {"url": estimate_notion_result["url"]}}}]}

    # 본문: 토글 블록으로 구성 (1차 의뢰)
    toggle_block = _build_order_toggle(form_data, estimate, estimate_notion_result, order_num=1)
    children = [toggle_block]

    payload = {
        "parent": {"database_id": CUSTOMER_DB_ID},
        "properties": properties,
        "children": children
    }

    try:
        resp = requests.post(f"{NOTION_API}/pages", headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            page = resp.json()
            page_id = page["id"].replace("-", "")
            return {"success": True, "page_id": page["id"], "url": f"https://www.notion.so/{page_id}", "order_num": 1, "is_existing": False}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_discord_notification(form_data, estimate, notion_result, doc_result=None):
    """Discord로 견적서 알림 전송 (대표님 검토용)"""
    supply = estimate["supply_total"]
    vat = estimate["vat"]
    total = estimate["grand_total"]

    features_str = ", ".join(estimate["feature_details"]) if estimate["feature_details"] else "없음"

    msg = (
        f"**[견적서 접수] {form_data.get('project_name', '미정')}**\n\n"
        f"고객: {form_data.get('client_name', '-')} / {form_data.get('contact_person', '-')}\n"
        f"유형: {form_data.get('project_type', '-')} | 디자인: {form_data.get('design_grade', '-')} | {form_data.get('page_count', 5)}페이지\n"
        f"추가기능: {features_str}\n\n"
        f"**가견적 (VAT별도)**\n"
        f"- 기획: {estimate['planning']:,}원\n"
        f"- 디자인: {estimate['design']:,}원\n"
        f"- 개발: {estimate['development']:,}원\n"
        f"- 인프라: {estimate['infra']:,}원\n"
        f"- **공급가: {supply:,}원**\n"
        f"- VAT: {vat:,}원\n"
        f"- **총합계: {total:,}원**\n"
        f"- 유지보수: {estimate['maintenance']:,}원/월\n\n"
    )

    if notion_result.get("success"):
        msg += f"Notion 견적: {notion_result['url']}\n"
    if doc_result and doc_result.get("success"):
        msg += f"견적서 문서: {doc_result['url']}\n"
    if notion_result.get("success") or (doc_result and doc_result.get("success")):
        msg += "대표님 검토 후 고객에게 전달해주세요."
    else:
        msg += f"Notion 생성 실패: {notion_result.get('error', '알 수 없는 오류')}"

    data = {
        "message": msg,
        "channelId": ESTIMATE_CHANNEL,
        "sender": "main",
        "client_id": CLIENT_ID
    }
    try:
        requests.post(N8N_WEBHOOK, json=data, timeout=10)
    except Exception as e:
        print(f"Discord 알림 실패: {e}", file=sys.stderr)


# ── 견적서 문서 생성 (견적서(배포) 하위 페이지) ──

def _fmt_won(amount):
    """금액을 원 단위 콤마 포맷"""
    return f"{int(amount):,}"


def _rt(content, bold=False):
    """Notion rich_text element 헬퍼"""
    rt = {"type": "text", "text": {"content": content}}
    if bold:
        rt["annotations"] = {"bold": True}
    return rt


def _build_estimate_doc_blocks(form_data, estimate):
    """견적서 페이지 본문 블록 배열 생성 (Notion API 2레벨 중첩 제한 준수)

    callout 블록은 rich_text에 모든 내용을 포함하여 2레벨 이내 유지.
    column_list → column → callout(rich_text only) = 2레벨.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    valid_until = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    project_type = form_data.get("project_type", "기본형")
    page_count = form_data.get("page_count", 5)
    design_grade = form_data.get("design_grade", "맞춤")
    features = form_data.get("features", [])
    features_str = ", ".join(features) if features else "기본"
    notes = form_data.get("notes", "")

    # 고객 정보 텍스트
    customer_lines = []
    if form_data.get("client_name"):
        customer_lines.append(f"상호/성명: {form_data['client_name']}")
    if form_data.get("contact_person"):
        customer_lines.append(f"담당자: {form_data['contact_person']}")
    if form_data.get("phone"):
        customer_lines.append(f"연락처: {form_data['phone']}")
    if form_data.get("email"):
        customer_lines.append(f"이메일: {form_data['email']}")
    customer_text = "\n".join(customer_lines) if customer_lines else "정보 없음"

    blocks = []

    # ── 1. Divider ──
    blocks.append({"object": "block", "type": "divider", "divider": {}})

    # ── 2. 견적일자 | 유효기간 ──
    blocks.append({
        "object": "block", "type": "column_list",
        "column_list": {"children": [
            {"object": "block", "type": "column", "column": {"children": [
                {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [
                    _rt("견적일자: ", bold=True), _rt(today)
                ]}}
            ]}},
            {"object": "block", "type": "column", "column": {"children": [
                {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [
                    _rt("유효기간: ", bold=True), _rt(valid_until)
                ]}}
            ]}}
        ]}
    })

    # ── 3. Divider ──
    blocks.append({"object": "block", "type": "divider", "divider": {}})

    # ── 4. 공급자 | 고객 (callout in columns, rich_text only — no children) ──
    blocks.append({
        "object": "block", "type": "column_list",
        "column_list": {"children": [
            {"object": "block", "type": "column", "column": {"children": [
                {"object": "block", "type": "callout", "callout": {
                    "icon": {"emoji": "🏢"},
                    "rich_text": [
                        _rt("공급자\n", bold=True),
                        _rt(f"상호: {SUPPLIER_INFO['company']}\n"
                            f"대표: {SUPPLIER_INFO['representative']}\n"
                            f"연락처: {SUPPLIER_INFO['phone']}\n"
                            f"이메일: {SUPPLIER_INFO['email']}")
                    ],
                    "color": "blue_background"
                }}
            ]}},
            {"object": "block", "type": "column", "column": {"children": [
                {"object": "block", "type": "callout", "callout": {
                    "icon": {"emoji": "🙍"},
                    "rich_text": [
                        _rt("고객\n", bold=True),
                        _rt(customer_text)
                    ],
                    "color": "yellow_background"
                }}
            ]}}
        ]}
    })

    # ── 5. Divider ──
    blocks.append({"object": "block", "type": "divider", "divider": {}})

    # ── 6. 견적 내용 Heading ──
    blocks.append({
        "object": "block", "type": "heading_3",
        "heading_3": {"rich_text": [_rt("✅ 견적 내용")]}
    })

    # ── 7. 견적 테이블 (7열) ──
    def _row(cells):
        """테이블 행. cells: list of str or (str, True) for bold"""
        return {"type": "table_row", "table_row": {"cells": [
            [_rt(c[0], bold=True)] if isinstance(c, tuple) else [_rt(str(c))]
            for c in cells
        ]}}

    table_rows = [
        _row([("구분", True), ("내용", True), ("수량", True),
              ("단가(원)", True), ("공급가(원)", True), ("부가세(원)", True), ("합계금액(원)", True)]),
        _row(["기획", "프로젝트 기획/분석", "1식",
              _fmt_won(estimate["planning"]), _fmt_won(estimate["planning"]),
              "-", _fmt_won(estimate["planning"])]),
        _row(["디자인", f"UI/UX 디자인 ({design_grade}, {page_count}p)", "1식",
              _fmt_won(estimate["design"]), _fmt_won(estimate["design"]),
              "-", _fmt_won(estimate["design"])]),
        _row(["개발", f"{project_type} 개발 ({features_str})", "1식",
              _fmt_won(estimate["development"]), _fmt_won(estimate["development"]),
              "-", _fmt_won(estimate["development"])]),
        _row(["인프라", "도메인/호스팅/SSL", "1식",
              _fmt_won(estimate["infra"]), _fmt_won(estimate["infra"]),
              "-", _fmt_won(estimate["infra"])]),
        _row(["유지보수", "월 유지보수", "월",
              _fmt_won(estimate["maintenance"]), _fmt_won(estimate["maintenance"]),
              "-", _fmt_won(estimate["maintenance"])]),
        _row([("총합계", True), "", "", "",
              (_fmt_won(estimate["supply_total"]), True),
              (_fmt_won(estimate["vat"]), True),
              (_fmt_won(estimate["grand_total"]), True)]),
    ]

    blocks.append({
        "object": "block", "type": "table",
        "table": {
            "table_width": 7,
            "has_column_header": True,
            "has_row_header": False,
            "children": table_rows
        }
    })

    # ── 8. Divider ──
    blocks.append({"object": "block", "type": "divider", "divider": {}})

    # ── 9. 비고 | 결제 안내 ──
    notes_body = ("• 상기 금액은 부가세 별도입니다.\n"
                  "• 추가 기능 및 페이지 추가 시 별도 협의합니다.\n"
                  "• 유지보수는 월 단위 계약입니다.")
    if notes:
        notes_body += f"\n• {notes}"

    blocks.append({
        "object": "block", "type": "column_list",
        "column_list": {"children": [
            {"object": "block", "type": "column", "column": {"children": [
                {"object": "block", "type": "callout", "callout": {
                    "icon": {"emoji": "📝"},
                    "rich_text": [_rt("비고\n", bold=True), _rt(notes_body)],
                    "color": "gray_background"
                }}
            ]}},
            {"object": "block", "type": "column", "column": {"children": [
                {"object": "block", "type": "callout", "callout": {
                    "icon": {"emoji": "💳"},
                    "rich_text": [_rt("결제 안내\n", bold=True), _rt(
                        "• 계약금: 총액의 50% (착수 시)\n"
                        "• 잔금: 총액의 50% (납품 완료 시)\n"
                        "• 세금계산서 발행 가능"
                    )],
                    "color": "green_background"
                }}
            ]}}
        ]}
    })

    # ── 10. Divider ──
    blocks.append({"object": "block", "type": "divider", "divider": {}})

    return blocks


def create_estimate_document(form_data, estimate, estimate_page_id=None):
    """견적서(배포) 하위에 '견적서_{고객명}_{날짜}' 페이지 생성

    Args:
        form_data: 폼 데이터
        estimate: calculate_estimate() 결과
        estimate_page_id: 견적 DB 페이지 ID (역링크용, optional)

    Returns:
        dict: {"success": True, "page_id": ..., "url": ...}
    """
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    today = datetime.now().strftime("%Y-%m-%d")
    client_name = form_data.get("client_name", form_data.get("project_name", "미정"))
    page_title = f"견적서_{client_name}_{today}"

    blocks = _build_estimate_doc_blocks(form_data, estimate)
    grand_total = estimate.get("grand_total", estimate["supply_total"] + estimate["vat"])

    # 견적서(배포) DB에 페이지 생성
    properties = {
        "견적서명": {"title": [{"text": {"content": page_title}}]},
        "고객명": {"rich_text": [{"text": {"content": client_name}}]},
        "총금액": {"number": grand_total},
        "상태": {"select": {"name": "발송대기"}},
        "발행일": {"date": {"start": today}},
    }
    # 견적DB 역링크 (relation)
    if estimate_page_id:
        properties["견적DB연결"] = {"relation": [{"id": estimate_page_id}]}

    payload = {
        "parent": {"database_id": ESTIMATE_DOC_DB},
        "properties": properties,
        "children": blocks
    }

    try:
        resp = requests.post(
            f"{NOTION_API}/pages", headers=headers, json=payload, timeout=30
        )
        if resp.status_code == 200:
            page = resp.json()
            page_id = page["id"]
            page_url = f"https://www.notion.so/{page_id.replace('-', '')}"

            # 견적 DB에 견적서URL 역링크
            if estimate_page_id:
                _update_estimate_doc_url(estimate_page_id, page_url, headers)

            return {"success": True, "page_id": page_id, "url": page_url}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:500]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _update_estimate_doc_url(estimate_page_id, doc_url, headers):
    """견적 DB 페이지에 견적서URL 속성 기록"""
    try:
        requests.patch(
            f"{NOTION_API}/pages/{estimate_page_id}",
            headers=headers,
            json={"properties": {"견적서URL": {"url": doc_url}}},
            timeout=15
        )
    except Exception:
        pass


def _append_callout_children(callout_block_id, items):
    """callout 블록에 children 블록 추가 (Notion 2레벨 제한 우회용)

    Args:
        callout_block_id: callout 블록 ID
        items: [{"heading": "제목", "bullets": ["항목1", ...]}, ...]
    """
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    children = []
    for item in items:
        if item.get("heading"):
            children.append({
                "object": "block", "type": "heading_3",
                "heading_3": {"rich_text": [_rt(item["heading"], bold=True)]}
            })
        for bullet in item.get("bullets", []):
            children.append({
                "object": "block", "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [_rt(bullet)]}
            })

    if children:
        try:
            requests.patch(
                f"{NOTION_API}/blocks/{callout_block_id}/children",
                headers=headers, json={"children": children}, timeout=15
            )
        except Exception:
            pass


def main():
    # 입력 읽기 (파일 또는 stdin)
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        with open(input_path, "r", encoding="utf-8") as f:
            form_data = json.load(f)
    else:
        form_data = json.load(sys.stdin)

    # 1. 가견적 산출
    estimate = calculate_estimate(form_data)

    # 2. Notion 견적 페이지 생성 (견적서 DB)
    notion_result = create_notion_page(form_data, estimate)

    # 2.5. 견적서 문서 페이지 생성 (견적서(배포) 하위)
    estimate_page_id = notion_result.get("page_id") if notion_result.get("success") else None
    doc_result = create_estimate_document(form_data, estimate, estimate_page_id)

    # 3. 고객 리스트 DB: 기존 고객 검색 → 신규/기존 분기
    client_name = form_data.get("client_name", form_data.get("project_name", "미정"))
    existing = search_existing_customer(client_name)

    if existing.get("found"):
        # 기존 고객: 페이지에 새 토글 블록 추가 + 속성 갱신
        customer_result = append_to_customer_page(
            existing["page_id"], form_data, estimate, notion_result
        )
    else:
        # 신규 고객: 새 페이지 생성 (토글 블록 형식)
        customer_result = create_customer_page(form_data, estimate, notion_result)

    # 4. Discord 알림 (대표님에게)
    send_discord_notification(form_data, estimate, notion_result, doc_result)

    # 5. 결과 출력
    result = {
        "estimate": {
            "planning": estimate["planning"],
            "design": estimate["design"],
            "development": estimate["development"],
            "infra": estimate["infra"],
            "maintenance": estimate["maintenance"],
            "supply_total": estimate["supply_total"],
            "vat": estimate["vat"],
            "grand_total": estimate["grand_total"],
        },
        "notion_estimate": notion_result,
        "estimate_document": doc_result,
        "notion_customer": customer_result,
        "customer_is_existing": existing.get("found", False),
        "features": estimate["feature_details"]
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
