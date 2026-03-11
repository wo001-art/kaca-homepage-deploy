'use client'

import { useEffect, useRef, ReactNode } from 'react'

interface ScrollRevealProps {
  children: ReactNode
  delay?: number
  direction?: 'up' | 'left' | 'right'
  className?: string
}

export default function ScrollReveal({
  children,
  delay = 0,
  direction = 'up',
  className = '',
}: ScrollRevealProps) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const timer = setTimeout(() => {
              entry.target.classList.add('revealed')
            }, delay)
            observer.unobserve(entry.target)
            return () => clearTimeout(timer)
          }
        })
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    )

    observer.observe(el)
    return () => observer.disconnect()
  }, [delay])

  const directionClass =
    direction === 'left'
      ? 'scroll-reveal scroll-reveal-left'
      : direction === 'right'
      ? 'scroll-reveal scroll-reveal-right'
      : 'scroll-reveal'

  return (
    <div
      ref={ref}
      className={`${directionClass}${className ? ' ' + className : ''}`}
    >
      {children}
    </div>
  )
}
