import os
import csv
import discord
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])
WORDLE_AUTHOR_ID = int(os.environ["WORDLE_AUTHOR_ID"])

OUT_CSV = "wordle_messages.csv"

def get_text(message: discord.Message) -> str:
	if message.content and message.content.strip():
		return message.content

	if message.embeds:
		for embed in message.embeds:
			if embed.description and embed.description.strip():
				return embed.description

	return ""

def load_seen_ids(csv_path: str) -> set[str]:
	if not os.path.exists(csv_path):
		return set()

	seen = set()
	with open(csv_path, "r", encoding="utf-8", newline="") as f:
		reader = csv.DictReader(f)
		for row in reader:
			if "message_id" in row:
				seen.add(row["message_id"])
	return seen

class Client(discord.Client):
	async def on_ready(self):
		channel = self.get_channel(CHANNEL_ID) or await self.fetch_channel(CHANNEL_ID)

		seen = load_seen_ids(OUT_CSV)
		new_rows = 0

		file_exists = os.path.exists(OUT_CSV)
		with open(OUT_CSV, "a", encoding="utf-8", newline="") as f:
			writer = csv.DictWriter(
				f,
				fieldnames=["date_utc", "message_id", "message"]
			)
			if not file_exists:
				writer.writeheader()

			async for message in channel.history(limit=None, oldest_first=True):
				if not message.author or message.author.id != WORDLE_AUTHOR_ID:
					continue

				message_id = str(message.id)
				if message_id in seen:
					continue

				text = get_text(message)
				if not text:
					continue

				if "results" not in text.lower():
					continue

				writer.writerow({
					"date_utc": message.created_at.isoformat(),
					"message_id": message_id,
					"message": text.replace("\r\n", "\n").replace("\r", "\n")
				})
				new_rows += 1

		print(f"Wrote {new_rows} new rows to {OUT_CSV}")
		await self.close()

def main():
	intents = discord.Intents.default()
	intents.guilds = True
	intents.messages = True
	intents.message_content = True

	Client(intents=intents).run(os.environ["DISCORD_BOT_TOKEN"])

if __name__ == "__main__":
	main()