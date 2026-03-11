import type { Metadata } from 'next'
import Nav from '../components/Nav'
import Footer from '../components/Footer'
import ProgramsContent from './ProgramsContent'

export const metadata: Metadata = {
  title: '교육과정 | 한국 아트크래프트 협회 (KACA)',
  description: '플루이드아트, 레진우드 베이직/마스터, 크리스탈 플라워, 원데이클래스 등 다양한 마블 플루이드 아트 교육과정을 만나보세요.',
  keywords: '플루이드아트 교육, 레진우드 과정, 크리스탈플라워, 원데이클래스, 마블아트 자격증',
  openGraph: {
    title: '교육과정 | 한국 아트크래프트 협회 (KACA)',
    description: '남녀노소 누구나 참여 가능한 플루이드 아트 교육과정. 베이직부터 마스터까지 단계별 커리큘럼을 제공합니다.',
    type: 'website',
    locale: 'ko_KR',
    siteName: '한국 아트크래프트 협회',
  },
}

export default function ProgramsPage() {
  const divisions = [
    { title: '레진플루이드아트마스터', color: '#1a3a5c', desc: '마블 플루이드 아트 레진 기법의 최고 전문가 과정' },
    { title: '아크릴플루이드마스터', color: '#6ba3d6', desc: '아크릴 물감을 활용한 플루이드 아트 전문 과정' },
    { title: '레진우드마스터', color: '#2d5016', desc: '레진과 우드를 결합한 가구/소품 제작 전문 과정' },
    { title: '크리스탈플라워마스터', color: '#c05080', desc: '크리스탈 레진으로 꽃을 담아내는 아트 전문 과정' },
    { title: '크래프트레진마스터', color: '#5b3d8f', desc: '레진 공예 액세서리/소품 제작 전문 과정' },
    { title: '블랑코오브제마스터', color: '#7a7a7a', desc: '흰색 기반 오브제 아트 전문 과정' },
    { title: '알콜잉크플로우마스터', color: '#b8600a', desc: '알콜잉크를 활용한 플로우 아트 전문 과정' },
  ]

  const programs = [
    {
      title: '레진플루이드아트마스터',
      img: '/images/programs/resin-fluidart.jpg',
      desc: '캔버스 위에 물감을 흘려 만드는 아름다운 마블링 아트입니다. 다양한 미술재료를 이용하여 독창적인 액체물감으로 물감을 흘리거나 부어 그 흐름을 이용하여 제작하는 예술 기법입니다.',
      details: ['남녀노소 누구나 참여 가능', '힐링 테라피 효과', '다양한 색상 조합 체험'],
    },
    {
      title: '아크릴플루이드마스터',
      img: '/images/programs/acrylic-fluidart.jpg',
      desc: '아크릴 물감을 활용한 플루이드 아트 전문 과정입니다. 다채로운 색상의 아크릴 물감으로 독창적인 마블링 작품을 제작합니다.',
      details: ['아크릴 물감 활용 기법', '다양한 마블링 패턴', '캔버스/보드 작품 제작'],
    },
    {
      title: '레진우드마스터',
      img: '/images/programs/resin-wood.jpg',
      desc: '레진과 우드를 결합한 전문 과정으로, 테이블·트레이 등 실용적인 레진우드 작품을 제작합니다.',
      details: ['레진+우드 결합 테크닉', '대형 작품 제작', '가구/소품 완성'],
    },
    {
      title: '크리스탈플라워마스터',
      img: '/images/programs/crystal-flower.jpg',
      desc: '크리스탈 레진으로 만드는 꽃 아트 과정입니다. 투명한 레진 속에 아름다운 꽃을 담아냅니다.',
      details: ['플라워 소재 선정', '크리스탈 레진 기법', '작품 완성 및 마감'],
    },
    {
      title: '크래프트레진마스터',
      img: '/images/programs/craft-resin.jpg',
      desc: '레진 공예 액세서리와 소품을 제작하는 전문 과정입니다. 키링, 펜던트, 트레이 등 다양한 크래프트 작품을 만듭니다.',
      details: ['레진 액세서리 제작', '몰드 활용 기법', '소품/잡화 완성'],
    },
    {
      title: '블랑코오브제마스터',
      img: '',
      desc: '흰색 기반의 오브제와 소품을 제작하는 전문 과정입니다. 미니멀한 감성의 인테리어 오브제를 만듭니다.',
      details: ['흰색 오브제 디자인', '인테리어 소품 제작', '미니멀 아트 기법'],
    },
    {
      title: '알콜잉크플로우마스터',
      img: '',
      desc: '알콜잉크를 활용한 플로우 아트 전문 과정입니다. 독특한 색감과 흐름으로 추상적인 작품을 제작합니다.',
      details: ['알콜잉크 기초 이론', '플로우 기법 응용', '타일/코스터 작품 제작'],
    },
  ]

  return (
    <>
      <Nav />
      <section className="page-hero">
        <h1>교육과정</h1>
        <p>다양한 플루이드 아트 프로그램을 만나보세요</p>
      </section>

      <ProgramsContent programs={programs} divisions={divisions} />

      <Footer />
    </>
  )
}
