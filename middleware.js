import { ipAddress, next } from '@vercel/edge'
import { Ratelimit } from '@upstash/ratelimit'
import { Redis } from "@upstash/redis";

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  // 5 requests from the same IP in 10 seconds
  limiter: Ratelimit.slidingWindow(2, '60 s'),
})

// Define which routes you want to rate limit
export const config = {
  matcher: '/api/:path*',
}

export default async function middleware(request) {
    console.log('works!');
    // You could alternatively limit based on user ID or similar
    const ip = ipAddress(request) || '127.0.0.1'
    const { success, pending, limit, reset, remaining } = await ratelimit.limit(
        ip
    )

    console.log('success?', success);

    return success
        ? next()
        : Response.json({errcode: "BLOCKD", description: "too many requests, try again later."}, {status: 429, statusText: "Too Many Requests"})
}