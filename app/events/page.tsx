import type { Metadata } from 'next'
import Nav from '../components/Nav'
import Footer from '../components/Footer'
import EventsContent from './EventsContent'

export const metadata: Metadata = {
  title: '전시/이벤트 | 한국 아트크래프트 협회 (KACA)',
  description: '고양국제아트페어, 회원전, 워크숍, 아트마켓 등 KACA의 다양한 전시 및 이벤트 활동을 확인하세요.',
  keywords: '플루이드아트 전시, KACA 이벤트, 마블아트 워크숍, 고양국제아트페어, 회원전',
  openGraph: {
    title: '전시/이벤트 | 한국 아트크래프트 협회 (KACA)',
    description: '연 3~5회 전시 참가, 전국 워크숍, 아트마켓까지 — KACA 회원들의 생동감 넘치는 활동 이력을 만나보세요.',
    type: 'website',
    locale: 'ko_KR',
    siteName: '한국 아트크래프트 협회',
  },
}

export default function EventsPage() {
  const exhibitions = [
    { date: '2025.07', title: '자연의 순환전', location: '무주', desc: '자연과 예술의 조화를 주제로 한 회원전' },
    { date: '2025.04', title: '자연순환전', location: '강릉', desc: '강릉에서 펼쳐진 봄 회원전' },
    { date: '2025.10', title: '고양국제아트페어', location: '킨텍스', desc: '제24회 고양국제아트페어 참가' },
    { date: '2023.05', title: '마블아트마켓전', location: '인사동', desc: '인사동에서 열린 마블아트 마켓' },
    { date: '2023.09', title: '울산 장생포 전시', location: '울산 문화창고', desc: '장생포 문화창고에서의 대규모 전시' },
    { date: '2022.10', title: 'FALL in 강릉', location: '강릉', desc: '가을 강릉에서 펼쳐진 회원전' },
  ]

  const activities = [
    { title: '전시 참여', desc: '고양국제아트페어, 뱅크아트페어 등 연 3~5회 전시에 참여합니다. 회원들의 작품을 대중에게 선보이는 소중한 기회입니다.', icon: '🎨' },
    { title: '회원 교류', desc: '전국 420여 명 회원과 함께하는 창작 네트워크입니다. 온·오프라인을 통해 활발한 소통과 협력이 이루어집니다.', icon: '🤝' },
    { title: '워크숍', desc: '지역별 회원 공방에서 정기적으로 진행하는 워크숍입니다. 새로운 기법과 트렌드를 공유합니다.', icon: '🖌️' },
    { title: '아트마켓', desc: '인사동, 강릉 등 전국 각지에서 열리는 아트마켓에 참가하여 작품을 판매하고 교류합니다.', icon: '🏪' },
  ]

  return (
    <>
      <Nav />
      <section className="page-hero">
        <h1>전시 / 이벤트</h1>
        <p>전국 각지에서 펼쳐진 우리 협회의 활동을 만나보세요</p>
      </section>

      <EventsContent exhibitions={exhibitions} activities={activities} />

      <Footer />
    </>
  )
}
