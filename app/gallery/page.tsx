'use client'

import { useState, useMemo } from 'react'
import Nav from '../components/Nav'
import Footer from '../components/Footer'
import ScrollReveal from '../components/ScrollReveal'

type Category = '전체' | '플루이드아트' | '레진우드' | '크리스탈플라워' | '혼합매체'

interface Work {
  title: string
  artist: string
  category: Category
  year: string
  desc: string
  size: 'normal' | 'tall' | 'wide'
}

const categoryGradients: Record<string, string> = {
  '플루이드아트': 'linear-gradient(135deg, #1a1a6e 0%, #0170B9 40%, #00BFA6 100%)',
  '레진우드': 'linear-gradient(135deg, #3D2B1F 0%, #8B5E3C 50%, #C8A97A 100%)',
  '크리스탈플라워': 'linear-gradient(135deg, #6B1F4F 0%, #D31789 50%, #f179c1 100%)',
  '혼합매체': 'linear-gradient(135deg, #1a1a2e 0%, #4A4A8E 50%, #7B5EA7 100%)',
}

const categoryPattern: Record<string, string> = {
  '플루이드아트': 'radial-gradient(ellipse at 30% 60%, rgba(0,191,166,0.5) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(255,255,255,0.15) 0%, transparent 50%)',
  '레진우드': 'radial-gradient(ellipse at 20% 80%, rgba(200,169,122,0.4) 0%, transparent 60%), radial-gradient(ellipse at 70% 30%, rgba(255,255,255,0.1) 0%, transparent 50%)',
  '크리스탈플라워': 'radial-gradient(ellipse at 50% 40%, rgba(255,255,255,0.2) 0%, transparent 50%), radial-gradient(ellipse at 80% 80%, rgba(241,121,193,0.4) 0%, transparent 60%)',
  '혼합매체': 'radial-gradient(ellipse at 40% 50%, rgba(123,94,167,0.5) 0%, transparent 60%), radial-gradient(ellipse at 70% 20%, rgba(255,255,255,0.1) 0%, transparent 40%)',
}

function highlightText(text: string, query: string): React.ReactNode {
  if (!query.trim()) return text
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
  const parts = text.split(regex)
  return parts.map((part, i) =>
    regex.test(part) ? (
      <mark key={i} className="gallery-search-highlight">{part}</mark>
    ) : (
      part
    )
  )
}

