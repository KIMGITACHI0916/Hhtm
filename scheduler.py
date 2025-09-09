# scheduler.py
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from waifu_picker import pick_waifu  # 🔥 Import picker

# Shared scheduler (global)
scheduler = AsyncIOScheduler()

# --- Waifu Dropper ---
async def drop_waifu(application, chat_id):
    try:
        chosen = pick_waifu()  # Get waifu from waifu_picker.py
        await application.bot.send_message(
            chat_id=chat_id,
            text=f"💮 A wild **{chosen}** has appeared!"
        )
    except Exception as e:
        print(f"[ERROR] drop_waifu({chat_id}): {e}")

# --- Start scheduler for a group ---
async def start_scheduler(application, chat_id, interval=30, duration=300):
    job_id = f"drop_{chat_id}"

    if scheduler.get_job(job_id):
        print(f"[INFO] Scheduler already running for {chat_id}")
        return

    scheduler.add_job(
        drop_waifu,
        IntervalTrigger(seconds=interval),
        args=[application, chat_id],
        id=job_id,
        replace_existing=True,
    )
    print(f"[INFO] Scheduler started for {chat_id} every {interval}s")

    async def auto_stop():
        await asyncio.sleep(duration)
        stop_scheduler(chat_id)

    asyncio.create_task(auto_stop())

# --- Stop scheduler for a group ---
def stop_scheduler(chat_id):
    job_id = f"drop_{chat_id}"
    job = scheduler.get_job(job_id)
    if job:
        job.remove()
        print(f"[INFO] Scheduler stopped for {chat_id}")

# --- Start global scheduler ---
def start_global_scheduler():
    if not scheduler.running:
        scheduler.start()
        print("[INFO] Global scheduler started")
        
