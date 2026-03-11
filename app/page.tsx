'use client'

import { useState } from 'react'
import Link from 'next/link'
import Nav from './components/Nav'
import Footer from './components/Footer'
import ScrollReveal from './components/ScrollReveal'

export default function Home() {
  return (
    <>
      <Nav />
      <Hero />
      <ScrollReveal>
        <ProgramsHighlight />
      </ScrollReveal>
      <ScrollReveal delay={100}>
        <EventsHighlight />
      </ScrollReveal>
      <ScrollReveal delay={100}>
        <Testimonials />
      </ScrollReveal>
      <ScrollReveal>
        <CtaBanner />
      </ScrollReveal>
      <Footer />
    </>
  )
}

/* ── Hero ── */
function Hero() {
  return (
    <section className="hero" style={{ backgroundImage: 'url(/images/hero-bg.png)' }}>
      <div className="hero-overlay" />
      <div className="hero-content">
        <h1>Welcome to<br /><em>Korea Art Craft Association</em></h1>
        <p>
          마블 플루이드 아트의 아름다운 세계로 여러분을 초대합니다.<br />
          누구나 예술가가 될 수 있는 즐겁고 편안한 창작의 시간을 경험하세요.
        </p>
        <div className="hero-buttons">
          <Link href="/contact" className="btn-cta">가입 문의하기</Link>
          <Link href="/programs" className="btn-outline-white">교육과정 보기</Link>
        </div>
      </div>
    </section>
  )
}

/* ── Programs Highlight (메인페이지용 간략 카드) ── */
function ProgramsHighlight() {
  const programs = [
    { img: '/images/programs/resin-fluidart.jpg', title: '레진플루이드아트' },
    { img: '/images/programs/acrylic-fluidart.jpg', title: '아크릴플루이드' },
    { img: '/images/programs/resin-wood.jpg', title: '레진우드' },
    { img: '/images/programs/crystal-flower.jpg', title: '크리스탈플라워' },
    { img: '/images/programs/craft-resin.jpg', title: '크래프트레진' },
  ]

  return (
    <section className="section">
      <div className="section-inner">
        <div className="section-header">
          <h2>교육과정</h2>
          <p>다양한 플루이드 아트 프로그램을 만나보세요</p>
        </div>
        <div className="highlight-grid">
          {programs.map((p) => (
            <Link href="/programs" key={p.title} className="highlight-card">
              <div className="highlight-img">
                <img src={p.img} alt={p.title} />
              </div>
              <h3>{p.title}</h3>
            </Link>
          ))}
        </div>
      </div>
    </section>
  )
}

/* ── Events Highlight (메인페이지용 간략 카드) ── */
function EventsHighlight() {
  const events = [
    { title: '전시 참여', desc: '고양국제아트페어, 뱅크아트페어 등 연 3~5회', icon: '🎨' },
    { title: '회원 교류', desc: '전국 420여 명 회원 창작 네트워크', icon: '🤝' },
    { title: '워크숍', desc: '지역별 정기 워크숍 진행', icon: '🖌️' },
    { title: '아트마켓', desc: '전국 각지 아트마켓 참가', icon: '🏪' },
  ]

  return (
    <section className="section section-light">
      <div className="section-inner">
        <div className="section-header">
          <h2>전시 / 이벤트</h2>
          <p>다양한 행사를 통해 예술의 즐거움을 나눕니다</p>
        </div>
        <div className="events-grid">
          {events.map((e) => (
            <Link href="/events" key={e.title} className="event-card">
              <div className="event-icon">{e.icon}</div>
              <h3>{e.title}</h3>
              <p>{e.desc}</p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  )
}

/* ── Testimonials ── */
function Testimonials() {
  const [current, setCurrent] = useState(0)
  const reviews = [
    { text: '플루이드 아트를 처음 접했는데 정말 힐링이 됩니다. 물감이 흘러가는 모습을 보면서 마음이 편안해져요.', author: '김○○ 회원', location: '서울' },
    { text: '원데이클래스로 시작해서 지금은 정회원이 되었어요. 전시에도 참여하고 정말 보람찬 활동입니다.', author: '이○○ 회원', location: '부산' },
    { text: '아이들과 함께 체험했는데 남녀노소 누구나 즐길 수 있어서 좋았습니다. 가족 활동으로 추천합니다!', author: '박○○ 회원', location: '대전' },
  ]

  return (
    <section className="section section-testimonial">
      <div className="section-inner">
        <div className="section-header">
          <h2>회원들의 이야기</h2>
        </div>
        <div className="testimonial-carousel">
          {reviews.map((r, i) => (
            <div key={i} className={`testimonial-slide ${i === current ? 'active' : ''}`}>
              <blockquote>&ldquo;{r.text}&rdquo;</blockquote>
              <div className="testimonial-author">— {r.author}, {r.location}</div>
            </div>
          ))}
        </div>
        <div className="testimonial-dots">
          {reviews.map((_, i) => (
            <button key={i} className={`dot ${i === current ? 'dot-active' : ''}`} onClick={() => setCurrent(i)} />
          ))}
        </div>
      </div>
    </section>
  )
}

/* ── CTA Banner ── */
function CtaBanner() {
  return (
    <section className="section-cta">
      <div className="cta-inner">
        <h2>함께 예술의 흐름을 만들어가요</h2>
        <p>마블 플루이드 아트에 관심이 있다면 누구나 환영합니다</p>
        <Link href="/contact" className="btn-cta-white">가입 문의하기</Link>
      </div>
    </section>
  )
}
