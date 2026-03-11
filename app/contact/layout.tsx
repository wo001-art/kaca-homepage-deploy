import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '문의하기 | 한국 아트크래프트 협회 (KACA)',
  description: '가입, 교육, 전시 등 궁금한 점을 문의해주세요. 전화 010-4714-7585 또는 문의 양식을 이용하세요.',
  keywords: 'KACA 문의, 마블플루이드아트 가입, 플루이드아트 원데이클래스 신청, 협회 연락처',
  openGraph: {
    title: '문의하기 | 한국 아트크래프트 협회 (KACA)',
    description: '마블 플루이드 아트에 관심이 있으신가요? 가입부터 교육, 전시 참여까지 무엇이든 문의해 주세요.',
    type: 'website',
    locale: 'ko_KR',
    siteName: '한국 아트크래프트 협회',
  },
}

export default function ContactLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
