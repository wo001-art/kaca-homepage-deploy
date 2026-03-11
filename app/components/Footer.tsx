import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-top">
          <div className="footer-brand">
            <div className="footer-logo">KACA</div>
            <p>한국 아트크래프트 협회<br />Korea Art Craft Association</p>
          </div>
          <div className="footer-links">
            <div className="footer-col">
              <h4>교육과정</h4>
              <Link href="/programs">레진플루이드아트</Link>
              <Link href="/programs">아크릴플루이드</Link>
              <Link href="/programs">레진우드</Link>
              <Link href="/programs">크리스탈플라워</Link>
            </div>
            <div className="footer-col">
              <h4>협회</h4>
              <Link href="/about">소개</Link>
              <Link href="/about">임원진</Link>
              <Link href="/events">전시 이력</Link>
            </div>
            <div className="footer-col">
              <h4>문의</h4>
              <a href="tel:010-4714-7585">010-4714-7585</a>
              <a href="mailto:wo.001@wookvan.com">wo.001@wookvan.com</a>
              <Link href="/contact">문의 양식</Link>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <span>© 2026 Korea Art Craft Association. All rights reserved.</span>
        </div>
      </div>
    </footer>
  )
}
