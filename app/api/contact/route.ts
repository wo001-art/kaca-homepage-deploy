import { NextRequest, NextResponse } from 'next/server'

// n8n Notion WF webhook endpoint
const N8N_WEBHOOK_URL = 'https://n8n.wookvan.com/webhook/ee4897b1-8329-4f93-8696-369835c16360'

// 입력값 검증
function validateInput(name: string, phone: string, message: string): string | null {
  if (!name || name.trim().length === 0) return '이름을 입력해주세요.'
  if (!phone || phone.trim().length === 0) return '연락처를 입력해주세요.'
  if (!message || message.trim().length === 0) return '문의 내용을 입력해주세요.'
  if (name.trim().length > 50) return '이름은 50자 이내로 입력해주세요.'
  if (phone.trim().length > 20) return '연락처는 20자 이내로 입력해주세요.'
  if (message.trim().length > 2000) return '문의 내용은 2000자 이내로 입력해주세요.'
  return null
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { name, phone, message } = body

    // 입력값 검증
    const validationError = validateInput(name, phone, message)
    if (validationError) {
      return NextResponse.json(
        { success: false, error: validationError },
        { status: 400 }
      )
    }

    const trimmedName = name.trim()
    const trimmedPhone = phone.trim()
    const trimmedMessage = message.trim()

    // n8n webhook으로 Notion에 저장 (worklog DB)
    const n8nPayload = {
      action: 'create',
      database: 'worklog',
      data: {
        Name: `홈페이지 문의: ${trimmedName}`,
        Status: '접수',
        Description: `${trimmedMessage}\n\n연락처: ${trimmedPhone}`,
      },
    }

    const n8nResponse = await fetch(N8N_WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(n8nPayload),
    })

    if (!n8nResponse.ok) {
      // n8n 실패 시 자연어 방식으로 재시도
      const fallbackPayload = {
        message: `KACA 홈페이지 문의 접수. 이름: ${trimmedName}, 연락처: ${trimmedPhone}, 내용: ${trimmedMessage}`,
      }

      const fallbackResponse = await fetch(N8N_WEBHOOK_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(fallbackPayload),
      })

      if (!fallbackResponse.ok) {
        throw new Error(`n8n webhook failed: ${fallbackResponse.status}`)
      }
    }

    return NextResponse.json(
      { success: true, message: '문의가 접수되었습니다.' },
      { status: 200 }
    )
  } catch (error) {
    console.error('Contact form error:', error)
    return NextResponse.json(
      { success: false, error: '문의 접수 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.' },
      { status: 500 }
    )
  }
}
