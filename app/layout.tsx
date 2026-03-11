import type { Metadata, Viewport } from 'next'
import './globals.css'

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export const metadata: Metadata = {
  title: {
    default: '한국 아트크래프트 협회 | 마블 플루이드 아트 (KACA)',
    template: '%s | KACA',
  },
  description: '한국 아트크래프트 협회(KACA) - 420여 명 회원과 함께하는 마블 플루이드 아트 협회. 교육, 전시, 자격증 과정을 운영합니다.',
  keywords: '한국아트크래프트협회, KACA, 마블플루이드아트, 레진아트, 플루이드아트, 크리스탈플라워, 전시, 교육, 원데이클래스, 레진우드',
  authors: [{ name: '한국 아트크래프트 협회' }],
  creator: '한국 아트크래프트 협회',
  openGraph: {
    title: '한국 아트크래프트 협회 | 마블 플루이드 아트 (KACA)',
    description: '420여 명 회원과 함께하는 마블 플루이드 아트 협회. 교육, 전시, 자격증 과정을 운영합니다.',
    type: 'website',
    locale: 'ko_KR',
    siteName: '한국 아트크래프트 협회',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  )
}
