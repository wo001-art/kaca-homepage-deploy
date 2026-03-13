# KACA 홈페이지 프로젝트

## 기본 정보
- **고객**: 한국아트크래프트협회 (KACA)
- **프로젝트**: KACA 홈페이지 제작
- **필요기능**: 갤러리, 문의폼, SEO, 관리자CMS
- **예산**: 150~300만원
- **가견적**: 2,700,000원
- **노션 견적 페이지ID**: 318765eb-4694-81ff-af75-c8604d61e0ab
- **노션 기획안 페이지ID**: 312765eb-4694-81c9-abe6-c9fca885b43e
- **견적 DB ID**: 3ddbf37e258c49418bf03698bc1d928a

## 패키지 구성
| 패키지 | 가격 | 페이지 | 주요 기능 |
|--------|------|--------|----------|
| Basic | 80~100만 | 5p | 심플 소개, Notion CMS, 반응형 |
| **Standard** | **120~150만** | **7p + 갤러리/공지** | **디자인 퀄리티 업, 검색/필터, n8n Band 동기화** |
| Premium | 200~250만 | 10p+ | 풀커스텀, 회원로그인, 결제, 다국어, SEO |

## 노션 기획안 섹션 구조 (페이지ID: 312765eb)
1. **협회 소개** - 비전/핵심가치, 420+회원, 2022년 창립
2. **전시회 & 갤러리** - 봄/가을 정기전시, 작품 갤러리
3. **교육 프로그램** - 기초/심화/원데이클래스/자격증(7개 과정)
4. **제품 & 작품** - 퓨어리움, 크리스탈레진
5. **FAQ** - 가입/수강/전시/자격증/원데이클래스
6. **문의하기** - 연락처/SNS

## Standard(120만) 패키지 진행 현황 (12/15, 80%)
| 항목 | 상태 | 비고 |
|------|------|------|
| 메인 | ✅ | Hero+하이라이트+후기+CTA |
| 협회소개 (/about) | ✅ | 소개+임원진(3/2)+ScrollReveal |
| 교육과정 (/programs) | ✅ | 5개 프로그램+ScrollReveal |
| 전시/이벤트 (/events) | ✅ | 활동4+전시이력6+ScrollReveal |
| 문의 (/contact) | ✅ | 폼UI+FAQ+API연동 |
| 갤러리 (/gallery) | ✅ | masonry그리드+모달+카테고리필터+텍스트검색 |
| 공지사항 (/notice) | ✅ | 카테고리탭+아코디언+페이지네이션 |
| 문의폼 전송 | ✅ | /api/contact → n8n webhook 연동 |
| 검색/필터 | ✅ | 갤러리 텍스트검색+하이라이트 |
| 애니메이션 | ✅ | ScrollReveal (7페이지 적용) |
| 반응형 | ✅ | 모바일/태블릿/데스크톱 |
| SEO | ✅ | 전 페이지 metadata+openGraph |
| **Notion CMS** | **준비만** | 대표님 지시: 연동 준비만 |
| **Band 동기화** | **대기** | 대표님 지시: 대기 |
| **Vercel 배포** | **대기** | 최종 확인 후 배포 |

## 로그인 추가 옵션 (고객 문의) — v3 최신
- **방식**: 자격증 발급 시 Notion에서 계정 자동 생성 (핸드폰번호=아이디)
- **비번 초기화**: 자격증번호 입력 → 리셋
- **일반인 가입 불가** (관리자만 계정 생성)
- **유료 항목**: Notion 회원DB + 인증API(15만) + 로그인 페이지(5만) = +20만원
- **서비스 제공(무료)**: 비밀번호 초기화, 회원전용 라우트, 게시판/전용 페이지, 기존 페이지 권한
- **총합**: Standard(120만) + 로그인(20만) = **140만원 (VAT별도)**
- **Notion 요구사항**: Notion Pro 플랜 ($10/월, 약 1.3만원) 권장
- **견적 이미지**: claude_tmp/login_pricing_v3-*.png (최신)

## Vercel 배포 URL (절대 혼동 금지)
| URL | 용도 | Vercel 프로젝트 | ⚠️ 주의사항 |
|-----|------|----------------|------------|
| **kaca-proposal.vercel.app** | **제안서 페이지** (Next.js + Notion CMS) | kaca-proposal | **절대 덮어쓰기 금지! 제안서 전용** |
| **kaca-homepage-deploy.vercel.app** | **홈페이지** (최신, 작업중) | kaca-homepage-deploy | 홈페이지 전용 |
| kaca-homepage.vercel.app | ⚠️ 구버전 (사용X, 덮어씌워짐) | kaca-homepage | 사용 금지 |
| kaca-deploy.vercel.app | ⚠️ 구버전 (사용X) | kaca-deploy | 사용 금지 |
| wo001-art.github.io/kaca-homepage/ | 5p Basic 샘플 | GitHub Pages | - |

