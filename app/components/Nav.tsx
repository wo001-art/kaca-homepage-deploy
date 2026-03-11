'use client'
import { useState } from 'react'
import Link from 'next/link'

export default function Nav() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <nav className="nav">
      <div className="nav-inner">
        <Link href="/" className="nav-logo">
          <img src="/images/logo-kaca.jpg" alt="KACA" className="nav-logo-img" />
          <div className="nav-logo-text">
            <span className="nav-logo-main">KACA</span>
            <span className="nav-logo-sub">한국아트크래프트협회</span>
          </div>
        </Link>
        <ul className={`nav-links ${mobileOpen ? 'nav-links-open' : ''}`}>
          <li><Link href="/programs" onClick={() => setMobileOpen(false)}>교육과정</Link></li>
          <li><Link href="/about" onClick={() => setMobileOpen(false)}>협회소개</Link></li>
          <li><Link href="/events" onClick={() => setMobileOpen(false)}>전시/이벤트</Link></li>
          <li><Link href="/gallery" onClick={() => setMobileOpen(false)}>갤러리</Link></li>
          <li><Link href="/notice" onClick={() => setMobileOpen(false)}>공지사항</Link></li>
          <li><Link href="/contact" onClick={() => setMobileOpen(false)}>문의</Link></li>
        </ul>
        <Link href="/contact" className="btn-cta nav-cta-btn">가입 문의</Link>
        <button className="nav-mobile" onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? '✕' : '☰'}
        </button>
      </div>
    </nav>
  )
}
