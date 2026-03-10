import os
import asyncio
import pandas as pd
import discord
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
TARGET_CHANNEL_ID = 1454963942555386181
CSV_PATH = "wordle_messages.csv"

# If you want Melbourne local time incl. DST, change to "Australia/Melbourne"
AEST = ZoneInfo("Australia/Brisbane")

DELAY_SECONDS = 1.0


def to_aest_date(date_utc_value: str):
	dt = pd.to_datetime(date_utc_value, utc=True, errors="coerce")
	if pd.isna(dt):
		return None
	return dt.to_pydatetime().astimezone(AEST).date()


def format_post(date_utc_value: str, message_text: str) -> str:
	aest_date = to_aest_date(date_utc_value)
	if aest_date is None:
		return ""

	date_str = aest_date.strftime("%d/%m/%Y")
	body = (message_text or "").strip()
	if not body:
		return ""

	return f"**{date_str}**\n{body}\n"


class Client(discord.Client):
	async def on_ready(self):
		channel = self.get_channel(TARGET_CHANNEL_ID) or await self.fetch_channel(TARGET_CHANNEL_ID)

		df = pd.read_csv(CSV_PATH, dtype=str).fillna("")
		if "date_utc" not in df.columns or "message" not in df.columns:
			raise ValueError("CSV must contain columns: date_utc, message")

		# Compute AEST dates
		df["aest_date"] = df["date_utc"].apply(to_aest_date)
		df = df[df["aest_date"].notna()].copy()

		if df.empty:
			print("No valid dates found.")
			await self.close()
			return

		posted = 0
		for _, row in df.iterrows():
			content = format_post(row["date_utc"], row["message"])
			if not content:
				continue

			await channel.send(content)
			posted += 1
			await asyncio.sleep(DELAY_SECONDS)

		await self.close()


def main():
	intents = discord.Intents.default()
	Client(intents=intents).run(TOKEN)


if __name__ == "__main__":
	main()