export default function GalleryPage() {
  const [category, setCategory] = useState<Category>('전체')
  const [modalWork, setModalWork] = useState<Work | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  const categories: Category[] = ['전체', '플루이드아트', '레진우드', '크리스탈플라워', '혼합매체']

  const works: Work[] = [
    { title: '오션 블루 웨이브', artist: '김○○', category: '플루이드아트', year: '2025', desc: '바다의 깊은 파란색을 플루이드 기법으로 표현한 작품', size: 'tall' },
    { title: '레진우드 테이블 세트', artist: '이○○', category: '레진우드', year: '2025', desc: '자연 원목과 투명 레진의 조화로운 테이블 작품', size: 'normal' },
    { title: '크리스탈 로즈 부케', artist: '박○○', category: '크리스탈플라워', year: '2025', desc: '장미를 크리스탈 레진으로 영원히 보존한 부케', size: 'normal' },
    { title: '갤럭시 드림', artist: '최○○', category: '플루이드아트', year: '2025', desc: '우주의 신비를 담은 갤럭시 테마 플루이드 작품', size: 'wide' },
    { title: '마블 라운드 트레이', artist: '정○○', category: '혼합매체', year: '2024', desc: '마블링 기법과 금박을 결합한 인테리어 트레이', size: 'normal' },
    { title: '레진 리버 보드', artist: '손○○', category: '레진우드', year: '2024', desc: '강물이 흐르는 듯한 블루 레진 서빙보드', size: 'tall' },
    { title: '선셋 플루이드', artist: '한○○', category: '플루이드아트', year: '2024', desc: '일몰의 따뜻한 색감을 플루이드로 표현', size: 'normal' },
    { title: '크리스탈 수국 램프', artist: '김○○', category: '크리스탈플라워', year: '2024', desc: '수국 꽃잎을 크리스탈 레진으로 감싼 무드등', size: 'wide' },
    { title: '어반 마블링', artist: '이○○', category: '혼합매체', year: '2024', desc: '도시적 감성의 흑백 마블링 캔버스', size: 'normal' },
    { title: '에메랄드 코스터', artist: '박○○', category: '레진우드', year: '2025', desc: '에메랄드빛 레진과 호두나무의 코스터 세트', size: 'normal' },
    { title: '봄바람 플루이드', artist: '최○○', category: '플루이드아트', year: '2025', desc: '봄의 산뜻한 파스텔 톤 플루이드 아트', size: 'tall' },
    { title: '프리저브드 카네이션', artist: '정○○', category: '크리스탈플라워', year: '2025', desc: '프리저브드 카네이션을 크리스탈로 보존한 작품', size: 'normal' },
  ]

  const getCategoryCount = (cat: Category) =>
    cat === '전체' ? works.length : works.filter(w => w.category === cat).length

  const filtered = useMemo(() => {
    let result = category === '전체' ? works : works.filter(w => w.category === category)
    if (searchQuery.trim()) {
      const q = searchQuery.trim().toLowerCase()
      result = result.filter(
        w =>
          w.title.toLowerCase().includes(q) ||
          w.artist.toLowerCase().includes(q) ||
          w.desc.toLowerCase().includes(q)
      )
    }
    return result
  }, [category, searchQuery])

  const isSearching = searchQuery.trim().length > 0

  return (
    <>
      <Nav />
      <section className="page-hero gallery-hero">
        <div className="gallery-hero-bg" />
        <div className="gallery-hero-content">
          <span className="gallery-hero-label">GALLERY</span>
          <h1>작품 갤러리</h1>
          <p>회원들의 아름다운 창작 작품을 감상하세요</p>
          <div className="gallery-hero-stat">총 {works.length}점의 작품</div>
        </div>
      </section>

      <section className="section">
        <div className="section-inner">
          {/* Category Filter + Search */}
          <ScrollReveal>
            <div className="gallery-filter-wrap">
              <div className="gallery-filter">
                {categories.map((cat) => (
                  <button
                    key={cat}
                    className={`filter-btn ${category === cat ? 'filter-active' : ''}`}
                    onClick={() => setCategory(cat)}
                  >
                    {cat}
                    <span className="filter-count">{getCategoryCount(cat)}</span>
                  </button>
                ))}
              </div>

              {/* Search Bar */}
              <div className="gallery-search-wrap">
                <div className="gallery-search-box">
                  <span className="gallery-search-icon">&#128269;</span>
                  <input
                    type="text"
                    className="gallery-search-input"
                    placeholder="작품명, 작가명, 설명으로 검색..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  {searchQuery && (
                    <button
                      className="gallery-search-clear"
                      onClick={() => setSearchQuery('')}
                      aria-label="검색어 지우기"
                    >
                      ✕
                    </button>
                  )}
                </div>
              </div>
            </div>
          </ScrollReveal>

          {/* Result count when searching */}
          {isSearching && (
            <p className="gallery-result-count">
              <strong>{filtered.length}</strong>개의 작품을 찾았습니다
              {filtered.length === 0 ? '' : ` — "${searchQuery}"`}
            </p>
          )}

          {/* Gallery Grid (masonry-like) */}
          <ScrollReveal delay={80}>
            <div className="gallery-masonry">
              {filtered.map((work, i) => {
                const gradient = categoryGradients[work.category] || categoryGradients['혼합매체']
                const pattern = categoryPattern[work.category] || categoryPattern['혼합매체']
                return (
                  <div
                    key={i}
                    className={`gallery-card gallery-card-${work.size}`}
                    onClick={() => setModalWork(work)}
                  >
                    <div
                      className="gallery-img-enhanced"
                      style={{ background: gradient }}
                    >
                      <div className="gallery-img-pattern" style={{ background: pattern }} />
                      <div className="gallery-img-overlay">
                        <span className="gallery-view-icon">+</span>
                      </div>
                      <span className="gallery-badge">{work.category}</span>
                      <span className="gallery-year-badge">{work.year}</span>
                    </div>
                    <div className="gallery-info">
                      <h3>{highlightText(work.title, searchQuery)}</h3>
                      <p className="gallery-meta">
                        {highlightText(work.artist, searchQuery)} · {work.year}
                      </p>
                      <p className="gallery-desc">{highlightText(work.desc, searchQuery)}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </ScrollReveal>

          {filtered.length === 0 && (
            <div className="gallery-empty">
              {isSearching ? (
                <p>
                  &ldquo;{searchQuery}&rdquo;에 해당하는 작품이 없습니다.<br />
                  <button
                    style={{ marginTop: '0.8rem', background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', fontFamily: 'inherit', fontSize: '0.95rem', textDecoration: 'underline' }}
                    onClick={() => setSearchQuery('')}
                  >
                    검색어 지우기
                  </button>
                </p>
              ) : (
                <p>해당 카테고리의 작품이 없습니다.</p>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Modal */}
      {modalWork && (
        <div className="gallery-modal-backdrop" onClick={() => setModalWork(null)}>
          <div className="gallery-modal" onClick={(e) => e.stopPropagation()}>
            <button className="gallery-modal-close" onClick={() => setModalWork(null)}>×</button>
            <div
              className="gallery-modal-img"
              style={{ background: categoryGradients[modalWork.category] || categoryGradients['혼합매체'] }}
            >
              <div
                className="gallery-img-pattern"
                style={{ background: categoryPattern[modalWork.category] || categoryPattern['혼합매체'] }}
              />
              <div className="gallery-modal-art-label">
                <span>{modalWork.category}</span>
              </div>
            </div>
            <div className="gallery-modal-info">
              <div className="gallery-modal-cat">{modalWork.category}</div>
              <h2 className="gallery-modal-title">{modalWork.title}</h2>
              <p className="gallery-modal-meta">{modalWork.artist} · {modalWork.year}</p>
              <p className="gallery-modal-desc">{modalWork.desc}</p>
              <div className="gallery-modal-divider" />
              <div className="gallery-modal-tags">
                <span className="gallery-modal-tag"># {modalWork.category}</span>
                <span className="gallery-modal-tag"># {modalWork.year}</span>
                <span className="gallery-modal-tag"># KACA</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <section className="section-cta">
        <div className="cta-inner">
          <h2>당신의 작품도 여기에</h2>
          <p>협회 회원이 되시면 갤러리에 작품을 전시할 수 있습니다</p>
          <a href="/contact" className="btn-cta-white">가입 문의하기</a>
        </div>
      </section>

      <Footer />
    </>
  )
}
