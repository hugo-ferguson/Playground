import os
import re
import csv
import discord
from dotenv import load_dotenv

load_dotenv()

CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])
WORDLE_AUTHOR_ID = int(os.environ["WORDLE_AUTHOR_ID"])

MUST_CONTAIN = "results"
OUT_CSV = "wordle_users.csv"

MENTION_ID_PATTERN = re.compile(r"<@!?(\d+)>")

def get_text(message: discord.Message) -> str:
	if message.content and message.content.strip():
		return message.content

	if message.embeds:
		for embed in message.embeds:
			if embed.description and embed.description.strip():
				return embed.description

	return ""

class Client(discord.Client):
	async def on_ready(self):
		channel = self.get_channel(CHANNEL_ID) or await self.fetch_channel(CHANNEL_ID)

		# Works for normal channels + threads.
		guild = getattr(channel, "guild", None)

		mentioned_user_ids: set[int] = set()

		async for message in channel.history(limit=None, oldest_first=True):
			if not message.author or message.author.id != WORDLE_AUTHOR_ID:
				continue

			text = get_text(message)
			if not text:
				continue

			if MUST_CONTAIN.lower() not in text.lower():
				continue

			for match in MENTION_ID_PATTERN.findall(text):
				mentioned_user_ids.add(int(match))

		print(f"Found {len(mentioned_user_ids)} unique mentioned user IDs")

		rows = []
		for user_id in sorted(mentioned_user_ids):
			member = None
			user = None

			# Try to resolve as a guild member first (gives display_name).
			if guild is not None:
				member = guild.get_member(user_id)
				if member is None:
					try:
						member = await guild.fetch_member(user_id)
					except discord.NotFound:
						member = None
					except discord.Forbidden:
						member = None

			if member is not None:
				user = member
			else:
				# Fallback: fetch user globally (works even if they left the server).
				try:
					user = await self.fetch_user(user_id)
				except discord.NotFound:
					user = None

			if user is None:
				rows.append({
					"user_id": str(user_id),
					"username": "",
					"global_name": "",
					"display_name": "",
				})
				continue

			rows.append({
				"user_id": str(user_id),
				"username": getattr(user, "name", "") or "",
				"global_name": getattr(user, "global_name", "") or "",
				"display_name": getattr(user, "display_name", "") or "",
			})

		with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
			writer = csv.DictWriter(f, fieldnames=["user_id", "username", "global_name", "display_name"])
			writer.writeheader()
			writer.writerows(rows)

		print(f"Wrote {len(rows)} rows to {OUT_CSV}")
		await self.close()

def main():
	intents = discord.Intents.default()
	intents.guilds = True
	intents.messages = True
	intents.message_content = True

	Client(intents=intents).run(os.environ["DISCORD_BOT_TOKEN"])

if __name__ == "__main__":
	main()