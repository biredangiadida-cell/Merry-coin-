from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from config import (
    BOT_TOKEN,
    COIN_PER_CLICK,
    DAILY_BONUS,
    REFERRAL_BONUS,
)

from database import (
    create_user,
    get_user,
    add_coins,
    set_daily,
    add_referral,
)

from datetime import datetime


# =========================
# MAIN MENU
# =========================

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton(
                "🪙 Coin Sassaabi",
                callback_data="collect"
            ),
            InlineKeyboardButton(
                "💰 Balance",
                callback_data="balance"
            ),
        ],
        [
            InlineKeyboardButton(
                "🎁 Daily Bonus",
                callback_data="daily"
            ),
            InlineKeyboardButton(
                "👥 Invite",
                callback_data="invite"
            ),
        ],
        [
            InlineKeyboardButton(
                "🏆 Leaderboard",
                callback_data="leaderboard"
            ),
            InlineKeyboardButton(
                "👤 Profile",
                callback_data="profile"
            ),
        ],
        [
            InlineKeyboardButton(
                "💸 Withdraw",
                callback_data="withdraw"
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# START
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    referred_by = None

    # Referral link:
    # /start ref_123456789

    if context.args:

        argument = context.args[0]

        if argument.startswith("ref_"):

            try:
                referred_by = int(
                    argument.replace("ref_", "")
                )
            except ValueError:
                referred_by = None

    # Prevent self-referral

    if referred_by == user.id:
        referred_by = None

    # Check if user already exists

    old_user = get_user(user.id)

    create_user(
        user.id,
        user.first_name,
        user.username,
        referred_by
    )

    # Referral reward

    if old_user is None and referred_by:

        referrer = get_user(referred_by)

        if referrer:

            add_coins(
                referred_by,
                REFERRAL_BONUS
            )

            add_referral(
                referred_by
            )

            try:

                await context.bot.send_message(
                    chat_id=referred_by,
                    text=(
                        "🎉 **Referral Milestone!**\n\n"
                        f"Namni tokko link kee irraa seene.\n"
                        f"🎁 +{REFERRAL_BONUS} MC argatte!"
                    ),
                    parse_mode="Markdown"
                )

            except Exception:
                pass

    await update.message.reply_text(
        f"🎉 **Baga Nagaan Dhuftan!**\n\n"
        f"👤 {user.first_name}\n\n"
        "🪙 **MERRYCOIN**\n\n"
        "Coin kee sassaabi.\n"
        "Hiriyoota kee affeeri.\n"
        "Daily bonus fudhadhu.\n\n"
        "👇 Menu keessaa filadhu:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )


# =========================
# BUTTON HANDLER
# =========================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    user = get_user(user_id)

    # Create account if missing

    if not user:

        create_user(
            user_id,
            query.from_user.first_name,
            query.from_user.username
        )

        user = get_user(user_id)

    # =====================
    # COLLECT COINS
    # =====================

    if query.data == "collect":

        coins = add_coins(
            user_id,
            COIN_PER_CLICK
        )

        await query.answer(
            f"+{COIN_PER_CLICK} 🪙 MC",
            show_alert=False
        )

        await query.edit_message_text(
            "🪙 **MERRYCOIN**\n\n"
            f"🎉 +{COIN_PER_CLICK} MC argatte!\n\n"
            f"💰 Balance: **{coins} MC**\n\n"
            "🪙 Coin dabalachuuf button kana irra deebi'ii tuqi.",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

    # =====================
    # BALANCE
    # =====================

    elif query.data == "balance":

        user = get_user(user_id)

        await query.edit_message_text(
            "💰 **BALANCE KEE**\n\n"
            f"🪙 Coin: **{user[3]} MC**\n"
            f"👥 Referrals: **{user[4]}**\n\n"
            "👇 Menu:",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

    # =====================
    # DAILY BONUS
    # =====================

    elif query.data == "daily":

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )

        user = get_user(user_id)

        last_daily = user[6]

        if last_daily == today:

            await query.answer(
                "❌ Daily bonus har'a fudhatameera.",
                show_alert=True
            )

            return

        coins = add_coins(
            user_id,
            DAILY_BONUS
        )

        set_daily(
            user_id,
            today
        )

        await query.edit_message_text(
            "🎁 **DAILY BONUS**\n\n"
            f"🎉 +{DAILY_BONUS} MC argatte!\n\n"
            f"💰 Balance: **{coins} MC**\n\n"
            "⏰ Boru deebi'i.",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

    # =====================
    # INVITE
    # =====================

    elif query.data == "invite":

        bot = await context.bot.get_me()

        link = (
            f"https://t.me/"
            f"{bot.username}"
            f"?start=ref_{user_id}"
        )

        await query.edit_message_text(
            "👥 **HIRIYOOTA AFFEERI**\n\n"
            "Link kee kana qoodi:\n\n"
            f"`{link}`\n\n"
            f"🎁 Nama tokko affeeruun "
            f"**{REFERRAL_BONUS} MC** argatta.",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

    # =====================
    # PROFILE
    # =====================

    elif query.data == "profile":

        user = get_user(user_id)

        username = user[2] or "N/A"

        await query.edit_message_text(
            "👤 **PROFILE KEE**\n\n"
            f"🆔 ID: `{user[0]}`\n"
            f"👤 Maqaa: {user[1]}\n"
            f"🔗 Username: @{username}\n\n"
            f"🪙 Coins: **{user[3]} MC**\n"
            f"👥 Referrals: **{user[4]}**",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

    # =====================
    # WITHDRAW
    # =====================

    elif query.data == "withdraw":

        await query.edit_message_text(
            "💸 **WITHDRAW**\n\n"
            "Withdraw system amma qophaa'aa jira.\n\n"
            "🪙 Coin kee kuufadhu.\n"
            "📢 Yeroo sirni withdrawal banamu "
            "beeksifama.",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

    # =====================
    # LEADERBOARD
    # =====================

    elif query.data == "leaderboard":

        await query.edit_message_text(
            "🏆 **LEADERBOARD**\n\n"
            "Leaderboard system itti aansee ni dabalama.\n\n"
            "🪙 Coin kee sassaabiitii sadarkaa kee ol kaasi!",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )


# =========================
# HELP
# =========================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "❓ **MERRYCOIN HELP**\n\n"
        "🪙 Coin Sassaabi — coin argadhu\n"
        "🎁 Daily Bonus — bonus guyyaa fudhadhu\n"
        "👥 Invite — hiriyoota affeeri\n"
        "💰 Balance — coin kee ilaali\n"
        "👤 Profile — account kee ilaali\n"
        "💸 Withdraw — withdrawal request\n\n"
        "📢 Gargaarsaaf admin qunnami.",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )


# =========================
# ERROR HANDLER
# =========================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    print(
        "ERROR:",
        context.error
    )


# =========================
# RUN BOT
# =========================

def run():

    if not BOT_TOKEN:

        print(
            "ERROR: BOT_TOKEN hin galchine!"
        )

        return

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Commands

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )

    # Buttons

    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    # Error handler

    app.add_error_handler(
        error_handler
    )

    print(
        "Merrycoin Bot started..."
    )

    app.run_polling()


# =========================
# START
# =========================

if __name__ == "__main__":
    run()
