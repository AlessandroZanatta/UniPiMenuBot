from telegram import (
    Update,
    ForceReply,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    LabeledPrice,
)
from telegram.utils.helpers import escape_markdown
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)
from telegram.error import Unauthorized

from db.crud import *
from utils.utils import *
from logger.logger import log

from utils.utils import get_menu_path


def start(update: Update, context: CallbackContext) -> None:
    """Check if the user is already registered. If not, send a welcome message and add the user to the subscribers."""
    user = update.effective_user
    chat_id = update.message.chat.id

    if is_already_subbed(chat_id):
        update.message.reply_text("Ti sei già iscrittə!")
        return

    update.message.reply_text(
        """Benvenutə nell'unofficial bot UniPi Menù!
Qua puoi trovare i menu settimanali di tutte le mense universitarie di Pisa ogni lunedì alle 7.30.

È in arrivo quello corrente, buon pasto! 🍕🍝🧆"""
    )

    add_user(chat_id)
    increment_number_of_users()
    context.bot.send_document(
        chat_id,
        document=open(get_menu_path(), "rb"),
        filename=get_menu_name(),
    )


def update_menu(context: CallbackContext) -> None:
    """Update the menu pdf by retrieving it from the official DSU website."""
    log.info("Updating the menu...")
    get_full_menu()
    log.info("Menu correctly updated!")


def send_menu(context: CallbackContext) -> None:
    """Send the menu to every user that is subscribed to the bot. Additionally, count the number of active users."""
    chat_ids = get_users()
    menu_name = get_menu_name()

    # Send the menu as a file to the first user that is still active
    while True:
        try:
            fid = context.bot.send_document(
                int(chat_ids.pop()),
                document=open(get_menu_path(), "rb"),
                filename=menu_name,
            ).document.file_id
            break
        except Unauthorized:
            pass

    active_users = 1

    # Then use the file_id to optimize sending the menu to every other user
    for chat_id in chat_ids:
        try:
            context.bot.send_document(
                int(chat_id),
                document=fid,
                filename=menu_name,
            )
            active_users += 1
        except Unauthorized:
            pass

    set_number_of_active_users(active_users)


def about_the_bot(update: Update, context: CallbackContext) -> None:
    update.message.reply_markdown(
        escape_markdown(
            f"""Il mio creatore è pigro, quindi mi ha creato per recuperare il menù tutti i giorni al suo posto! Spero di tornare utile anche a te!
Se vuoi sostenere il corretto funzionamento del bot, puoi offire al mio creatore un caffè virtuale con /buy_me_a_coffee!

Il sorgente del bot è disponibile """
        )
        + "[su github](https://github.com/AlessandroZanatta/UniPiMenuBot)"
        + escape_markdown(
            "! Se ci sono del problemi con il funzionamento del bot o hai delle idee per delle nuove funzionalità, "
        )
        + "[scrivi pure qua](https://github.com/AlessandroZanatta/UniPiMenuBot/issues/new)"
        + f"""!

Attualmente, l'applicazione viene utilizzata da {get_number_of_active_users()} studenti universitari!"""
    )


def buy_me_a_coffee(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("In arrivo in futuro... ☕️")
