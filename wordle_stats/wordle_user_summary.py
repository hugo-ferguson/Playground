import re
from datetime import timedelta
import pandas as pd

SCORE_BLOCKS = re.compile(r"([0-6X])/6:\s*(.+?)(?=(?:\s+[0-6X]/6:)|$)")
MENTION_ID = re.compile(r"<@!?(\d+)>")

def norm(text: str) -> str:
	return re.sub(r"\s+", " ", (text or "").strip()).casefold()

OVERRIDES = {norm(name): "945209223011258448" for name in [
	"/me Vacuum Sounds",
	"Big Gawny",
	"Nightmare Freddy",
]}
OVERRIDES = {norm(name): "266535613862248449" for name in [
	"رايدن",
	r"young paper chaser \(agp\)",
	"Fenomist",
	"Free again to do as I please",
	"Porno"
]}
OVERRIDES[norm("I wuv bwuewock")] = "283430810290487296"
OVERRIDES[norm("Beans For Joel")] = "154468120877072384"

IGNORE = {
	norm("Group Leader")
}

def name_to_ids(users: pd.DataFrame) -> dict[str, set[str]]:
	m = {}
	for _, r in users.iterrows():
		uid = str(r.get("user_id", "") or "").strip()
		if not uid:
			continue
		for col in ("display_name", "global_name", "username"):
			key = norm(str(r.get(col, "") or ""))
			if key:
				m.setdefault(key, set()).add(uid)
	return m

def streak(dates: pd.Series) -> int:
	ds = sorted(pd.to_datetime(dates).dt.date.unique())
	if not ds:
		return 0
	best = run = 1
	for i in range(1, len(ds)):
		run = run + 1 if (ds[i] - ds[i - 1]).days == 1 else 1
		best = max(best, run)
	return best

def main():
	users = pd.read_csv("wordle_users.csv", dtype=str).fillna("")
	users = users[users["user_id"].astype(str).str.fullmatch(r"\d+")]\
		.drop_duplicates("user_id", keep="first")

	messages = pd.read_csv("wordle_messages.csv", dtype={"message_id": str}).fillna("")

	lookup = name_to_ids(users)

	rows = []
	for _, r in messages.iterrows():
		msg = str(r.get("message", "") or "")
		if not msg:
			continue

		post_dt = pd.to_datetime(r.get("date_utc", ""), utc=True, errors="coerce")
		if pd.isna(post_dt):
			continue

		day = post_dt.date() - timedelta(days=1)
		text = re.sub(r"\s+", " ", msg.strip())

		for score_text, body in SCORE_BLOCKS.findall(text):
			# IDs
			for uid in MENTION_ID.findall(body):
				rows.append((day, str(uid), score_text))

			# @names (split-based; safe for names with spaces)
			clean = MENTION_ID.sub("", body)
			for part in clean.split("@")[1:]:
				name = part.strip().strip(" ,;|")
				if not name:
					continue
				key = norm(name)
				if key in IGNORE:
					continue

				uid = OVERRIDES.get(key)
				if not uid:
					cands = sorted(lookup.get(key, set()))
					uid = cands[0] if len(cands) == 1 else None

				if uid:
					rows.append((day, str(uid), score_text))

	games = pd.DataFrame(rows, columns=["report_date", "user_id", "score_text"])\
		.drop_duplicates(["report_date", "user_id"], keep="last")

	games["score_num"] = pd.to_numeric(games["score_text"].replace({"X": "7"}), errors="coerce")
	games["played"] = 1
	games.to_csv("wordle_games.csv", index=False)

	total_days = int(pd.to_datetime(games["report_date"]).dt.date.nunique()) if len(games) else 0

	agg = games.groupby("user_id").agg(
		total_games=("played", "sum"),
		average_score=("score_num", "mean"),
	).reset_index()

	# Guess distribution
	dist = games.groupby(["user_id", "score_text"])["played"].sum().unstack(fill_value=0)
	for key in ["1", "2", "3", "4", "5", "6", "X"]:
		if key not in dist.columns:
			dist[key] = 0
	dist = dist[["1", "2", "3", "4", "5", "6", "X"]].reset_index().rename(columns={
		"1": "first_guesses",
		"2": "second_guesses",
		"3": "third_guesses",
		"4": "fourth_guesses",
		"5": "fifth_guesses",
		"6": "sixth_guesses",
		"X": "not_guessed",
	})
	agg = agg.merge(dist, on="user_id", how="left").fillna(0)

	# Streak + percent played
	agg["longest_streak"] = games.groupby("user_id")["report_date"].apply(streak).values
	agg["%_games_played"] = agg["total_games"] / total_days if total_days else 0.0

	out = users[["user_id", "username", "display_name"]].merge(agg, on="user_id", how="left")

	out["total_games"] = out["total_games"].fillna(0).astype(int)
	out["longest_streak"] = out["longest_streak"].fillna(0).astype(int)
	for c in ["first_guesses","second_guesses","third_guesses","fourth_guesses","fifth_guesses","sixth_guesses","not_guessed"]:
		out[c] = out[c].fillna(0).astype(int)

	out.sort_values(["total_games", "average_score"], ascending=[False, True])\
		.to_csv("wordle_user_summary.csv", index=False)

	print(f"Wrote wordle_user_summary.csv (days_observed={total_days}, players={len(out)})")

if __name__ == "__main__":
	main()