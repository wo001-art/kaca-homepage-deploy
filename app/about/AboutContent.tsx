'use client'

import ScrollReveal from '../components/ScrollReveal'
import Link from 'next/link'

interface Member {
  name: string
  role: string
  location: string
  initial: string
}

interface AboutContentProps {
  members: Member[]
}

export default function AboutContent({ members }: AboutContentProps) {
  return (
    <>
      {/* Our Story */}
      <ScrollReveal>
        <section className="section">
          <div className="section-inner">
            <div className="about-layout">
              <div className="about-image">
                <img src="/images/about-fluid.png" alt="마블 플루이드 아트" />
              </div>
              <div className="about-text">
                <h2>협회 소개</h2>
                <h3>마블 플루이드 아트의<br />새로운 가능성을 열다</h3>
                <p>
                  한국 아트크래프트 협회(KACA)는 마블 플루이드 아트를 중심으로
                  예술적 교류와 창작 활동을 지원하는 단체입니다.
                  회원 간의 활발한 소통과 협력을 통해 예술적 역량을 강화하고,
                  전시, 교육 등 다양한 활동을 통해 마블 플루이드 아트의
                  저변 확대를 위해 노력합니다.
                </p>
                <p>
                  끊임없는 새로운 시도와 도전을 통해 예술계에 긍정적인 영향을
                  미치고, 회원들의 성장과 발전을 적극적으로 지원합니다.
                </p>
                <div className="about-stats">
                  <div className="stat-item">
                    <span className="stat-num">420+</span>
                    <span className="stat-label">회원</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-num">9,000+</span>
                    <span className="stat-label">작품 사진</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-num">15+</span>
                    <span className="stat-label">전시 개최</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </ScrollReveal>

      {/* Team */}
      <ScrollReveal delay={100}>
        <section className="section section-light">
          <div className="section-inner">
            <div className="section-header">
              <h2>임원진 소개</h2>
              <p>협회를 이끌어가는 핵심 리더들을 소개합니다</p>
            </div>
            <div className="team-grid">
              {members.map((m) => (
                <div key={m.name} className="team-card">
                  <div className="team-avatar">{m.initial}</div>
                  <div className="team-name">{m.name}</div>
                  <div className="team-role">{m.role}</div>
                  {m.location && <div className="team-location">{m.location}</div>}
                </div>
              ))}
            </div>
          </div>
        </section>
      </ScrollReveal>

      <section className="section-cta">
        <div className="cta-inner">
          <h2>함께 예술의 흐름을 만들어가요</h2>
          <p>마블 플루이드 아트에 관심이 있다면 누구나 환영합니다</p>
          <a href="/contact" className="btn-cta-white">가입 문의하기</a>
        </div>
      </section>
    </>
  )
}
