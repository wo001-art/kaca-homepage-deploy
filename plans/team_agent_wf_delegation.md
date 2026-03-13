# 팀에이전트 WF 위임 구현 계획

> 목표: 팀에이전트가 Claude 토큰 대신 WF 도구로 최대한 작업하도록 구조 변경
> 작성일: 2026-03-13

---

## 1. 현황 분석

### 에이전트별 토큰 소비 구조

| 에이전트 | 현재 토큰 사용 | WF 위임 가능 비율 |
|----------|---------------|-----------------|
| PM | 상태관리/디스패치/품질검수 | 낮음 (판단 로직) |
| Research | 사이트분석 + 트렌드조사 + 리포트 작성 | **높음 (분석은 WF, 리포트만 Claude)** |
| Planning/UX | 사이트맵/와이어프레임/UX흐름도/제작가이드 | 중간 (템플릿 기반 자동생성 가능) |
| Design | 디자인시스템 + HTML/Tailwind 시안 | 중간 (참고사이트 분석은 WF) |
| Frontend | Next.js 페이지/컴포넌트 코드 작성 | 낮음 (코드 생성은 Claude 필수) |
| Backend | API/CMS/기능 구현 | 중간 (Notion/배포는 WF) |

### 현재 WF 도구 (통합 WF: hp-agent-tool)

| action | 상태 | 사용 에이전트 |
|--------|------|-------------|
| site-analyze | ✅ 딥리서치v2 | Research |
| trend-crawl | ✅ 딥리서치v2 | Research |
| contact-form | ✅ Notion API | Backend |
| deploy | ✅ Vercel API | Backend |
| lighthouse | ⏸ 보류 | Frontend |
| screenshot | ⏸ 보류 | Design |

---

## 2. 새로 추가할 WF 브랜치

### 2-1. `generate-sitemap` (Planning/UX용)

**목적**: 고객 요구사항 → 사이트맵 자동 생성 (Perplexity 분석 기반)
**구현**: 딥리서치v2 호출 → "이 업종/규모에 적합한 사이트맵 제안" 프롬프트
**입력**: `{action: "generate-sitemap", data: {industry, page_count, features[], reference_url}}`
**출력**: `{pages: [{name, path, description, priority}], recommended_structure}`
**절약 효과**: Planning/UX 에이전트의 사이트맵 초안 작업 토큰 절감

### 2-2. `generate-design-tokens` (Design용)

**목적**: 참고사이트 분석 → 컬러/폰트/간격 디자인 토큰 자동 추출
**구현**: 딥리서치v2 호출 → "이 사이트의 디자인 시스템 분석" + JSON 포맷 요청
**입력**: `{action: "generate-design-tokens", data: {reference_url, industry, mood}}`
**출력**: `{colors: {primary, secondary, accent, bg, text}, fonts: {heading, body}, spacing, border_radius}`
**절약 효과**: Design 에이전트의 디자인 시스템 초안 토큰 절감

### 2-3. `generate-page-template` (Frontend용)

**목적**: 페이지 유형별 Next.js 보일러플레이트 코드 자동 생성
**구현**: n8n Code 노드에서 템플릿 엔진으로 생성 (Claude 토큰 0)
**입력**: `{action: "generate-page-template", data: {page_type, page_name, features[], design_tokens}}`
**출력**: `{code: "// Next.js page code...", layout: "...", components: [...]}`
**페이지 타입별 템플릿**:
  - `hero`: Hero 섹션 + CTA
  - `about`: 소개 + 임원진 그리드
  - `gallery`: Masonry 그리드 + 모달 + 필터
  - `contact`: 폼 + FAQ 아코디언
  - `notice`: 카테고리탭 + 페이지네이션
  - `events`: 카드 그리드 + 타임라인
  - `programs`: 프로그램 카드 + 상세 토글
  - `members`: 로그인 + 회원전용 컨텐츠
  - `shop`: 상품 그리드 + 결제
  - `admin`: 대시보드 레이아웃
**절약 효과**: Frontend 에이전트가 0부터 코드 작성 → 템플릿 기반 수정으로 토큰 대폭 절감

### 2-4. `notion-cms-setup` (Backend용)

**목적**: 페이지 구조에 맞는 Notion DB 자동 생성 + API Route 코드 생성
**구현**: Notion API로 DB 생성 + Code 노드에서 API 코드 템플릿 생성
**입력**: `{action: "notion-cms-setup", data: {pages: [{name, fields}], project_slug}}`
**출력**: `{databases: [{name, id, properties}], api_code: "..."}`
**절약 효과**: Backend 에이전트의 Notion 설정 + API Route 작성 토큰 절감

### 2-5. `seo-generate` (Frontend용)

**목적**: 페이지별 SEO 메타데이터 자동 생성
**구현**: Perplexity로 업종+페이지 분석 → SEO 메타 JSON 생성
**입력**: `{action: "seo-generate", data: {page_name, industry, description, keywords[]}}`
**출력**: `{title, description, og_title, og_description, keywords[], structured_data}`
**절약 효과**: Frontend 에이전트의 SEO 설정 토큰 절감

### 2-6. `validate-code` (공통)

**목적**: 생성된 코드의 문법/린트 검증 (Claude 대신 WF에서 처리)
**구현**: Code 노드에서 기본 검증 (JSON parse, 필수 import 확인, 파일 구조 체크)
**입력**: `{action: "validate-code", data: {code, file_type, expected_exports[]}}`
**출력**: `{valid: true/false, errors: [], warnings[]}`
**절약 효과**: 에이전트 재시도 횟수 감소

---

