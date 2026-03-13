# 홈페이지 제작 팀에이전트 → n8n WF 전환 계획

> 목표: n8n WF가 메인 오케스트레이터, AI Agent/Code 노드로 작업 수행. Claude 토큰 사용 → 거의 0
> 작성일: 2026-03-13 (v2 전면 수정)

---

## 1. 핵심 아이디어

**Before**: Claude 에이전트 6개 (PM/Research/Planning/Design/Frontend/Backend) → 각각 Sonnet, 토큰 대량 소비
**After**: 패키지별 n8n WF 1개가 전체 작업 수행 → AI Agent 노드(Gemini/Perplexity) + Code 노드 + Switch/Merge 병렬처리

```
고객 의뢰 (Notion 상태변경)
  → n8n Webhook 트리거
    → 패키지별 WF 자동 실행
      → AI Agent 노드 + Code 노드가 작업
        → 결과물 Notion/Vercel/GitHub에 자동 업로드
          → 완료 알림 Discord
```

**Claude 토큰 = 거의 0** (Gemini 2.0 Flash + Perplexity sonar-pro가 AI 작업 담당)

---

## 2. Notion DB 링크

| DB | ID | 용도 |
|----|-----|------|
| 홈페이지견적 | `3ddbf37e-258c-4941-8bf0-3698bc1d928a` | 견적/의뢰 접수 (상태: 접수→진행→완료) |
| 고객리스트 | `181d1c32-1694-80a7-8b50-c4b9ad2fbbfc` | 고객 정보 관리 (연락처, 이력) |
| 작업로그 | Notion 작업로그 DB | 작업 진행 로그 |
| 기획안 페이지 | `312765eb-4694-81c9-abe6-c9fca885b43e` | 기획안/제안서 |

---

## 3. 패키지별 WF 구조

### 3-1. WF-Basic (5페이지, 80~100만)

```
[Webhook 트리거] 의뢰 접수
  │
  ├─ [Phase 1: 리서치] ──────────────────── 병렬 실행
  │   ├─ HTTP Request → 딥리서치v2 (사이트 분석)
  │   ├─ HTTP Request → 딥리서치v2 (트렌드 조사)
  │   └─ Merge (리서치 결과 합산)
  │
  ├─ [Phase 2: 기획] ────────────────────── 순차 실행
  │   ├─ AI Agent (Gemini) → 사이트맵 생성 (5p: 메인/소개/서비스/문의/FAQ)
  │   └─ Code 노드 → 와이어프레임 JSON 생성
  │
  ├─ [Phase 3: 디자인] ──────────────────── 순차 실행
  │   ├─ AI Agent (Gemini) → 디자인 토큰 추출 (참고사이트 기반)
  │   └─ Code 노드 → Tailwind 설정 + globals.css 생성
  │
  ├─ [Phase 4: 코드 생성] ───────────────── 병렬 실행 (핵심)
  │   ├─ Code 노드 → 메인페이지 템플릿
  │   ├─ Code 노드 → 소개페이지 템플릿
  │   ├─ Code 노드 → 서비스페이지 템플릿
  │   ├─ Code 노드 → 문의페이지 템플릿
  │   ├─ Code 노드 → FAQ페이지 템플릿
  │   ├─ AI Agent (Gemini) → SEO 메타데이터 × 5p
  │   └─ Merge (전체 코드 합산)
  │
  ├─ [Phase 5: 백엔드] ──────────────────── 병렬 실행
  │   ├─ HTTP Request → Notion CMS DB 생성 (notion-api WF)
  │   ├─ Code 노드 → API Route 코드 생성
  │   └─ Code 노드 → 문의폼 API 연동 코드
  │
  ├─ [Phase 6: 배포]
  │   ├─ HTTP Request → GitHub 커밋 (push_files)
  │   └─ HTTP Request → Vercel 배포 트리거
  │
  └─ [Phase 7: 완료 처리]
      ├─ HTTP Request → Notion 견적DB 상태 → '완료'
      ├─ HTTP Request → Notion 고객리스트 업데이트
      └─ HTTP Request → Discord 완료 알림
```

