import { ipAddress, next } from '@vercel/edge'
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from "@upstash/redis";

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  // 25 requests from the same IP in 50 seconds
  limiter: Ratelimit.slidingWindow(25, '50 s'),
})

// Define which routes you want to rate limit
export const config = {
  matcher: '/api/sendmail',
}

export default async function middleware(request) {
    // You could alternatively limit based on user ID or similar
    const ip = ipAddress(request) || '127.0.0.1'
    const { success, pending, limit, reset, remaining } = await ratelimit.limit(
        ip
    )

    return success
        ? next()
        : Response.json({error: "BLOCKD", description: "too many requests, try again later."}, {status: 429, statusText: "Too Many Requests"})
}