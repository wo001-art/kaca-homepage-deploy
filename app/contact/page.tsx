'use client'

import { useState } from 'react'
import Nav from '../components/Nav'
import Footer from '../components/Footer'
import ScrollReveal from '../components/ScrollReveal'

// metadata는 'use client' 컴포넌트에서 export 불가 — layout.tsx 또는 별도 서버 래퍼로 처리
// SEO는 layout.tsx의 전역 metadata를 상속하며, 아래 정보는 참고용 주석으로 유지
// title: '문의하기 | 한국 아트크래프트 협회 (KACA)'
// description: '가입, 교육, 전시 등 궁금한 점을 문의해주세요. 전화 010-4714-7585 또는 문의 양식을 이용하세요.'

type FormStatus = 'idle' | 'loading' | 'success' | 'error'

export default function ContactPage() {
  const [open, setOpen] = useState<number | null>(null)

  // 문의 폼 상태
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [message, setMessage] = useState('')
  const [formStatus, setFormStatus] = useState<FormStatus>('idle')
  const [statusMessage, setStatusMessage] = useState('')

  const faqs = [
    { q: '마블 플루이드 아트가 뭔가요?', a: '다양한 미술재료를 이용하여 독창적인 액체물감으로 물감을 흘리거나 부어 그 흐름을 이용하여 제작하는 예술 기법입니다. 남녀노소 누구나 아름다운 컬러로 힐링할 수 있는 힐링테라피입니다.' },
    { q: '회원 가입은 어떻게 하나요?', a: '협회 부회장(이지연, 010-4714-7585)에게 연락하시거나, 아래 문의 양식을 통해 가입 신청하실 수 있습니다.' },
    { q: '원데이클래스도 운영하나요?', a: '네, 전국 각 지역의 회원 공방에서 원데이클래스를 운영하고 있습니다. 문의하시면 가까운 공방을 안내해 드립니다.' },
    { q: '전시 참여는 어떻게 하나요?', a: '협회 회원이시면 연 3~5회 열리는 회원전, 기획전, 초대전에 참여하실 수 있습니다. 전시 일정은 공지사항을 통해 안내됩니다.' },
    { q: '자격증 과정이 있나요?', a: '레진우드 베이직/마스터 과정, 크리스탈 플라워 마스터 과정 등 다양한 자격증 교육 프로그램을 운영하고 있습니다.' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // 기본 검증
    if (!name.trim() || !phone.trim() || !message.trim()) {
      setFormStatus('error')
      setStatusMessage('모든 항목을 입력해주세요.')
      return
    }

    setFormStatus('loading')
    setStatusMessage('')

    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, phone, message }),
      })

      const data = await res.json()

      if (res.ok && data.success) {
        setFormStatus('success')
        setStatusMessage('문의가 접수되었습니다. 빠른 시일 내에 연락드리겠습니다.')
        // 폼 초기화
        setName('')
        setPhone('')
        setMessage('')
      } else {
        setFormStatus('error')
        setStatusMessage(data.error || '문의 접수 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.')
      }
    } catch {
      setFormStatus('error')
      setStatusMessage('네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.')
    }
  }

  return (
    <>
      <Nav />
      <section className="page-hero">
        <h1>문의하기</h1>
        <p>가입, 교육, 전시 등 궁금한 점을 문의해주세요</p>
      </section>

      {/* Contact Form */}
      <ScrollReveal>
      <section className="section">
        <div className="section-inner">
          <div className="contact-layout">
            <div className="contact-info">
              <h3>연락처</h3>
              <div className="contact-item">
                <span className="contact-icon">📞</span>
                <div>
                  <div className="contact-label">전화</div>
                  <div className="contact-value">010-4714-7585</div>
                </div>
              </div>
              <div className="contact-item">
                <span className="contact-icon">✉️</span>
                <div>
                  <div className="contact-label">이메일</div>
                  <div className="contact-value">wo.001@wookvan.com</div>
                </div>
              </div>
              <div className="contact-item">
                <span className="contact-icon">📍</span>
                <div>
                  <div className="contact-label">주소</div>
                  <div className="contact-value">경기도 구리시 갈매순환로166번길 45<br />구리갈매아너시티 지하4층 BH434호</div>
                </div>
              </div>
              <div className="contact-item">
                <span className="contact-icon">📱</span>
                <div>
                  <div className="contact-label">밴드</div>
                  <div className="contact-value">마블플루이드아트</div>
                </div>
              </div>
            </div>
            <div className="contact-form">
              <h3>문의 양식</h3>

              {/* 상태 알림 */}
              {formStatus === 'success' && (
                <div className="form-alert form-alert-success">
                  {statusMessage}
                </div>
              )}
              {formStatus === 'error' && (
                <div className="form-alert form-alert-error">
                  {statusMessage}
                </div>
              )}

              <form onSubmit={handleSubmit} noValidate>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="contact-name">이름</label>
                    <input
                      id="contact-name"
                      type="text"
                      placeholder="이름을 입력해주세요"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      disabled={formStatus === 'loading'}
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="contact-phone">연락처</label>
                    <input
                      id="contact-phone"
                      type="tel"
                      placeholder="010-0000-0000"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      disabled={formStatus === 'loading'}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label htmlFor="contact-message">문의 내용</label>
                  <textarea
                    id="contact-message"
                    placeholder="문의하실 내용을 적어주세요"
                    rows={5}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    disabled={formStatus === 'loading'}
                  />
                </div>
                <button
                  type="submit"
                  className={`btn-cta btn-full${formStatus === 'loading' ? ' btn-loading' : ''}`}
                  disabled={formStatus === 'loading'}
                >
                  {formStatus === 'loading' ? '보내는 중...' : '문의 보내기'}
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>
      </ScrollReveal>

      {/* FAQ */}
      <ScrollReveal delay={100}>
      <section className="section section-light">
        <div className="section-inner">
          <div className="section-header">
            <h2>자주 묻는 질문</h2>
          </div>
          <div className="faq-list">
            {faqs.map((faq, i) => (
              <div key={i} className={`faq-item ${open === i ? 'faq-open' : ''}`}>
                <button className="faq-q" onClick={() => setOpen(open === i ? null : i)}>
                  <span>{faq.q}</span>
                  <span className="faq-icon">{open === i ? '−' : '+'}</span>
                </button>
                <div className="faq-a">
                  <p>{faq.a}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
      </ScrollReveal>

      <Footer />
    </>
  )
}