### 3-2. WF-Standard (7페이지, 120~150만) — Basic 확장

```
Basic 전체 포함 +

[Phase 4 추가 병렬]:
  ├─ Code 노드 → 갤러리 페이지 (Masonry 그리드 + 모달 + 필터)
  ├─ Code 노드 → 공지사항 페이지 (카테고리탭 + 페이지네이션)
  ├─ Code 노드 → 전시/이벤트 페이지 (카드 그리드)
  └─ AI Agent (Gemini) → SEO 메타데이터 × 2p 추가

[Phase 5 추가]:
  ├─ Code 노드 → 검색/필터 컴포넌트 코드
  ├─ Code 노드 → Band 동기화 API Route
  └─ AI Agent (Gemini) → 인터랙션 애니메이션 코드
```

### 3-3. WF-Premium (10페이지, 200~250만) — Standard 확장

```
Standard 전체 포함 +

[Phase 4 추가 병렬]:
  ├─ Code 노드 → 회원전용 페이지 (로그인 + 보호 라우트)
  ├─ Code 노드 → 제품/결제 페이지 (상품 그리드 + 결제)
  ├─ Code 노드 → 관리자 대시보드 (레이아웃 + 통계)
  └─ AI Agent (Gemini) → SEO 메타데이터 × 3p 추가

[Phase 5 추가]:
  ├─ Code 노드 → NextAuth 인증 시스템
  ├─ Code 노드 → 결제 연동 (토스페이먼츠)
  ├─ Code 노드 → 다국어 i18n 설정
  └─ AI Agent (Gemini) → 고급 SEO (구조화 데이터, canonical)
```

---

## 4. 노드별 AI 모델 배정

| 노드 타입 | AI 모델 | 용도 | 토큰 비용 |
|-----------|---------|------|----------|
| AI Agent (리서치) | Perplexity sonar-pro | 사이트분석, 트렌드 | Perplexity 요금 |
| AI Agent (생성) | Gemini 2.0 Flash | 사이트맵, SEO, 디자인토큰 | 무료~저렴 |
| AI Agent (코드검증) | Gemini 2.0 Flash | 생성 코드 검증 | 무료~저렴 |
| Code 노드 | 없음 (JS 실행) | 페이지 템플릿, API Route | 0원 |
| HTTP Request | 없음 | Notion/Vercel/GitHub API | 0원 |

**Claude 토큰 = 0** (모든 AI 작업은 Gemini/Perplexity)

---

## 5. Switch + Merge 병렬 구조

```
                    ┌─ 사이트 분석 (딥리서치) ─┐
Switch (리서치) ────┤                          ├── Merge → Phase 2
                    └─ 트렌드 조사 (딥리서치) ─┘

                    ┌─ 메인페이지 (Code) ──────┐
                    ├─ 소개페이지 (Code) ──────┤
Switch (코드생성) ──┤─ 서비스페이지 (Code) ────┤── Merge → Phase 5
                    ├─ 문의페이지 (Code) ──────┤
                    └─ FAQ페이지 (Code) ───────┘

                    ┌─ Notion CMS 설정 ────────┐
Switch (백엔드) ────┤─ API Route 생성 ─────────┤── Merge → Phase 6
                    └─ 문의폼 연동 ────────────┘
```

**효과**: 병렬 실행으로 전체 소요 시간 단축

---

## 6. Notion 연동 상세

### 의뢰 접수 → WF 자동 트리거

```
Notion 홈페이지견적 DB (3ddbf37e...)
  └─ 상태: "접수" 변경
      └─ Notion 자동화 → Webhook: hp-estimate-trigger
          └─ 패키지 판별 (페이지수/기능 기준)
              ├─ Basic → WF-Basic 실행
              ├─ Standard → WF-Standard 실행
              └─ Premium → WF-Premium 실행
```

### 완료 시 자동 업데이트

