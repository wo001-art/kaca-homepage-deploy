import type { Metadata } from 'next'
import Nav from '../components/Nav'
import Footer from '../components/Footer'
import AboutContent from './AboutContent'

export const metadata: Metadata = {
  title: '협회소개 | 한국 아트크래프트 협회 (KACA)',
  description: '한국 아트크래프트 협회(KACA)를 소개합니다. 420여 명의 회원과 함께하는 마블 플루이드 아트 협회의 비전, 임원진, 활동 이력을 확인하세요.',
  keywords: '한국아트크래프트협회 소개, KACA 임원진, 마블플루이드아트 협회, 플루이드아트 단체',
  openGraph: {
    title: '협회소개 | 한국 아트크래프트 협회 (KACA)',
    description: '420여 명의 회원, 9000여 점의 작품, 15회 이상의 전시를 이어온 마블 플루이드 아트 협회를 소개합니다.',
    type: 'website',
    locale: 'ko_KR',
    siteName: '한국 아트크래프트 협회',
  },
}

export default function AboutPage() {
  const members = [
    { name: '손종탁', role: '협회장', location: '울산', initial: '손' },
    { name: '이지연', role: '부회장', location: '파주 헤이리', initial: '이' },
    { name: '김영숙', role: '문화홍보이사', location: '남양주', initial: '김' },
    { name: '한기홍', role: '제품개발기획이사', location: '', initial: '한' },
    { name: '이소영', role: '교육이사', location: '안산/화성', initial: '이' },
  ]

  return (
    <>
      <Nav />
      <section className="page-hero">
        <h1>협회소개</h1>
        <p>한국 아트크래프트 협회(KACA)를 소개합니다</p>
      </section>

      <AboutContent members={members} />

      <Footer />
    </>
  )
}
