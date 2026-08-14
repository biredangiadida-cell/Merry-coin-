from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from config import BOT_TOKEN, COIN_PER_CLICK, DAILY_BONUS
from database import (
    create_user,
    get_user,
    update_user,
    add_coins
)

from datetime import datetime


def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🪙 Coin Sassaabi", callback_data="collect"),
            InlineKeyboardButton("💰 Balance", callback_data="balance")
        ],
        [
            InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily"),
            InlineKeyboardButton("👥 Invite", callback_data="invite")
        ],
        [
            InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
            InlineKeyboardButton("👤 Profile", callback_data="profile")
        ],
        [
            InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    create_user(
        user.id,
        user.first_name,
        user.username
    )

    await update.message.reply_text(
        f"🎉 Baga nagaan dhuftan, {user.first_name}!\n\n"
        "🪙 **MERRYCOIN**\n\n"
        "Coin kee sassaabi, hiriyoota affeeri, bonus argadhu.\n\n"
        "👇 Menu keessaa filadhu:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    user = get_user(user_id)

    if not user:
        create_user(
            user_id,
            query.from_user.first_name,
            query.from_user.username
        )
        user = get_user(user_id)

    if query.data == "collect":

        coins = add_coins(
            user_id,
            COIN_PER_CLICK
        )

        await query.answer(
            f"+{COIN_PER_CLICK} 🪙 Coin!",
            show_alert=False
        )

        await query.edit_message_text(
            f"🪙 **Merrycoin**\n\n"
            f"🎉 Coin argatte!\n\n"
            f"💰 Balance: **{coins} MC**\n\n"
            "Coin dabalachuuf button kana irra deebi'ii tuqi.",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

    elif query.data == "balance":

        user = get_user(user_id)

        await query.edit_message_text(
            f"💰 **Balance Kee**\n\n"
            f"🪙 Coin: **{user['coins']} MC**\n"
            f"👥 Referrals: **{user['referrals']}**",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

    elif query.data == "daily":

        today = datetime.now().strftime("%Y-%m-%d")

        user = get_user(user_id)

        if user["last_daily"] == today:

            await query.answer(
                "❌ Daily bonus har'a fudhatameera.",
                show_alert=True
            )

        else:

            coins = add_coins(
                user_id,
                DAILY_BONUS
            )

            update_user(
                user_id,
                {
                    "last_daily": today
                }
            )

            await query.edit_message_text(
                f"🎁 **Daily Bonus**\n\n"
                f"🎉 +{DAILY_BONUS} MC argatte!\n\n"
                f"💰 Balance: **{coins} MC**",
                reply_markup=main_menu(),
                parse_mode="Markdown"
            )

    elif query.data == "invite":

        bot = await context.bot.get_me()

        link = f"https://t.me/{bot.username}?start=ref_{user_id}"

        await query.edit_message_text(
            "👥 **Hiriyoota Affeeri**\n\n"
            "Link kana hiriyoota keetiif qoodi:\n\n"
            f"`{link}`\n\n"
            "🎁 Namni link kee irraa dhufu yeroo system referral keessatti galmaa'u bonus argatta.",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

    elif query.data == "profile":

        user = get_user(user_id)

        username = user["username"] or "N/A"

        await query.edit_message_text(
            f"👤 **Profile**\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"👤 Name: {user['first_name']}\n"
            f"🔗 Username: @{username}\n"
            f"🪙 Coins: **{user['coins']} MC**\n"
            f"👥 Referrals: **{user['referrals']}**",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

    elif query.data == "withdraw":

        await query.edit_message_text(
            "💸 **Withdraw**\n\n"
            "Withdraw system yeroo ammaa qophaa'aa jira.\n\n"
            "🪙 Coin kee kuufadhu.",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

    elif query.data == "leaderboard":

        await query.edit_message_text(
            "🏆 **Leaderboard**\n\n"
            "Leaderboard system itti aansee ni dabalama.",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )


def run():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    print("Merrycoin Bot started...")

    app.run_polling()


if __name__ == "__main__":
    run()
