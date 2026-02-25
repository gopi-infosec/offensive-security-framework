// app/api/chat/route.ts - 2026 WORKING VERSION
import { GoogleGenerativeAI } from '@google/generative-ai'
import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  try {
    const apiKey = process.env.NEXT_PUBLIC_GEMINI_API_KEY
    if (!apiKey) {
      return NextResponse.json({ error: 'API key missing' }, { status: 500 })
    }

    const body = await req.json()
    const { message } = body

    if (!message) {
      return NextResponse.json({ error: 'No message' }, { status: 400 })
    }

    console.log('🚀 Using gemini-2.0-flash...')
    
    const genAI = new GoogleGenerativeAI(apiKey)
    
    // ✅ 2026 WORKING MODELS (in order of reliability)
    const modelNames = [
      "gemini-2.0-flash",
      "gemini-2.5-flash", 
      "gemini-2.5-pro",
      "gemini-1.5-flash"
    ]

    let result
    for (const modelName of modelNames) {
      try {
        console.log(`🔍 Trying model: ${modelName}`)
        const model = genAI.getGenerativeModel({ model: modelName })
        result = await model.generateContentStream(message)
        console.log(`✅ SUCCESS with ${modelName}`)
        break
      } catch (e) {
        console.log(`❌ ${modelName} failed, trying next...`)
        continue
      }
    }

    if (!result) {
      throw new Error('No working models found')
    }

    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      async start(controller) {
        for await (const chunk of result.stream) {
          const text = chunk.text()
          controller.enqueue(encoder.encode(text))
        }
        controller.close()
      },
    })

    return new NextResponse(stream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-cache',
      },
    })
  } catch (error: any) {
    console.error('❌ FINAL ERROR:', error.message)
    return NextResponse.json(
      { error: `Failed: ${error.message}` },
      { status: 500 }
    )
  }
}

