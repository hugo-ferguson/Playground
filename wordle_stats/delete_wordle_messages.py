import os
import asyncio
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])
WORDLE_AUTHOR_ID = int(os.environ["WORDLE_AUTHOR_ID"])

MUST_CONTAIN = ""			# safety filter; set "" to disable
DRY_RUN = False				# True = "fake delete": print content for newest 50 matches, delete nothing
PREVIEW_LIMIT = 50			# how many matches to "fake delete" in DRY_RUN
MAX_DELETE = 0				# 0 = unlimited (only used when DRY_RUN=False)
DELAY_SECONDS = 0.6			# only used when DRY_RUN=False
PRINT_EMBEDS = True
TRUNCATE_CHARS = 0			# 0 = no truncation; otherwise truncate printed content to this many chars


def get_text(message: discord.Message) -> str:
	parts: list[str] = []

	if message.content and message.content.strip():
		parts.append(message.content.strip())

	if PRINT_EMBEDS:
		for embed in message.embeds or []:
			if embed.title and embed.title.strip():
				parts.append(embed.title.strip())
			if embed.description and embed.description.strip():
				parts.append(embed.description.strip())

	return "\n".join(parts).strip()


def maybe_truncate(text: str) -> str:
	if TRUNCATE_CHARS and len(text) > TRUNCATE_CHARS:
		return text[:TRUNCATE_CHARS] + "…"
	return text


class Client(discord.Client):
	async def on_ready(self):
		channel = self.get_channel(CHANNEL_ID) or await self.fetch_channel(CHANNEL_ID)

		print(f"Logged in as: {self.user}")
		print(f"Channel ID: {CHANNEL_ID}")
		print(f"Target author ID: {WORDLE_AUTHOR_ID}")
		print(f"MUST_CONTAIN={MUST_CONTAIN!r} DRY_RUN={DRY_RUN}")

		scanned = 0
		matched = 0
		deleted = 0

		# newest -> oldest
		async for msg in channel.history(limit=None, oldest_first=False):
			scanned += 1

			if not msg.author or msg.author.id != WORDLE_AUTHOR_ID:
				continue

			text = get_text(msg)
			if not text:
				continue

			if MUST_CONTAIN and MUST_CONTAIN.casefold() not in text.casefold():
				continue

			matched += 1

			if DRY_RUN:
				print("─" * 80)
				print(f"[DRY] Would delete message id={msg.id} at {msg.created_at.isoformat()}")
				print(maybe_truncate(text))

				if matched >= PREVIEW_LIMIT:
					print("─" * 80)
					print(f"DRY_RUN=True -> previewed {PREVIEW_LIMIT} newest matching messages. No deletions performed.")
					break
				continue

			# REAL DELETE MODE
			try:
				await msg.delete()
				deleted += 1
				print(f"Deleted: {msg.created_at.isoformat()} id={msg.id}")

			except discord.Forbidden:
				print("ERROR: Forbidden (bot lacks Manage Messages in this channel).")
				break
			except discord.NotFound:
				continue
			except discord.HTTPException as e:
				print(f"HTTPException: {e} (sleep 2s)")
				await asyncio.sleep(2.0)

			if MAX_DELETE and deleted >= MAX_DELETE:
				print("Reached MAX_DELETE, stopping.")
				break

			await asyncio.sleep(DELAY_SECONDS)

		print(f"Done. scanned={scanned} matched={matched} deleted={deleted} (dry_run={DRY_RUN})")
		await self.close()


def main():
	intents = discord.Intents.default()
	intents.message_content = True
	Client(intents=intents).run(TOKEN)


if __name__ == "__main__":
	main()