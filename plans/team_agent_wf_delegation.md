# 홈페이지 제작 팀에이전트 → n8n WF 전환 구현 가이드

> **목표**: n8n WF가 메인 오케스트레이터. AI Agent/Code 노드로 작업 수행. Claude 토큰 → 거의 0
> **작성일**: 2026-03-13 (v3 테크니컬 라이터 검수)
> **대상 독자**: n8n WF 구축자 (Claude / 코어AI)

---

## 목차

1. [아키텍처 개요](#1-아키텍처-개요)
2. [Notion DB 스키마](#2-notion-db-스키마)
3. [n8n Credential 매핑](#3-n8n-credential-매핑)
4. [패키지별 WF 구조](#4-패키지별-wf-구조)
5. [Phase별 입출력 데이터 스키마](#5-phase별-입출력-데이터-스키마)
6. [페이지 템플릿 상세](#6-페이지-템플릿-상세)
7. [승인 게이트 (고객 확인 단계)](#7-승인-게이트)
8. [에러 핸들링 및 재시도](#8-에러-핸들링-및-재시도)
9. [기존 팀에이전트 단순화](#9-기존-팀에이전트-단순화)
10. [기존 도구 WF 연계](#10-기존-도구-wf-연계)
11. [테스트 전략](#11-테스트-전략)
12. [마이그레이션 경로](#12-마이그레이션-경로)
13. [구현 순서](#13-구현-순서)
14. [Before vs After 비교](#14-before-vs-after-비교)

---

## 1. 아키텍처 개요

### Before (Claude 에이전트 중심)

```
메인 에이전트 (Opus)
  └─ PM (Sonnet) ─→ Research (Sonnet) ─→ Planning (Sonnet)
                     ─→ Design (Sonnet) ─→ Frontend (Sonnet) ─→ Backend (Sonnet)
```

- 6개 에이전트, 전부 Sonnet, 토큰 ~400K/프로젝트
- Python 오케스트레이터 (homepage_orchestrator.py) + 상태관리 (state_manager.py)

### After (n8n WF 중심)

```
고객 의뢰 (Notion 상태변경 → "접수")
  → Webhook 트리거 (hp-estimate-trigger)
    → 패키지 판별 Switch
      → WF-Basic / WF-Standard / WF-Premium
        → Phase 1~7 자동 실행 (AI Agent + Code 노드)
          → 결과물 GitHub/Vercel/Notion에 자동 업로드
            → Discord 완료 알림
```

- n8n WF가 오케스트레이터
- AI 작업: Gemini 2.0 Flash + Perplexity sonar-pro (Claude 토큰 = 0)
- 코드 생성: Code 노드 템플릿 (JS, 토큰 = 0)
- 병렬 처리: Switch + Merge

---

## 2. Notion DB 스키마

### 홈페이지견적 DB

| 필드 | ID | 타입 | 용도 |
|------|-----|------|------|
| 프로젝트명 | title | title | 의뢰 제목 |
| 고객명 | Y<Bm | rich_text | 고객 이름 |
| 상태 | m^<~ | **select** | 접수 → 진행 → 시안확인 → 개발 → 검수 → 완료 |
| 프로젝트유형 | cKN{ | select | 신규제작 / 리뉴얼 / 유지보수 |
| 페이지수 | CM{g | number | 패키지 자동 판별 기준 |
| 필요기능 | ~VJg | multi_select | 갤러리, 검색, Band동기화, 로그인, 결제, 다국어 등 |
| 예산범위 | kn{N | select | ~100만 / 100~150만 / 150~200만 / 200만+ |
| 참고사이트 | K]MR | url | 리서치 입력값 |
| 이메일 | A<h{ | email | 고객 연락처 |
| 연락처 | O\V~ | phone_number | 고객 연락처 |
| 견적서URL | _Jg} | url | 완료 시 자동 입력 |
| 비고 | ;HA? | rich_text | 문의 내용 |
| DB ID | - | - | `3ddbf37e-258c-4941-8bf0-3698bc1d928a` |

### 고객리스트 DB

| 필드 | 타입 | 용도 |
|------|------|------|
| 고객명 | title | 고객 식별 |
| 연락처 | phone_number | 전화번호 |
| 이메일 | email | 이메일 |
| 의뢰내역 | relation → 홈페이지견적 | 의뢰 연결 |
| 메모 | rich_text | 누적 이력 |
| DB ID | - | `181d1c32-1694-80a7-8b50-c4b9ad2fbbfc` |

### 기획안 페이지

- **페이지 ID**: `312765eb-4694-81c9-abe6-c9fca885b43e`
- 제작 완료 시 결과 요약 블록 append

---

## 3. n8n Credential 매핑

| Credential | 타입 | 사용 노드 | 비고 |
|------------|------|----------|------|
| Gemini API | Header Auth | AI Agent (사이트맵/SEO/디자인토큰) | `AIzaSyB4WYF4LnMMWNYR1TkHKGSH6IbYLO5KRzs` |
| Perplexity API | Perplexity API (`mvKpz4kWcVc1BsJH`) | 딥리서치v2 WF (내부) | WF 호출이므로 직접 불필요 |
| Notion API | Header Auth | HTTP Request (DB CRUD) | `ntn_31774688...` |
| Vercel Token | Header Auth | HTTP Request (배포) | `Bearer vcp_1P4Q...` |
| GitHub PAT | Header Auth | HTTP Request (push_files) | API 키 관리.md 참조 |
| Discord (WIN Message Gate) | 없음 (Webhook) | HTTP Request | URL만 사용 |

### Credential 보안 규칙

- API 키는 n8n Credential에 저장 (WF JSON에 하드코딩 금지)
- 환경변수: Notion/Vercel/GitHub 토큰은 n8n 환경변수로 관리
- 생성 코드 내 `.env.local` 템플릿만 포함 (실제 값은 배포 시 Vercel 환경변수에 설정)

---

## 4. 패키지별 WF 구조

### 패키지 자동 판별 로직

```javascript
// Notion 견적DB에서 읽어온 데이터 기준
const pageCount = input.페이지수 || 5;
const features = input.필요기능 || [];

if (pageCount >= 10 || features.some(f => ['로그인','결제','다국어'].includes(f))) {
  return 'premium';
} else if (pageCount >= 7 || features.some(f => ['갤러리','공지사항','검색','Band동기화'].includes(f))) {
  return 'standard';
} else {
  return 'basic';
}
```

### 4-1. WF-Basic (5페이지, 80~100만)

```
[Webhook: hp-homepage-build]
  │
  ├─ Code: 패키지 판별 → basic
  │
  ├─ [Phase 1: 리서치] ──────────────── 병렬
  │   ├─ HTTP → 딥리서치v2 (사이트 분석)
  │   ├─ HTTP → 딥리서치v2 (트렌드 조사)
  │   └─ Merge (리서치 합산)
  │
  ├─ [Phase 2: 기획] ───────────────── 순차
  │   ├─ AI Agent (Gemini) → 사이트맵 5p
  │   └─ Code → 와이어프레임 JSON
  │
  │ ⏸ [승인 게이트: 사이트맵 확인] → Notion 상태 "시안확인" 대기
  │
  ├─ [Phase 3: 디자인] ─────────────── 순차
  │   ├─ AI Agent (Gemini) → 디자인 토큰 추출
  │   └─ Code → tailwind.config + globals.css
  │
  ├─ [Phase 4: 코드 생성] ──────────── 병렬 (핵심)
  │   ├─ Code × 5 → 페이지 템플릿 (hero/about/programs/contact/faq)
  │   ├─ AI Agent (Gemini) → SEO 메타 × 5p
  │   ├─ Code → layout.tsx + Nav + Footer
  │   └─ Merge (전체 코드)
  │
  ├─ [Phase 5: 백엔드] ─────────────── 병렬
  │   ├─ HTTP → Notion CMS DB 생성
  │   ├─ Code → API Route (Notion SDK)
  │   └─ Code → 문의폼 API (/api/contact)
  │
  ├─ [Phase 6: 배포]
  │   ├─ HTTP → GitHub push_files (코드 전체)
  │   ├─ HTTP → Vercel 배포 트리거
  │   └─ AI Agent (Gemini) → 배포 결과 검증
  │
  └─ [Phase 7: 완료]
      ├─ HTTP → Notion 견적DB 상태 → '완료' + 견적서URL
      ├─ HTTP → Notion 고객리스트 업데이트
      └─ HTTP → Discord 완료 알림
```

### 4-2. WF-Standard (7페이지, 120~150만)

Basic 전체 + 아래 추가:

```
[Phase 4 추가 병렬]:
  ├─ Code → 갤러리 (Masonry + 모달 + 필터)
  ├─ Code → 공지사항 (카테고리탭 + 페이지네이션)
  ├─ Code → 전시/이벤트 (카드 그리드 + 타임라인)
  └─ AI Agent (Gemini) → SEO × 2p 추가

[Phase 5 추가]:
  ├─ Code → 검색/필터 컴포넌트
  ├─ Code → Band 동기화 API Route
  └─ Code → ScrollReveal 애니메이션 설정
```

### 4-3. WF-Premium (10페이지, 200~250만)

Standard 전체 + 아래 추가:

```
[Phase 4 추가 병렬]:
  ├─ Code → 회원전용 (로그인 + 보호 라우트)
  ├─ Code → 결제 (상품 그리드 + 토스)
  ├─ Code → 관리자 대시보드
  └─ AI Agent (Gemini) → SEO × 3p 추가

[Phase 5 추가]:
  ├─ Code → NextAuth 인증
  ├─ Code → 토스페이먼츠 연동
  ├─ Code → i18n 다국어 설정
  └─ AI Agent (Gemini) → 구조화 데이터 (JSON-LD)
```

---

## 5. Phase별 입출력 데이터 스키마

### Phase 1: 리서치

**Input** (Webhook에서 전달):
```json
{
  "project_id": "322765eb-...",
  "client_name": "한국아트크래프트협회",
  "reference_url": "https://hawaiifluidart.com/",
  "industry": "아트/공예 협회",
  "features": ["갤러리", "문의폼", "공지사항"],
  "page_count": 7,
  "package": "standard"
}
```

**Output** (Merge 후):
```json
{
  "site_analysis": { "perplexity": "...", "reddit": [...], "youtube": [...] },
  "trend_analysis": { "perplexity": "...", "reddit": [...], "youtube": [...] }
}
```

### Phase 2: 기획

**Input**: Phase 1 Output + 프로젝트 정보
**Output**:
```json
{
  "sitemap": [
    { "name": "메인", "path": "/", "description": "Hero + 하이라이트", "priority": 1.0 },
    { "name": "소개", "path": "/about", "description": "협회소개 + 임원진", "priority": 0.8 }
  ],
  "wireframe": { "layout": "sidebar-none", "header": "fixed", "footer": "standard" }
}
```

### Phase 3: 디자인

**Input**: Phase 2 sitemap + reference_url
**Output**:
```json
{
  "design_tokens": {
    "colors": { "primary": "#0170B9", "secondary": "#FF6B9D", "accent": "#10B981", "bg": "#FFFFFF", "text": "#1F2937" },
    "fonts": { "heading": "Pretendard", "body": "Pretendard" },
    "spacing": { "section": "80px", "card": "24px" },
    "border_radius": "12px"
  },
  "tailwind_config": "// generated tailwind.config.ts ...",
  "globals_css": "// generated globals.css ..."
}
```

### Phase 4: 코드 생성

**Input**: design_tokens + sitemap + wireframe
**Output** (페이지당):
```json
{
  "files": [
    { "path": "app/page.tsx", "content": "// Next.js page code..." },
    { "path": "app/about/page.tsx", "content": "..." },
    { "path": "app/components/Nav.tsx", "content": "..." }
  ],
  "seo": [
    { "page": "/", "title": "...", "description": "...", "og_image": "..." }
  ]
}
```

### Phase 5: 백엔드

**Input**: sitemap + features
**Output**:
```json
{
  "notion_databases": [{ "name": "갤러리", "id": "created-db-id", "properties": {...} }],
  "api_routes": [
    { "path": "app/api/contact/route.ts", "content": "..." },
    { "path": "app/api/gallery/route.ts", "content": "..." }
  ],
  "env_template": "NOTION_TOKEN=\nNOTION_DATABASE_ID=\n"
}
```

### Phase 6: 배포

**Input**: 전체 files 배열
**Output**:
```json
{
  "github_commit": "abc1234",
  "vercel_url": "https://project-name.vercel.app",
  "deploy_status": "READY"
}
```

---

## 6. 페이지 템플릿 상세

### 템플릿 변수

Code 노드에서 사용하는 공통 변수:

```javascript
const vars = {
  siteName: "한국아트크래프트협회",     // 프로젝트명
  primaryColor: "#0170B9",              // design_tokens.colors.primary
  fontFamily: "Pretendard",             // design_tokens.fonts.heading
  sections: [...],                       // sitemap 기반 네비게이션
  notionDbId: "xxx",                    // CMS 연동용
  contactEmail: "info@kaca.or.kr"       // 문의폼 수신
};
```

### 템플릿 목록

| 타입 | 컴포넌트 구성 | 패키지 | 변수 |
|------|-------------|--------|------|
| `hero` | Hero 배너 + CTA + 하이라이트 카드 3개 + 후기 캐러셀 | Basic+ | siteName, primaryColor, heroImage |
| `about` | 소개 텍스트 + 임원진 그리드 (3/2) + ScrollReveal | Basic+ | members[], mission, vision |
| `programs` | 프로그램 카드 그리드 + 상세 토글 | Basic+ | programs[{name, desc, image}] |
| `contact` | 폼 (이름/이메일/전화/메시지) + FAQ 아코디언 + 지도 | Basic+ | contactEmail, faqs[] |
| `faq` | 카테고리별 아코디언 (가입/수강/전시/자격증) | Basic+ | categories[{name, items[]}] |
| `gallery` | Masonry 그리드 + Lightbox 모달 + 카테고리 필터 + 텍스트 검색 | Standard+ | notionDbId (갤러리 DB) |
| `notice` | 카테고리 탭 + 아코디언 + 페이지네이션 (10개/페이지) | Standard+ | notionDbId (공지 DB) |
| `events` | 카드 그리드 + 타임라인 뷰 | Standard+ | events[{title, date, image}] |
| `members` | NextAuth 로그인 폼 + 보호 라우트 + 회원 콘텐츠 | Premium | authProvider, protectedRoutes[] |
| `shop` | 상품 그리드 + 장바구니 + 토스페이먼츠 결제 | Premium | products[], tossClientKey |
| `admin` | 대시보드 + 통계 차트 + 데이터 테이블 CRUD | Premium | adminRoutes[], stats[] |

### 공통 컴포넌트 (자동 생성)

| 파일 | 내용 |
|------|------|
| `app/layout.tsx` | RootLayout (폰트, 메타데이터, Nav+Footer 포함) |
| `app/components/Nav.tsx` | 반응형 네비게이션 (모바일 햄버거, 데스크톱 가로) |
| `app/components/Footer.tsx` | 푸터 (연락처, SNS, 저작권) |
| `app/components/ScrollReveal.tsx` | 스크롤 애니메이션 래퍼 |
| `tailwind.config.ts` | 디자인 토큰 기반 Tailwind 설정 |
| `app/globals.css` | 전역 스타일 + 커스텀 유틸리티 |

---

## 7. 승인 게이트

WF 중간에 고객/대표님 확인이 필요한 단계. Notion DB 상태 변경으로 제어.

### 게이트 위치

| 게이트 | 위치 | Notion 상태 | 대기 방식 |
|--------|------|------------|----------|
| 견적 승인 | Phase 1 전 | "접수" → "진행" | Webhook 트리거 (자동) |
| 사이트맵 확인 | Phase 2 → 3 | "진행" → "시안확인" | **별도 Webhook 트리거** |
| 디자인 확인 | Phase 3 → 4 | "시안확인" → "개발" | **별도 Webhook 트리거** |
| 최종 검수 | Phase 6 → 7 | "개발" → "검수" → "완료" | **별도 Webhook 트리거** |

### 구현 방식

```
WF-Basic (Phase 1~2)
  → Phase 2 완료 시: Notion 상태 → "시안확인" + Discord 알림 ("사이트맵 확인해주세요")
  → WF 종료

Notion 자동화: 상태 "시안확인" → "개발" 변경 시
  → Webhook: hp-homepage-resume
  → WF-Basic-Phase3 (Phase 3~7) 실행
```

**WF를 단계별로 분리**:
- `WF-Basic-Research` (Phase 1~2): 리서치 + 기획 → 사이트맵 제출
- `WF-Basic-Build` (Phase 3~6): 디자인 + 코드 + 배포
- `WF-Basic-Complete` (Phase 7): 검수 후 완료 처리

각 WF는 Notion 상태 변경 Webhook으로 연결.

---

## 8. 에러 핸들링 및 재시도

### 에러 분류

| 에러 유형 | 예시 | 대응 |
|-----------|------|------|
| API 일시 오류 | Gemini 429, Notion 502 | 자동 재시도 (3회, 30초 간격) |
| 데이터 오류 | 필수 필드 누락, 잘못된 URL | Discord 알림 + 수동 확인 |
| 코드 생성 실패 | 템플릿 변수 누락 | Fallback 기본 템플릿 사용 |
| 배포 실패 | Vercel 빌드 에러 | Discord 알림 + 에러 로그 첨부 |

### n8n 에러 설정

```
모든 HTTP Request 노드:
  - onError: "continueRegularOutput"
  - retry: { count: 3, delay: 30000 }

모든 AI Agent 노드:
  - timeout: 60000 (60초)
  - onError: "continueRegularOutput" + fallback 응답

Webhook 응답:
  - 항상 200 반환 (비동기 처리)
  - 에러 시 Discord 알림으로 통보
```

### 에러 알림 형식

```
Discord 알림:
  ⚠️ [HP-WF] Phase 4 에러
  프로젝트: {project_name}
  노드: 메인페이지 템플릿
  에러: Template variable 'heroImage' is undefined
  상태: Fallback 템플릿으로 대체함
```

---

## 9. 기존 팀에이전트 단순화

### Before: 6개 에이전트 (전부 Sonnet)

| 에이전트 | 모델 | 작업 | 프롬프트 |
|----------|------|------|---------|
| PM | Sonnet | 디스패치, 품질검수, 보고 | pm_agent.md (상세) |
| Research | Sonnet | 사이트분석, 트렌드조사, 리포트 작성 | research_agent.md |
| Planning/UX | Sonnet | 사이트맵, 와이어프레임, UX흐름도 | planning_ux_agent.md |
| Design | Sonnet | 디자인시스템, HTML/Tailwind 시안 | design_agent.md |
| Frontend | Sonnet | Next.js 페이지/컴포넌트 코드 | frontend_agent.md |
| Backend | Sonnet | API Route, Notion CMS, 배포 | backend_agent.md |

### After: 1개 감독 에이전트 (Haiku) + n8n WF

| 역할 | 담당 | 모델 | 작업 |
|------|------|------|------|
| **WF 실행** | n8n | - | 전체 작업 (리서치→코드생성→배포) |
| **감독/검증** | Claude (Haiku) | Haiku | WF 결과 확인, 예외 처리, Discord 보고 |

### 감독 에이전트 역할 (최소한)

```
1. 의뢰 접수 감지 → WF 트리거 확인
2. 각 Phase 완료 알림 수신 → 결과 간단 검증
3. 승인 게이트 → 대표님에게 확인 요청 전달
4. 에러 발생 시 → 판단 후 재시도 or 대표님 보고
5. 최종 완료 → 고객 납품 보고
```

**토큰 사용량**: ~10K (기존 ~400K 대비 97% 절감)

### 프롬프트 단순화

기존 6개 프롬프트 파일 → 1개로 통합:

```markdown
# 홈페이지 제작 감독 에이전트 (Haiku)

## 역할
n8n WF가 실행하는 홈페이지 제작 작업을 감독합니다.

## 할 일
1. WF 실행 결과를 확인하고 문제가 있으면 보고
2. 승인 게이트에서 대표님에게 확인 요청
3. 에러 발생 시 재시도 판단
4. 완료 시 Discord 보고

## 하지 않을 일
- 코드 직접 작성 (WF Code 노드가 담당)
- 사이트 분석 (WF 딥리서치가 담당)
- 디자인 결정 (WF Gemini가 담당)
- Notion/Vercel API 직접 호출 (WF HTTP Request가 담당)
```

### 파일 변경 목록

| 파일 | 변경 |
|------|------|
| `homepage_orchestrator.py` | `orchestrate()` 단순화 — WF 트리거 + 결과 확인만 |
| `state_manager.py` | 삭제 또는 경량화 — Notion DB가 상태 관리 |
| `wf_client.py` | 단일 엔드포인트 (`hp-homepage-build`) |
| `prompts/*.md` (6개) | 1개로 통합 (`supervisor_agent.md`) |
| `package_checklist.json` | 유지 (WF 완료 시 자동 체크) |

---

## 10. 기존 도구 WF 연계

| 기존 WF | ID | 활용 |
|---------|-----|------|
| Tool - 딥리서치v2 | Tqb0NrVeIpZ7Ta5T | Phase 1 리서치 (HTTP Request → webhook/deep-research-v2) |
| Tool - 노션작업 | l5ZsWCtn5jZoQyNM | 고객DB/견적DB CRUD (webhook/ee4897b1-...) |
| HP - 통합 에이전트 도구 | SL7JvxXrditA68Fs | deploy, contact-form 등 개별 도구 (webhook/hp-agent-tool) |
| WIN Message Gate | X2tCCiNA2zCvUc6X | Discord 알림 (webhook/win-message-gate) |
| HP - 견적서 자동생성 | FWXDVdlYMrBH4hXH | 견적서 PDF 생성 (webhook/hp-estimate-trigger) |

### 신규 WF 목록

| WF | Webhook | 용도 |
|----|---------|------|
| HP - Basic 제작 (Phase 1~2) | hp-basic-research | 리서치 + 기획 |
| HP - Basic 제작 (Phase 3~6) | hp-basic-build | 디자인 + 코드 + 배포 |
| HP - Standard 제작 (Phase 1~2) | hp-standard-research | Basic + 갤러리/공지/이벤트 |
| HP - Standard 제작 (Phase 3~6) | hp-standard-build | Basic + 확장 기능 |
| HP - Premium 제작 (Phase 1~2) | hp-premium-research | Standard + 회원/결제/관리자 |
| HP - Premium 제작 (Phase 3~6) | hp-premium-build | Standard + 확장 기능 |
| HP - 완료 처리 | hp-complete | Notion 업데이트 + Discord 알림 |

---

## 11. 테스트 전략

### 단위 테스트 (WF 노드별)

| 대상 | 테스트 방법 | 합격 기준 |
|------|-----------|----------|
| 패키지 판별 Code | 다양한 pageCount/features 조합 입력 | 올바른 패키지 반환 |
| 페이지 템플릿 Code | 디자인 토큰 입력 → 코드 출력 | 유효한 TSX, import 정상 |
| Gemini 사이트맵 | 참고사이트 + 업종 입력 | JSON 포맷, 필수 페이지 포함 |
| Notion DB 생성 | DB 속성 입력 | 실제 DB 생성 확인 |
| Vercel 배포 | 테스트 코드 push | READY 상태 확인 |

### 통합 테스트

```
1. 테스트 의뢰 생성 (Notion 견적DB에 테스트 데이터)
2. 상태 → "접수" 변경
3. WF 자동 실행 확인
4. Phase 1~2 완료 → 사이트맵 출력 확인
5. 상태 → "개발" 변경
6. Phase 3~6 완료 → Vercel 배포 URL 확인
7. 상태 → "완료" + 고객리스트 업데이트 확인
8. 테스트 데이터 정리 (archive)
```

### 검증 체크리스트

- [ ] 생성된 코드가 `next build` 통과하는지
- [ ] 반응형 (모바일/태블릿/데스크톱) 정상
- [ ] SEO 메타태그 정상
- [ ] Notion CMS 데이터 표시 정상
- [ ] 문의폼 전송 정상
- [ ] 배포 URL 접속 정상

---

## 12. 마이그레이션 경로

### 단계별 전환

```
[현재] Python 오케스트레이터 + Claude 6개 에이전트
  ↓
[Phase A] WF-Basic 구축 + 테스트 (신규 의뢰만)
  ↓
[Phase B] WF-Standard/Premium 구축
  ↓
[Phase C] 기존 오케스트레이터 → 감독 에이전트로 단순화
  ↓
[Phase D] 기존 프롬프트 6개 → supervisor_agent.md 1개로 통합
  ↓
[최종] n8n WF 메인 + Claude 감독(Haiku) 보조
```

### 병행 운영 기간

- Phase A~B 동안: 기존 시스템과 WF를 병행
- 신규 의뢰 → WF로 처리
- 기존 진행중 의뢰 (KACA 등) → 기존 시스템으로 완료
- WF 안정화 확인 후 기존 시스템 비활성화

### 보존 파일

| 파일 | 처리 |
|------|------|
| `homepage_orchestrator.py` | 경량화 (WF 트리거만) |
| `state_manager.py` | 아카이브 (Notion DB로 대체) |
| `wf_client.py` | 경량화 (단일 엔드포인트) |
| `prompts/*.md` (6개) | 아카이브 + `supervisor_agent.md` 신규 |
| `package_checklist.json` | 유지 |

---

## 13. 구현 순서

### Phase 1: WF-Basic 구축 (최우선)

- [ ] Webhook 트리거 (`hp-homepage-build`)
- [ ] 패키지 판별 Code 노드
- [ ] 리서치 병렬 (딥리서치v2 × 2 + Merge)
- [ ] AI Agent (Gemini) 사이트맵 생성
- [ ] 디자인 토큰 추출 (Gemini)
- [ ] Code 노드 페이지 템플릿 5개 (hero/about/programs/contact/faq)
- [ ] 공통 컴포넌트 (layout/Nav/Footer/ScrollReveal)
- [ ] Notion CMS DB 생성 + API Route
- [ ] GitHub push + Vercel 배포
- [ ] Notion 상태 업데이트 + Discord 알림
- [ ] 에러 핸들링 + 재시도 설정

### Phase 2: WF-Standard 확장

- [ ] Basic WF 복제
- [ ] 갤러리/공지/이벤트 페이지 템플릿 추가
- [ ] 검색/필터 + Band 동기화 + 애니메이션 추가

### Phase 3: WF-Premium 확장

- [ ] Standard WF 복제
- [ ] 회원/결제/관리자 페이지 템플릿 추가
- [ ] NextAuth + 토스페이먼츠 + i18n 추가

### Phase 4: 팀에이전트 단순화

- [ ] `supervisor_agent.md` 프롬프트 작성
- [ ] `homepage_orchestrator.py` WF 트리거 전용으로 경량화
- [ ] `wf_client.py` 단일 엔드포인트 업데이트
- [ ] 기존 6개 프롬프트 아카이브

### Phase 5: 승인 게이트 + 자동화

- [ ] Notion 자동화 → Webhook 연결 (상태별)
- [ ] 승인 게이트 WF 분리 (Research / Build / Complete)
- [ ] 고객리스트 자동 업데이트
- [ ] 통합 테스트

---

## 14. Before vs After 비교

| 항목 | Before (Claude 에이전트) | After (n8n WF) |
|------|------------------------|----------------|
| AI 모델 | Sonnet × 6 에이전트 | Gemini Flash + Perplexity |
| Claude 토큰 | ~400K/프로젝트 | **~10K (감독만)** |
| 비용 | 높음 (Claude API) | **낮음 (Gemini 무료 + Perplexity 저가)** |
| 실행 방식 | 순차 (에이전트 간 대기) | **병렬 (Switch+Merge)** |
| 오케스트레이터 | Claude PM 에이전트 | **n8n WF** |
| 코드 생성 | Claude가 직접 작성 | **Code 노드 템플릿** |
| 상태 관리 | state_manager.py (JSON) | **Notion DB (상태 속성)** |
| 승인 게이트 | Python 코드 내 분기 | **Notion 상태 → Webhook** |
| 에러 처리 | 에이전트 재시도 (토큰 소비) | **n8n 자동 재시도 (토큰 0)** |
| 에이전트 수 | 6개 (Sonnet) | **1개 감독 (Haiku)** |
| 프롬프트 | 6개 파일 (총 ~2000줄) | **1개 파일 (~30줄)** |
