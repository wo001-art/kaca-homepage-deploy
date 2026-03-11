'use client'

import ScrollReveal from '../components/ScrollReveal'

interface Program {
  title: string
  img: string
  desc: string
  details: string[]
}

interface Division {
  title: string
  color: string
  desc: string
}

interface ProgramsContentProps {
  programs: Program[]
  divisions: Division[]
}

export default function ProgramsContent({ programs, divisions }: ProgramsContentProps) {
  const toId = (title: string) => title.replace(/\s/g, '-')

  const handleCardClick = (title: string) => {
    const el = document.getElementById(toId(title))
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }

  return (
    <>
      <section className="section">
        <div className="section-inner">
          <div className="section-header">
            <h2>자격증 분과</h2>
            <p>7개 전문 분과에서 자격증을 취득하세요</p>
          </div>
          <div className="division-banner-grid">
            {divisions.map((div) => (
              <div
                className="division-banner-card"
                key={div.title}
                style={{ background: div.color }}
                onClick={() => handleCardClick(div.title)}
              >
                <span>{div.title}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section section-programs-detail">
        <div className="section-inner">
          {programs.map((p, i) => (
            <ScrollReveal key={p.title} delay={i * 80} direction={i % 2 === 0 ? 'left' : 'right'}>
              <div id={toId(p.title)} className={`program-detail ${i % 2 === 1 ? 'program-detail-reverse' : ''}`}>
                {p.img ? (
                  <div className="program-detail-img">
                    <img src={p.img} alt={p.title} />
                  </div>
                ) : (
                  <div className="program-detail-img program-detail-placeholder">
                    <span className="placeholder-text">이미지 준비 중</span>
                  </div>
                )}
                <div className="program-detail-text">
                  <h2>{p.title}</h2>
                  <p>{p.desc}</p>
                  <ul>
                    {p.details.map((d) => (
                      <li key={d}>{d}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </ScrollReveal>
          ))}
        </div>
      </section>

      <section className="section-cta">
        <div className="cta-inner">
          <h2>교육 프로그램에 관심이 있으신가요?</h2>
          <p>문의를 통해 가까운 공방과 일정을 확인하세요</p>
          <a href="/contact" className="btn-cta-white">문의하기</a>
        </div>
      </section>
    </>
  )
}
