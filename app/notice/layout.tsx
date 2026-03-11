import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '공지사항 | 한국 아트크래프트 협회 (KACA)',
  description: '한국 아트크래프트 협회의 최신 공지, 소식, 교육 일정을 확인하세요. 전시 안내, 자격증 시험 일정, 워크숍 모집 등 다양한 정보를 제공합니다.',
  keywords: 'KACA 공지사항, 마블플루이드아트 소식, 협회 교육 일정, 플루이드아트 전시 공지',
  openGraph: {
    title: '공지사항 | 한국 아트크래프트 협회 (KACA)',
    description: 'KACA의 최신 공지와 소식을 확인하세요. 전시, 교육, 자격증 시험 일정을 놓치지 마세요.',
    type: 'website',
    locale: 'ko_KR',
    siteName: '한국 아트크래프트 협회',
  },
}

export default function NoticeLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
