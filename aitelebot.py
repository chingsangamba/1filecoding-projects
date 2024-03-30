#!/usr/bin/env python
# pyright: reportUnusedVariable=false, reportGeneralTypeIssues=false
"""

Hit RUN to execute the program.

You can also deploy a stable, public version of your project, unaffected by the changes you make in the workspace.

This proof-of-concept Telegram bot takes a user's text messages and turns them into stylish images. Utilizing Python, the `python-telegram-bot` library, and PIL for image manipulation, it offers a quick and interactive way to generate content.

Read the README.md file for more information on how to get and deploy Telegram bots.
"""

import logging
import requests
from telegram import __version__ as TG_VER

try:
	from telegram import __version_info__
except ImportError:
	__version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
	raise RuntimeError(
	    f"This example is not compatible with your current PTB version {TG_VER}. To view the "
	    f"{TG_VER} version of this example, "
	    f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html")

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from PIL import Image, ImageDraw, ImageFont
import os

my_bot_token = ''


def get_concatenated_string(prompt):
	# Define the data payload
	data = {
	    "stream": True,
	    "input": {
	        "top_p": 1,
	        "prompt": prompt,
	        "temperature": 0.5,
	        "system_prompt":
	        "You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.",
	        "max_new_tokens": 500
	    }
	}

	# Define headers
	headers = {
	    "Authorization": "Token r8_KlPo3vNtrJkuFLvOquoBsYEJsImgH0I22XeEz",
	    "Content-Type": "application/json"
	}

	# Send POST request to get prediction
	response = requests.post(
	    "https://api.replicate.com/v1/models/meta/llama-2-70b-chat/predictions",
	    json=data,
	    headers=headers)
	prediction = response.json()

	# Extract stream URL from prediction
	stream_url = prediction.get('urls', {}).get('stream')

	concatenated_string = ""
	if stream_url:
		stream_response = requests.get(stream_url,
		                               headers={
		                                   "Accept": "text/event-stream",
		                                   "Cache-Control": "no-store"
		                               },
		                               stream=True)
		for line in stream_response.iter_lines():
			line = line.decode()
			if line.startswith("data:"):
				# Extract the string after "data:"
				string_data = line.replace("data:", "").strip()
				# Concatenate the string
				concatenated_string += string_data
	else:
		print("Stream URL not found in prediction response")

	return concatenated_string


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Send a message when the command /start is issued."""
	user = update.effective_user
	await update.message.reply_html(
	    rf"Hi {user.mention_html()}!",
	    reply_markup=ForceReply(selective=True),
	)


async def help_command(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Send a message when the command /help is issued."""
	await update.message.reply_text("Help!")


async def stylize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	prompt = update.message.text
	concatenated_string = get_concatenated_string(prompt)
	# Reply with the generated string
	await update.message.reply_text(concatenated_string)


def main() -> None:
	"""Start the bot."""
	# Create the Application and pass it your bot's token.
	application = Application.builder().token(my_bot_token).build()

	# on different commands - answer in Telegram
	application.add_handler(CommandHandler("start", start))
	application.add_handler(CommandHandler("help", help_command))

	# on non command i.e message - echo the message on Telegram
	application.add_handler(
	    MessageHandler(filters.TEXT & ~filters.COMMAND, stylize))

	# Run the bot until the user presses Ctrl-C
	application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
	main()