## 제안서 페이지 상세 (kaca-proposal) — 절대 덮어쓰기 금지
- **URL**: https://kaca-proposal.vercel.app
- **기술**: Next.js 14 + Notion API (ISR 60초)
- **Git 원본**: kaca-homepage 레포 commit `004832d`
- **Notion 페이지 ID**: `312765eb-4694-81d9-9baa-f39099d7a0df` (고객 공유용 제안서)
- **Notion 페이지 제목**: "한국아트크래프트협회 홈페이지 제작 제안서"
- **Vercel 환경변수**: NOTION_TOKEN + NOTION_PAGE_ID (312765eb469481d99baaf39099d7a0df)
- **섹션**: 프로젝트 개요 / 기술 구성 / 홈페이지 구성(7p) / 참고 사이트 분석 / 패키지 안내(3티어) / 월 유지보수 / 진행 프로세스 / 준비사항 / 문의
- **사고 이력**: 2026-03-11 잘못된 Notion 페이지 ID(318765eb=견적DB)로 배포 → 다른 내용 표시 → 올바른 ID(312765eb-81d9)로 복구 완료

## 오케스트레이터 프로젝트
- **slug**: kaca-2026
- **경로**: homepage-projects/kaca-2026/project_state.json

## 참고 사이트 (필수 참조)
- **URL**: https://hawaiifluidart.com/
- **특징**: 플루이드 아트 전문 스튜디오 홈페이지
- **구조 (이 구성을 따라야 함)**:
  1. **Header/Nav**: 고정, 로고 좌측, 메뉴(Classes, About, Events), CTA 버튼
  2. **Hero**: 풀와이드 배너, 환영 메시지 + CTA
  3. **Featured Classes Grid**: 5열 카드 캐러셀 (클래스별 이미지+제목)
  4. **Event/Experience Cards**: 4열 그리드 (Girls Night, Birthday, Corporate, Date Night)
  5. **Testimonials**: 캐러셀/슬라이더 (후기)
  6. **Signature Experiences**: 프로그램 상세 설명 리스트
  7. **Extended Activities**: 추가 활동 리스트
  8. **Cultural Welcome**: 브랜딩/환영 섹션
  9. **Target Audience**: 아이콘 + 텍스트 리스트
  10. **Footer**
- **디자인**: glassmorphism 헤더, 캐러셀, 반응형, 깔끔한 카드 UI
- **컬러**: 메인 블루(#0170B9), 핑크/마젠타 포인트, 화이트 배경

## KACA 적용 매핑
| Hawaii Fluid Art | KACA 적용 |
|-----------------|-----------|
| Classes | 교육/자격증 과정 (레진우드, 크리스탈 플라워 등) |
| About/History | 협회 소개, 임원진 |
| Events | 전시 이력 (고양아트페어, 자연순환전 등) |
| Find a Studio | 가입 문의 |
| Testimonials | 회원 후기 / 작품 갤러리 |
| Signature Experiences | 주요 활동 상세 (전시, 교육, 원데이클래스, 회원교류) |

## 임원진 (3/2 배치, 가운데 정렬)
| 이름 | 직책 | 지역 |
|------|------|------|
| 손종탁 | 협회장 | 울산 |
| 이지연 | 부회장 | 파주 헤이리 |
| 김영숙 | 문화홍보이사 | 남양주 |
| 한기홍 | 제품개발기획이사 | - |
| 이소영 | 교육이사 | 안산/화성 |

## 배포
- **Vercel**: https://kaca-homepage-deploy.vercel.app
- **레포**: kaca-homepage-deploy (clean, no secrets)
- **소스**: C:\Users\Administrator\Documents\ClaudeCodeHub\kaca-homepage

## n8n WF (홈페이지 관련)
| WF ID | 이름 | 상태 | 용도 |
|-------|------|------|------|
| FWXDVdlYMrBH4hXH | HP - 견적서 자동생성 [Auto] | ON | 견적서 자동생성 (Webhook 트리거, Notion 상태변경→접수 시 실행) |
| SL7JvxXrditA68Fs | HP - 홈페이지 에이전트 도구 [Webhook] | ON | 통합 에이전트 도구 (6개 브랜치 Switch) |

### 통합 에이전트 도구 WF (SL7JvxXrditA68Fs)
- **Webhook**: `https://n8n.wookvan.com/webhook/hp-agent-tool`
- **호출**: `POST {action, data}` → Switch 노드로 분기
- **브랜치 상태** (2026-03-13):

| action | 기능 | 상태 | 구현 |
|--------|------|------|------|
| site-analyze | 경쟁사/참고사이트 분석 | ✅ | 딥리서치v2 WF 호출 (Perplexity sonar-pro) |
| trend-crawl | 트렌드 분석 | ✅ | 딥리서치v2 WF 호출 (Perplexity sonar-pro) |
| contact-form | 문의폼 Notion 접수 | ✅ | Notion API 직접호출 (견적DB) |
| deploy | Vercel 배포 | ✅ | Vercel API |
| lighthouse | 성능 측정 | ⏸ 보류 | PageSpeed API (미활성화) |
| screenshot | 사이트 캡처 | ⏸ 보류 | placeholder |

### 견적서 WF 변경 이력 (2026-03-13)
- Schedule 트리거(1분 간격) → Webhook 트리거로 변경
- Webhook: `https://n8n.wookvan.com/webhook/hp-estimate-trigger`
- Notion DB 자동화에서 상태→접수 변경 시 webhook 호출하도록 설정 필요

## 기술 스택
- Next.js 14.2.21 + React 18.3.1 + TypeScript
- 이미지: Imagen 3 API 생성
