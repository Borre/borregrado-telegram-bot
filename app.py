import os

from dotenv import load_dotenv
from telegram import (ForceReply, InlineKeyboardButton, InlineKeyboardMarkup,
                      Update)
from telegram.ext import (Application, CallbackContext, CallbackQueryHandler,
                          CommandHandler, ContextTypes, MessageHandler,
                          filters)
from telegram.ext.filters import User

import check_script
import models

load_dotenv()

# Replace with your Telegram bot token
TOKEN = os.environ["TELEGRAM_TOKEN"]
authorized_user_id_1 = int(os.environ["AUTHORIZED_USER_ID_1"])
authorized_user_id_2 = int(os.environ["AUTHORIZED_USER_ID_2"])
ALLOWED_IDS = [authorized_user_id_1, authorized_user_id_2]


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


async def ana_command(update: Update, context: CallbackContext):
    # Check if the user is authorized
    if update.message.from_user.id not in [authorized_user_id_1, authorized_user_id_2]:
        await update.message.reply_text(
            "You are not authorized to use this command.")
        return
    else:
        options = ["Poop", "Pee", "Eat", "Sleep"]
        keyboard = []
        for option in options:
            button = InlineKeyboardButton(option, callback_data=option)
            keyboard.append([button])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Please select an option:", reply_markup=reply_markup)


def ana_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    option = query.data
    if option == "Poop":
        models.ana_save_to_database(poop=True)
    elif option == "Pee":
        models.ana_save_to_database(pee=True)
    elif option == "Eat":
        if update.message:
            print("Update variable is here")
            ana_eat_command(update, context)
            update.message.reply_text("Please select an option for {}:".format(
                "eat"))
        else:
            print("Update variable is None")
    elif option == "Sleep":
        models.ana_save_to_database(sleep=True)
        query.answer(text=f"You selected: {option}")


def ana_eat_command(update: Update, context: CallbackContext):
    print("ana_eat_command")
    options = ["1 Breast", "Both Breast", "Formula 1 oz", "Formula 2 oz"]
    keyboard = []
    for option in options:
        button = InlineKeyboardButton(option, callback_data=option)
        keyboard.append([button])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Please select an option for {}:".format(
        option), reply_markup=reply_markup)

# Telegram bot


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler(
        "start", start, filters=User(ALLOWED_IDS)))
    application.add_handler(CommandHandler(
        "help", help_command, filters=User(ALLOWED_IDS)))
    application.add_handler(CommandHandler(
        "check", check_command, filters=User(ALLOWED_IDS)))

    application.add_handler(CommandHandler(
        "ana", ana_command, filters=User(ALLOWED_IDS)))

    application.add_handler(CallbackQueryHandler(
        ana_menu(Update, CallbackContext)))

    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, echo))
    application.run_polling()


if __name__ == "__main__":
    main()