| 대상 | 작업 | API |
|------|------|-----|
| 홈페이지견적 DB | 상태 → '완료', 견적서URL 입력 | Notion API |
| 고객리스트 DB | 신규→생성 / 기존→토글 append | Notion API (notion-api WF) |
| 기획안 페이지 | 제작 결과 요약 추가 | Notion API |

---

## 7. 페이지 템플릿 목록 (Code 노드용)

| 타입 | 기본 구성 | 해당 패키지 |
|------|----------|-----------|
| `hero` | Hero 배너 + CTA + 하이라이트 | Basic+ |
| `about` | 소개 텍스트 + 임원진 그리드 + ScrollReveal | Basic+ |
| `programs` | 프로그램 카드 + 상세 토글 | Basic+ |
| `contact` | 폼 UI + FAQ 아코디언 + API 연동 | Basic+ |
| `faq` | 카테고리별 아코디언 | Basic+ |
| `gallery` | Masonry 그리드 + 모달 + 카테고리 필터 + 검색 | Standard+ |
| `notice` | 카테고리탭 + 아코디언 + 페이지네이션 | Standard+ |
| `events` | 카드 그리드 + 타임라인 | Standard+ |
| `members` | 로그인 폼 + 보호 라우트 + 회원 콘텐츠 | Premium |
| `shop` | 상품 그리드 + 장바구니 + 결제 | Premium |
| `admin` | 대시보드 + 통계 차트 + CRUD | Premium |

각 템플릿 = Next.js 14 App Router + TypeScript + Tailwind CSS

---

## 8. 기존 도구 WF와의 관계

| 기존 WF | 활용 방식 |
|---------|----------|
| Tool - 딥리서치v2 (Tqb0NrVeIpZ7Ta5T) | 리서치 단계에서 HTTP Request로 호출 |
| Tool - 노션작업 (l5ZsWCtn5jZoQyNM) | 고객DB/견적DB CRUD |
| HP - 통합 에이전트 도구 (SL7JvxXrditA68Fs) | 개별 도구 호출용 (deploy, contact-form 등) |
| WIN Message Gate (X2tCCiNA2zCvUc6X) | Discord 알림 |

---

## 9. 구현 순서

### Phase 1: WF-Basic 구축 (최우선)
- [ ] Webhook 트리거 + 패키지 판별 Switch
- [ ] 리서치 병렬 (딥리서치v2 × 2 + Merge)
- [ ] AI Agent (Gemini) 사이트맵 생성
- [ ] Code 노드 페이지 템플릿 5개
- [ ] Notion CMS + API Route 자동 생성
- [ ] Vercel 배포 + Notion 상태 업데이트
- [ ] Discord 완료 알림

### Phase 2: WF-Standard 확장
- [ ] Basic WF 복제 + 갤러리/공지/이벤트 추가
- [ ] 검색/필터 + Band 동기화 + 애니메이션

### Phase 3: WF-Premium 확장
- [ ] Standard WF 복제 + 회원/결제/관리자 추가
- [ ] NextAuth + 토스페이먼츠 + i18n

### Phase 4: 자동화 완성
- [ ] Notion 자동화 → Webhook 연결
- [ ] 고객리스트 자동 업데이트
- [ ] 에러 핸들링 + 재시도 로직

---

## 10. Before vs After 비교

| 항목 | Before (Claude 에이전트) | After (n8n WF) |
|------|------------------------|----------------|
| AI 모델 | Sonnet × 6 에이전트 | Gemini Flash + Perplexity |
| Claude 토큰 | ~400K/프로젝트 | **~0** |
| 실행 시간 | 순차 (에이전트 간 대기) | **병렬 (Switch+Merge)** |
| 비용 | 높음 (Claude API) | **낮음 (Gemini 무료 + Perplexity 저가)** |
| 오케스트레이터 | Claude PM 에이전트 | **n8n WF** |
| 코드 생성 | Claude가 직접 작성 | **Code 노드 템플릿** |
| DB 연동 | Python wf_client.py | **n8n HTTP Request 직접** |
| 배포 | Claude가 WF 호출 | **n8n이 직접 Vercel API** |
| 상태 관리 | state_manager.py (JSON) | **Notion DB (상태 속성)** |
