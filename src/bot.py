#!/usr/bin/env python
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    ConversationHandler,
    PreCheckoutQueryHandler,
)
from pydantic.error_wrappers import ValidationError

from settings.settings import settings
from logger.logger import log
from utils.utils import *
from db.crud import set_number_of_active_users
from handlers.handlers import *


def main():
    log.info("Starting bot...")
    if not os.path.exists(settings.menus_dir):
        os.mkdir(settings.menus_dir)

    get_full_menu()
    set_number_of_active_users(get_number_of_users())

    # Create the bot updater
    try:
        updater = Updater(settings.bot_api_key)
    except ValidationError:
        log.fatal("Missing bot_api_key!")
        exit(-1)

    # Setup the scheduler to activate every week on monday
    scheduler = updater.job_queue
    dispatcher = updater.dispatcher

    # dispatcher.add_handler(CommandHandler("update_menu", update_menu))
    scheduler.run_custom(
        update_menu,
        job_kwargs={"trigger": "cron", "day_of_week": "mon", "hour": 7, "minute": 0},
    )

    # dispatcher.add_handler(CommandHandler("send_menu", send_menu))
    scheduler.run_custom(
        send_menu,
        job_kwargs={"trigger": "cron", "day_of_week": "mon", "hour": 7, "minute": 30},
    )

    dispatcher.add_handler(CommandHandler("about", about_the_bot))
    dispatcher.add_handler(CommandHandler("start", start))

    # Start the bot
    try:
        updater.start_polling()
    except Unauthorized:
        log.fatal("bot_api_key is incorrect!")
        exit(-1)

    # Start bot event-loop
    updater.idle()


if __name__ == "__main__":
    main()
