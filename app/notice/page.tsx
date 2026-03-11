'use client'

import { useState } from 'react'
import Nav from '../components/Nav'
import Footer from '../components/Footer'
import ScrollReveal from '../components/ScrollReveal'

type FilterTab = '전체' | '공지' | '소식' | '교육'

interface Notice {
  id: number
  category: '공지' | '소식' | '교육'
  title: string
  date: string
  important: boolean
  content: string
}

const ITEMS_PER_PAGE = 5

export default function NoticePage() {
  const [activeTab, setActiveTab] = useState<FilterTab>('전체')
  const [openId, setOpenId] = useState<number | null>(null)
  const [currentPage, setCurrentPage] = useState(1)

  const notices: Notice[] = [
    {
      id: 1, category: '공지', title: '2026년 상반기 정기 회원전 참가 안내', date: '2026-03-05', important: true,
      content: '2026년 상반기 정기 회원전 참가 신청을 받습니다. 참가를 희망하시는 회원님께서는 2026년 3월 31일까지 협회 카카오톡 채널 또는 이메일로 신청해주시기 바랍니다. 출품 작품은 최대 2점이며, 작품 규격은 50호 이하입니다.'
    },
    {
      id: 2, category: '공지', title: '제7회 마블 플루이드 아트 자격증 시험 일정', date: '2026-02-28', important: true,
      content: '제7회 마블 플루이드 아트 자격증 시험이 2026년 4월 중 진행될 예정입니다. 응시 자격은 협회 정회원이며, 베이직 및 마스터 과정 이수자에 한합니다. 세부 일정 및 접수 방법은 추후 공지 예정입니다.'
    },
    {
      id: 3, category: '소식', title: '고양국제아트페어 2026 참가 확정', date: '2026-02-20', important: false,
      content: '한국 아트크래프트 협회가 고양국제아트페어 2026에 참가 확정되었습니다. 전시 기간은 2026년 10월로 예정되어 있으며, 참가 회원 모집은 별도 공지를 통해 안내드릴 예정입니다.'
    },
    {
      id: 4, category: '교육', title: '크리스탈 플라워 마스터 과정 3기 모집', date: '2026-02-15', important: false,
      content: '크리스탈 플라워 마스터 과정 3기 수강생을 모집합니다. 교육 기간은 2026년 3월~5월(총 12주)이며, 전국 협회 공방에서 진행됩니다. 수강료 및 신청 방법은 문의하기 페이지를 통해 확인해주세요.'
    },
    {
      id: 5, category: '소식', title: '협회 창립 4주년 기념 온라인 전시 오픈', date: '2026-02-10', important: false,
      content: '한국 아트크래프트 협회 창립 4주년을 기념하여 온라인 전시를 오픈합니다. 전국 420여 명 회원의 작품 200여 점을 온라인에서 감상하실 수 있습니다. 온라인 전시 링크는 협회 밴드 및 SNS를 통해 공유됩니다.'
    },
    {
      id: 6, category: '공지', title: '2026년 연회비 납부 안내', date: '2026-01-15', important: false,
      content: '2026년 연회비 납부 기간을 안내드립니다. 납부 기간: 2026년 1월 15일 ~ 2월 28일. 납부 금액: 정회원 연 30,000원. 납부 방법: 협회 지정 계좌로 이체 후 영수증 제출.'
    },
    {
      id: 7, category: '교육', title: '레진우드 베이직 과정 신규 개설 (대전)', date: '2026-01-10', important: false,
      content: '대전 지역에 레진우드 베이직 과정이 새롭게 개설됩니다. 총 8주 과정으로, 레진아트의 기초부터 실전 작품 제작까지 배울 수 있습니다. 선착순 10명 모집이므로 빠른 신청 바랍니다.'
    },
    {
      id: 8, category: '소식', title: '2025년 활동 결산 보고서', date: '2025-12-30', important: false,
      content: '2025년 협회 활동 결산 보고서를 공유합니다. 올 한 해 전시 6회, 워크숍 12회, 원데이클래스 200여 회를 성공적으로 진행하였습니다. 새해에도 더욱 활발한 활동으로 보답하겠습니다.'
    },
    {
      id: 9, category: '공지', title: '겨울 워크숍 참가 신청 안내', date: '2025-12-15', important: false,
      content: '2025년 겨울 워크숍 참가 신청을 받습니다. 일시: 2025년 12월 28일(토). 장소: 서울 인사동 협회 전시장. 프로그램: 플루이드아트 콜렉팅 기법 + 신년 인테리어 소품 만들기. 참가비: 회원 무료, 비회원 30,000원.'
    },
    {
      id: 10, category: '소식', title: '울산 장생포 전시 성황리에 마무리', date: '2025-11-20', important: false,
      content: '지난 11월 10일~15일 울산 장생포 문화창고에서 진행된 협회 회원전이 성황리에 마무리되었습니다. 약 1,200여 명의 관람객이 방문하였으며, 회원들의 창작 열정을 보여준 훌륭한 전시였습니다.'
    },
  ]

  const filterTabs: FilterTab[] = ['전체', '공지', '소식', '교육']

  const getTabCount = (tab: FilterTab) =>
    tab === '전체' ? notices.length : notices.filter(n => n.category === tab).length

  const filtered = activeTab === '전체' ? notices : notices.filter(n => n.category === activeTab)

  // 중요 공지 상단 고정
  const sorted = [...filtered].sort((a, b) => {
    if (a.important && !b.important) return -1
    if (!a.important && b.important) return 1
    return 0
  })

  const totalPages = Math.ceil(sorted.length / ITEMS_PER_PAGE)
  const paginated = sorted.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE)

  const formatDate = (dateStr: string) => {
    const [year, month, day] = dateStr.split('-')
    const now = new Date()
    const date = new Date(dateStr)
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays === 0) return '오늘'
    if (diffDays <= 7) return `${diffDays}일 전`
    return `${year}.${month}.${day}`
  }

  const getCategoryClass = (cat: string) => {
    switch (cat) {
      case '공지': return 'notice-cat-announcement'
      case '소식': return 'notice-cat-news'
      case '교육': return 'notice-cat-education'
      default: return ''
    }
  }

  const handleTabChange = (tab: FilterTab) => {
    setActiveTab(tab)
    setCurrentPage(1)
    setOpenId(null)
  }

  return (
    <>
      <Nav />
      <section className="page-hero">
        <h1>공지사항</h1>
        <p>협회의 소식과 공지를 확인하세요</p>
      </section>

      <ScrollReveal>
      <section className="section">
        <div className="section-inner">
          {/* Filter Tabs */}
          <div className="notice-tabs">
            {filterTabs.map((tab) => (
              <button
                key={tab}
                className={`notice-tab ${activeTab === tab ? 'notice-tab-active' : ''}`}
                onClick={() => handleTabChange(tab)}
              >
                {tab}
                <span className="notice-tab-count">{getTabCount(tab)}</span>
              </button>
            ))}
          </div>

          {/* Notice List */}
          <div className="notice-list-v2">
            {paginated.map((n) => (
              <div key={n.id} className={`notice-item-v2 ${n.important ? 'notice-pinned-v2' : ''} ${openId === n.id ? 'notice-open' : ''}`}>
                <button
                  className="notice-row"
                  onClick={() => setOpenId(openId === n.id ? null : n.id)}
                >
                  <div className="notice-row-left">
                    {n.important && (
                      <span className="notice-pin-badge">중요</span>
                    )}
                    <span className={`notice-category ${getCategoryClass(n.category)}`}>{n.category}</span>
                    <span className="notice-title-v2">{n.title}</span>
                  </div>
                  <div className="notice-row-right">
                    <span className="notice-date-v2">{formatDate(n.date)}</span>
                    <span className="notice-chevron">{openId === n.id ? '▲' : '▼'}</span>
                  </div>
                </button>
                <div className="notice-accordion">
                  <div className="notice-accordion-inner">
                    <p className="notice-content">{n.content}</p>
                    <div className="notice-content-meta">
                      <span>작성일: {n.date.replace(/-/g, '.')}</span>
                      {n.important && <span className="notice-important-label">중요 공지</span>}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filtered.length === 0 && (
            <div className="gallery-empty">
              <p>해당 카테고리의 공지가 없습니다.</p>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="notice-pagination">
              <button
                className="page-btn page-prev"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage(p => p - 1)}
              >
                ‹
              </button>
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <button
                  key={page}
                  className={`page-btn ${currentPage === page ? 'page-btn-active' : ''}`}
                  onClick={() => setCurrentPage(page)}
                >
                  {page}
                </button>
              ))}
              <button
                className="page-btn page-next"
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage(p => p + 1)}
              >
                ›
              </button>
            </div>
          )}
        </div>
      </section>
      </ScrollReveal>

      <section className="section-cta">
        <div className="cta-inner">
          <h2>최신 소식을 놓치지 마세요</h2>
          <p>협회 밴드에서 더 많은 소식을 확인하실 수 있습니다</p>
          <a href="/contact" className="btn-cta-white">문의하기</a>
        </div>
      </section>

      <Footer />
    </>
  )
}
