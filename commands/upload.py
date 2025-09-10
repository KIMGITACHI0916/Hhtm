async def upload_waifu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message  # works for text + captions
    user_id = update.effective_user.id

    if user_id != OWNER_ID:
        await message.reply_text("🚫 Only the owner can upload waifus.")
        return

    # Get text from either normal text or caption
    text = message.text or message.caption
    if not text:
        await message.reply_text("⚠️ You must provide waifu details in the command text or caption.")
        return

    matches = re.findall(r"\((.*?)\)", text)
    if len(matches) < 4:
        await message.reply_text(
            "⚠️ Usage: /upload (Name) (Series) (Rarity) (ID) [FileID]"
        )
        return

    name = matches[0].strip()
    series = matches[1].strip()
    rarity = matches[2].strip()
    
    try:
        waifu_id = int(matches[3].strip())
    except ValueError:
        await message.reply_text("⚠️ ID must be an integer.")
        return

    # Get image: reply to photo or optional file ID
    file_id = None
    if message.reply_to_message and message.reply_to_message.photo:
        photo = message.reply_to_message.photo[-1]  # best quality
        file_id = photo.file_id
    elif len(matches) >= 5:
        file_id = matches[4].strip()
    
    if not file_id:
        await message.reply_text(
            "⚠️ Please reply to a photo or provide a valid Telegram file ID."
        )
        return

    # Check for duplicate ID
    if waifus.find_one({"id": waifu_id}):
        await message.reply_text(f"⚠️ Waifu with ID {waifu_id} already exists!")
        return

    # Prepare waifu doc
    new_waifu = {
        "id": waifu_id,
        "name": name,
        "rarity": rarity,
        "desc": f"From {series}",
        "image": file_id,
    }

    waifus.insert_one(new_waifu)

    await message.reply_text(
        f"✅ Added {name} | Rarity: {rarity} | ID: {waifu_id}"
    )
    
