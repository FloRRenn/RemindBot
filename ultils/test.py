import asyncpraw
import asyncio

async def main():
    reddit = asyncpraw.Reddit(
        client_id = "mNQvUsUerhYPAQRPdiRo9A",
        client_secret = "wMQcKlzXglgfFsu4YfCL0V80f5IEWw",
        user_agent = "myBostPythonDiscord",
    )

    subreddit = await reddit.subreddit("realasians")
    async for submission in subreddit.top(time_filter="day", limit=5):
        print(submission.url)

asyncio.run(main())
        