## 3. 패키지별 WF 호출 플로우

### Basic (5페이지, 10항목)

```
Research 에이전트
  ├─ WF: site-analyze (참고사이트 분석)          ← WF
  ├─ WF: trend-crawl (업종 트렌드)              ← WF
  └─ Claude: 리포트 정리 (최소화)               ← 토큰

Planning/UX 에이전트
  ├─ WF: generate-sitemap (5페이지 구조)        ← WF [신규]
  └─ Claude: 와이어프레임/가이드 보정            ← 토큰 (최소)

Design 에이전트
  ├─ WF: generate-design-tokens (디자인 토큰)   ← WF [신규]
  └─ Claude: 시안 HTML 작성                     ← 토큰

Frontend 에이전트
  ├─ WF: generate-page-template × 5페이지       ← WF [신규]
  ├─ WF: seo-generate × 5페이지                 ← WF [신규]
  └─ Claude: 템플릿 커스텀 수정만                ← 토큰 (대폭 절감)

Backend 에이전트
  ├─ WF: notion-cms-setup (DB+API 자동생성)     ← WF [신규]
  ├─ WF: contact-form (문의폼 연동)             ← WF
  ├─ WF: deploy (Vercel 배포)                   ← WF
  └─ Claude: 특수 로직만                         ← 토큰 (최소)
```

### Standard (7페이지, 15항목) — Basic + 추가분

```
추가 WF 호출:
  ├─ WF: generate-page-template × 2 (갤러리, 공지)  ← WF
  ├─ WF: seo-generate × 2                            ← WF
  └─ Claude: 검색/필터 로직, Band 동기화 커스텀       ← 토큰
```

### Premium (10페이지, 21항목) — Standard + 추가분

```
추가 WF 호출:
  ├─ WF: generate-page-template × 3 (회원, 결제, 관리자)  ← WF
  ├─ WF: seo-generate × 3                                   ← WF
  └─ Claude: 인증/결제/다국어 로직                            ← 토큰
```

---

## 4. 예상 토큰 절감율

| 에이전트 | Before (토큰) | After (토큰) | 절감율 |
|----------|-------------|------------|--------|
| Research | ~50K | ~15K (리포트 정리만) | **70%** |
| Planning/UX | ~40K | ~15K (사이트맵 보정만) | **60%** |
| Design | ~60K | ~30K (시안 작성만) | **50%** |
| Frontend | ~150K | ~50K (템플릿 커스텀만) | **65%** |
| Backend | ~80K | ~30K (특수 로직만) | **60%** |
| PM | ~20K | ~20K (변동 없음) | 0% |
| **합계** | **~400K** | **~160K** | **~60%** |

---

## 5. 구현 순서

### Phase 1: 통합 WF 엔드포인트 정리 (즉시)
- [ ] wf_client.py: 6개 개별 엔드포인트 → 단일 `hp-agent-tool` 통합
- [ ] 호출 방식: `call_wf("hp-agent-tool", {action: "site-analyze", data: {...}})`

### Phase 2: 코드 템플릿 브랜치 추가 (핵심, 최대 토큰 절감)
- [ ] `generate-page-template`: 10개 페이지 타입 템플릿
- [ ] `seo-generate`: SEO 메타데이터 자동 생성
- [ ] `validate-code`: 코드 검증

### Phase 3: 기획/디자인 자동화 브랜치 추가
- [ ] `generate-sitemap`: 사이트맵 자동 생성
- [ ] `generate-design-tokens`: 디자인 토큰 추출

### Phase 4: 백엔드 자동화 브랜치 추가
- [ ] `notion-cms-setup`: Notion DB + API Route 자동 생성

### Phase 5: 에이전트 프롬프트 최적화
- [ ] 각 에이전트 프롬프트에 "WF 도구 우선 사용" 지시 추가
- [ ] 프롬프트 경량화 (불필요한 설명 제거, 핵심 지시만)
- [ ] 체크리스트 마킹 자동화 (WF 완료 시 자동 mark)

---

## 6. wf_client.py 변경 사항

```python
# Before: 6개 개별 엔드포인트
WF_ENDPOINTS = {
    "site-analyzer": "/webhook/hp-site-analyzer",
    "trend-crawler": "/webhook/hp-trend-crawler",
    ...
}

# After: 단일 통합 엔드포인트
AGENT_TOOL_URL = "https://n8n.wookvan.com/webhook/hp-agent-tool"

def call_agent_tool(action: str, data: dict, timeout=120):
    """통합 에이전트 도구 WF 호출"""
    return call_wf_raw(AGENT_TOOL_URL, {"action": action, "data": data}, timeout)
```

---

## 7. 통합 WF Switch 브랜치 최종 구조

```
hp-agent-tool (Webhook)
  └─ Switch (action)
       ├─ site-analyze      → 딥리서치v2 호출
       ├─ trend-crawl        → 딥리서치v2 호출
       ├─ contact-form       → Notion API
       ├─ deploy             → Vercel API
       ├─ generate-sitemap   → 딥리서치v2 + Code 포맷 [신규]
       ├─ generate-design-tokens → 딥리서치v2 + Code 추출 [신규]
       ├─ generate-page-template → Code 템플릿 엔진 [신규]
       ├─ notion-cms-setup   → Notion API + Code 생성 [신규]
       ├─ seo-generate       → 딥리서치v2 + Code 포맷 [신규]
       ├─ validate-code      → Code 검증 [신규]
       ├─ lighthouse         → PageSpeed API [보류]
       └─ screenshot         → 캡처 API [보류]
```

총 12개 브랜치 (활성 10개 + 보류 2개)
