# Copyright @ISmartDevs
# Channel t.me/TheSmartDev
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
import logging
from config import OWNER_IDS, COMMAND_PREFIX
from telegraph import Telegraph

# Setup LOGGER
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Telegraph client
telegraph = Telegraph()
telegraph.create_account(
    short_name="SmartUtilBot",
    author_name="SmartUtilBot",
    author_url="https://t.me/TheSmartDevs"
)

def setup_logs_handler(app: Client):
    logger.info("Setting up logs handler")

    async def create_telegraph_page(content: str) -> str:
        """Create a Telegraph page with the given content, truncating to 40,000 characters"""
        try:
            # Truncate content to 40,000 characters to respect Telegraph limits
            truncated_content = content[:40000]
            response = telegraph.create_page(
                title="SmartLogs",
                html_content=f"<pre>{truncated_content}</pre>",
                author_name="SmartUtilBot",
                author_url="https://t.me/TheSmartDevs"
            )
            return f"https://telegra.ph/{response['path']}"
        except Exception as e:
            logger.error(f"Failed to create Telegraph page: {e}")
            return None

    @app.on_message(filters.command(["logs"], prefixes=COMMAND_PREFIX) & (filters.private | filters.group))
    async def logs_command(client, message):
        user_id = message.from_user.id
        logger.info(f"Logs command from user {user_id}")
        if user_id not in OWNER_IDS:
            logger.info("User not admin, sending restricted message")
            await client.send_message(
                chat_id=message.chat.id,
                text="**🚫 Hey Gay 🏳️‍🌈 This Is Not For You This Only For Males👱‍♂️**",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Send a loading message
        loading_message = await client.send_message(
            chat_id=message.chat.id,
            text="**Checking The Logs...💥**",
            parse_mode=ParseMode.MARKDOWN
        )

        # Wait for 2 seconds
        await asyncio.sleep(2)

        # Check if logs exist
        if not os.path.exists("botlog.txt"):
            await loading_message.edit_text(
                text="**Sorry Bro No Logs Found**",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        logger.info("User is admin, sending log document")
        await client.send_document(
            chat_id=message.chat.id,
            document="botlog.txt",
            caption="""**✘ Hey Sir! Here Is Your Order ↯**
**✘━━━━━━━━━━━━━━━━━━━━━━━━━↯**
**✘ All Logs Database Succesfully Exported! ↯**
**↯ Access Granted Only to Authorized Admins ↯**
**✘━━━━━━━━━━━━━━━━━━━━━━━━━↯**
**✘ Select an Option Below to View Logs:**
**✘ Logs Here Offer the Fastest and Clearest Access! ↯**
**✘━━━━━━━━━━━━━━━━━━━━━━━━━↯**
**✘Huge Respect For You My Master↯**""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✘ Display Logs↯", callback_data="display_logs"),
                    InlineKeyboardButton("✘ Web Paste↯", callback_data="web_paste$")
                ],
                [InlineKeyboardButton("✘ Close↯", callback_data="close_doc$")]
            ])
        )

        # Delete the temporary "Checking The Logs..." message
        await loading_message.delete()

    @app.on_callback_query(filters.regex(r"^(close_doc\$|close_logs\$|web_paste\$|display_logs)$"))
    async def handle_callback(client: Client, query: CallbackQuery):
        user_id = query.from_user.id
        data = query.data
        logger.info(f"Callback query from user {user_id}, data: {data}")
        if user_id not in OWNER_IDS:
            logger.info("User not admin, sending callback answer")
            await query.answer(
                text="🚫 Hey Gay 🏳️‍🌈 This Is Not For You This Only For Males👱‍♂️",
                show_alert=True
            )
            return
        logger.info("User is admin, processing callback")
        if data == "close_doc$":
            await query.message.delete()
            await query.answer()
        elif data == "close_logs$":
            await query.message.delete()
            await query.answer()
        elif data == "web_paste$":
            await query.answer("Uploading logs to Telegraph...")
            # Edit the main log message to show uploading status
            await query.message.edit_caption(
                caption="**✘Uploading SmartLogs To Telegraph↯**",
                parse_mode=ParseMode.MARKDOWN
            )
            # Check if logs exist
            if not os.path.exists("botlog.txt"):
                await query.message.edit_caption(
                    caption="**✘Sorry Bro Telegraph API Dead↯**",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            try:
                # Read and truncate logs
                with open("botlog.txt", "r", encoding="utf-8") as f:
                    logs_content = f.read()
                # Create Telegraph page
                telegraph_url = await create_telegraph_page(logs_content)
                if telegraph_url:
                    await query.message.edit_caption(
                        caption="""**✘ Hey Sir! Here Is Your Order ↯**
**✘━━━━━━━━━━━━━━━━━━━━━━━━━↯**
**✘ All Logs Database Succesfully Exported! ↯**
**↯ Access Granted Only to Authorized Admins ↯**
**✘━━━━━━━━━━━━━━━━━━━━━━━━━↯**
**✘ Select an Option Below to View Logs:**
**✘ Logs Here Offer the Fastest and Clearest Access! ↯**
**✘━━━━━━━━━━━━━━━━━━━━━━━━━↯**
**✘Huge Respect For You My Master↯**""",
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("✘ View Web↯", url=telegraph_url)]
                        ])
                    )
                else:
                    await query.message.edit_caption(
                        caption="**✘Sorry Bro Telegraph API Dead↯**",
                        parse_mode=ParseMode.MARKDOWN
                    )
            except Exception as e:
                logger.error(f"Error uploading to Telegraph: {e}")
                await query.message.edit_caption(
                    caption="**✘Sorry Bro Telegraph API Dead↯**",
                    parse_mode=ParseMode.MARKDOWN
                )
        elif data == "display_logs":
            await send_logs_page(client, query.message.chat.id)
            await query.answer()

    async def send_logs_page(client: Client, chat_id: int):
        """Send the last 20 lines of botlog.txt, respecting Telegram's 4096-character limit"""
        logger.info(f"Sending latest logs to chat {chat_id}")
        if not os.path.exists("botlog.txt"):
            await client.send_message(
                chat_id=chat_id,
                text="**✘Sorry Bro No Logs Found↯**",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        try:
            with open("botlog.txt", "r", encoding="utf-8") as f:
                logs = f.readlines()
            # Get the last 20 lines (or fewer if the file is shorter)
            latest_logs = logs[-20:] if len(logs) > 20 else logs
            text = "".join(latest_logs)
            # Truncate to 4096 characters (Telegram's message limit)
            if len(text) > 4096:
                text = text[-4096:]
            await client.send_message(
                chat_id=chat_id,
                text=text if text else "No logs available.",
                parse_mode=ParseMode.DISABLED,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✘ Back↯", callback_data="close_logs$")]
                ])
            )
        except Exception as e:
            logger.error(f"Error sending logs: {e}")
            await client.send_message(
                chat_id=chat_id,
                text="**✘Sorry There Was A Issue On My Server↯**",
                parse_mode=ParseMode.MARKDOWN
            )
