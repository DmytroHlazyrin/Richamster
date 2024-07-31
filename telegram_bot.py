from decouple import config
import logging
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

API_TOKEN = config("TG_TOKEN")
DJANGO_API_URL = config("API_URL")
DJANGO_RANDOM_BOOK_URL = config("RANDOM_BOOK_URL")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


reply_keyboard = [
    [KeyboardButton("Add book")],
    [KeyboardButton("List book")],
    [KeyboardButton("Random book")],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Select an option:", reply_markup=markup)


async def handle_message(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    text = update.message.text
    logger.info(f"Received message: {text}")

    if text == "Add book":
        await update.message.reply_text(
            "Send me the book name and author in the format: "
            "'Book Name - Author'"
        )
        context.user_data["awaiting_book_info"] = True

    elif text == "List book":
        response = requests.get(DJANGO_API_URL)
        logger.info(
            f"List book response status: {response.status_code}, "
            f"response text: {response.text}"
        )
        if response.status_code == 200:
            data = response.json()
            books = data[:10]  # First 10 books
            books_list = "\n".join(
                [f"{book['name']} by {book['author']}" for book in books]
            )
            await update.message.reply_text(f"Books:\n{books_list}")
        else:
            await update.message.reply_text("Failed to fetch data from API.")

    elif text == "Random book":
        response = requests.get(DJANGO_RANDOM_BOOK_URL)
        logger.info(
            f"Random book response status: {response.status_code}, "
            f"response text: {response.text}"
        )
        if response.status_code == 200:
            books = response.json()
            if books:
                book = books[0]
                await update.message.reply_text(
                    f"Random Book: {book['name']} by {book['author']}"
                )
            else:
                await update.message.reply_text("No books found.")
        else:
            await update.message.reply_text("Failed to fetch data from API.")

    elif (
        "awaiting_book_info" in context.user_data
        and context.user_data["awaiting_book_info"]
    ):
        text = update.message.text
        logger.info(f"Book info received: {text}")
        if " - " in text:
            name, author = text.split(" - ")
            response = requests.post(
                DJANGO_API_URL, json={"name": name, "author": author}
            )
            logger.info(
                f"Add book response status: {response.status_code}, "
                f"response text: {response.text}"
            )
            if response.status_code == 201:
                await update.message.reply_text(
                    f"Book '{name}' by {author} added successfully."
                )
            else:
                await update.message.reply_text(
                    f"Failed to add the book. "
                    f"Response status: {response.status_code}, "
                    f"response text: {response.text}"
                )
        else:
            await update.message.reply_text(
                "Please send the book name and author "
                "in the correct format: 'Book Name - Author'"
            )
        context.user_data["awaiting_book_info"] = False


def main() -> None:
    application = ApplicationBuilder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
