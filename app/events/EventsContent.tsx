'use client'

import ScrollReveal from '../components/ScrollReveal'

interface Exhibition {
  date: string
  title: string
  location: string
  desc: string
}

interface Activity {
  title: string
  desc: string
  icon: string
}

interface EventsContentProps {
  exhibitions: Exhibition[]
  activities: Activity[]
}

export default function EventsContent({ exhibitions, activities }: EventsContentProps) {
  return (
    <>
      {/* Activities */}
      <ScrollReveal>
        <section className="section">
          <div className="section-inner">
            <div className="section-header">
              <h2>주요 활동</h2>
            </div>
            <div className="events-grid">
              {activities.map((a, i) => (
                <ScrollReveal key={a.title} delay={i * 80}>
                  <div className="event-card">
                    <div className="event-icon">{a.icon}</div>
                    <h3>{a.title}</h3>
                    <p>{a.desc}</p>
                  </div>
                </ScrollReveal>
              ))}
            </div>
          </div>
        </section>
      </ScrollReveal>

      {/* Exhibition List */}
      <ScrollReveal delay={100}>
        <section className="section section-dark">
          <div className="section-inner">
            <div className="section-header">
              <h2>전시 이력</h2>
              <p>지금까지의 전시 활동을 소개합니다</p>
            </div>
            <div className="exhibition-list">
              {exhibitions.map((ex, i) => (
                <ScrollReveal key={ex.date + ex.title} delay={i * 60}>
                  <div className="exhibition-card">
                    <div className="exhibition-date">{ex.date} · {ex.location}</div>
                    <h3>{ex.title}</h3>
                    <p>{ex.desc}</p>
                  </div>
                </ScrollReveal>
              ))}
            </div>
          </div>
        </section>
      </ScrollReveal>

      <section className="section-cta">
        <div className="cta-inner">
          <h2>다음 전시에 함께하세요</h2>
          <p>회원이 되시면 전시 참여 기회가 주어집니다</p>
          <a href="/contact" className="btn-cta-white">가입 문의하기</a>
        </div>
      </section>
    </>
  )
}
