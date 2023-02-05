import datetime
import logging
import os
from typing import Dict

from dotenv import load_dotenv
from telegram import (ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                      Update)
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)
from telegram.ext.filters import User

import check_script
import models

load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Replace with your Telegram bot token
TOKEN = os.environ["TELEGRAM_TOKEN"]
authorized_user_id_1 = int(os.environ["AUTHORIZED_USER_ID_1"])
authorized_user_id_2 = int(os.environ["AUTHORIZED_USER_ID_2"])
ALLOWED_IDS = [authorized_user_id_1, authorized_user_id_2]


CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ["Pee", "Poop"],
    ["Sleep", "Eat"],
    ["Done"],
]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


async def check_command(update, context):
    # Check if the user is authorized
    if update.message.from_user.id not in [authorized_user_id_1, authorized_user_id_2]:
        await update.message.reply_text(
            "You are not authorized to use this command.")
        return

    # Check internet connectivity
    internet = check_script.check_internet()

    # Check DNS resolution
    dns = check_script.check_dns()

    # Check firewall response
    firewall = check_script.check_firewall()

    # Check IP response
    nas = check_script.check_nas()

    ifconfig_me = check_script.get_ifconfig_me_all()

    # Save the results to the database
    models.check_save_to_database(internet, dns, firewall, nas, ifconfig_me)

    # Send the results to the user
    await update.message.reply_text(
        "Internet: " + internet + "\nDNS: " + dns + "\nFirewall: " + firewall + "\nNAS: " + nas + "\nInternet Information: " + ifconfig_me)


async def ana_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Check if the user is authorized
    if update.message.from_user.id not in [authorized_user_id_1, authorized_user_id_2]:
        await update.message.reply_text(
            "You are not authorized to use this command.")
        return
    else:
        await update.message.reply_text(
            "Hi! This is Borregrado bot, I will help you to keep track of your Ana's activities.\n\n"
            "Send /cancel to stop talking to me.\n\n"
            "What do you want to register?",
            reply_markup=markup
        )
        return CHOOSING


async def regular_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text.lower() == "pee":
        context.user_data["pee"] = True
    elif text.lower() == "poop":
        context.user_data["poop"] = True
    await update.message.reply_text(f"Ana {text.lower()}? I will remember that! \n What else do you want to register?",
                                    reply_markup=markup)
    return CHOOSING


async def custom_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text.lower() == "sleep":
        context.user_data["sleep"] = True
        context.user_data["sleep_time"] = 0
        context.user_data["eat"] = False
        await update.message.reply_text(
            'Alright, how much time Ana sleept? Please enter it in hours.',
        )
    elif text.lower() == "eat":
        context.user_data["sleep"] = False
        context.user_data["sleep_time"] = 0
        context.user_data["eat"] = True
        await update.message.reply_text(
            'Alright, how much Ana ate? One or both breast?".',
        )

    return TYPING_REPLY


async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    text = update.message.text
    if user_data["sleep"] == True & user_data["sleep_time"] == 0:
        user_data["sleep_time"] = text
    elif user_data["eat"] == True:
        user_data["eat_quality"] = text
    await update.message.reply_text(
        "Something else?",
        reply_markup=markup,
    )

    return CHOOSING


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
        "Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler(
        "start", start, filters=User(ALLOWED_IDS)))
    application.add_handler(CommandHandler(
        "help", help_command, filters=User(ALLOWED_IDS)))
    application.add_handler(CommandHandler(
        "check", check_command, filters=User(ALLOWED_IDS)))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("ana", ana_command)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex(
                        "^(Pee|Poop)$"), regular_choice
                ),
                MessageHandler(filters.Regex(
                    "^(Eat|Sleep)$"), custom_choice),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex(
                        "^Done$")), regular_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND |
                                     filters.Regex("^Done$")),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
