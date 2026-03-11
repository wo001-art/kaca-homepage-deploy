import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '작품 갤러리 | 한국 아트크래프트 협회 (KACA)',
  description: 'KACA 회원들의 아름다운 플루이드아트, 레진우드, 크리스탈플라워, 혼합매체 작품을 카테고리별로 감상하세요.',
  keywords: '플루이드아트 갤러리, 레진우드 작품, 크리스탈플라워, 마블아트 작품 전시, KACA 회원 작품',
  openGraph: {
    title: '작품 갤러리 | 한국 아트크래프트 협회 (KACA)',
    description: '420여 명 KACA 회원들의 창작 작품을 한눈에 — 플루이드아트부터 크리스탈플라워까지.',
    type: 'website',
    locale: 'ko_KR',
    siteName: '한국 아트크래프트 협회',
  },
}

export default function GalleryLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
