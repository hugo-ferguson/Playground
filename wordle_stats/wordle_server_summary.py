import pandas as pd


def main():
	users = pd.read_csv("wordle_users.csv", dtype=str).fillna("")
	games = pd.read_csv("wordle_games.csv", dtype=str).fillna("")
	answers = pd.read_json("wordle_answers.json")

	games["report_date"] = pd.to_datetime(games["report_date"]).dt.date
	games["score_text"] = games["score_text"].astype(str)

	# Build "Display Name (username)" label
	def format_player(row) -> str:
		display_name = str(row.get("display_name", "") or "").strip()
		username = str(row.get("username", "") or "").strip()
		user_id = str(row.get("user_id", "") or "").strip()

		if display_name and username:
			return f"{display_name} ({username})"
		if username:
			return username
		return user_id

	users["player"] = users.apply(format_player, axis=1)
	games["player"] = games["user_id"].map(dict(zip(users["user_id"].astype(str), users["player"]))).fillna(games["user_id"])

	# Answers lookup: report_date should map to the NEXT day's Wordle
	answers["wordle_date"] = pd.to_datetime(answers["date"]).dt.date

	# If the Wordle was on 2025-12-21, it should attach to report_date 2025-12-20
	answers["report_date"] = pd.to_datetime(answers["wordle_date"]) - pd.Timedelta(days=1)
	answers["report_date"] = pd.to_datetime(answers["report_date"]).dt.date

	answers = answers[["report_date", "game", "answer"]].rename(columns={
		"game": "wordle_number",
		"answer": "wordle_answer",
	})

	# Difficulty score: treat X as 7 so DNFs make the day harder
	games["difficulty_score"] = pd.to_numeric(games["score_text"].replace({"X": "7"}), errors="coerce")

	daily = games.groupby("report_date").agg(
		players=("user_id", "nunique"),
		avg_difficulty=("difficulty_score", "mean"),
		not_guessed=("score_text", lambda s: int((s == "X").sum())),
	).reset_index()

	# Attach wordle number + answer
	daily = daily.merge(answers, on="report_date", how="left")

	hardest5 = daily.sort_values(
		["avg_difficulty", "players", "not_guessed"],
		ascending=[False, False, False]
	).head(5)

	easiest5 = daily.sort_values(
		["avg_difficulty", "players", "not_guessed"],
		ascending=[True, False, True]
	).head(5)

	# First guesses by day
	first = games[games["score_text"] == "1"].copy()
	first_by_day = (
		first.groupby("report_date")["player"]
		.apply(lambda s: ", ".join(sorted(set(s))))
		.reset_index()
		.rename(columns={"player": "who"})
	)
	first_by_day["count"] = first.groupby("report_date")["user_id"].nunique().values
	first_by_day = first_by_day.merge(answers, on="report_date", how="left").sort_values("report_date")

	rows = []

	def wordle_label(r) -> str:
		num = r.get("wordle_number", "")
		ans = r.get("wordle_answer", "")
		if pd.notna(num) and str(num).strip():
			return f"#{int(num)} {str(ans).upper() if pd.notna(ans) else ''}".strip()
		return ""

	for rank, (_, r) in enumerate(hardest5.iterrows(), start=1):
		rows.append({
			"stat": "hardest_day",
			"rank": rank,
			"wordle": wordle_label(r),
			"value": round(float(r["avg_difficulty"]), 3),
			"players": int(r["players"]),
			"not_guessed": int(r["not_guessed"]),
			"details": "",
		})

	for rank, (_, r) in enumerate(easiest5.iterrows(), start=1):
		rows.append({
			"stat": "easiest_day",
			"rank": rank,
			"wordle": wordle_label(r),
			"value": round(float(r["avg_difficulty"]), 3),
			"players": int(r["players"]),
			"not_guessed": int(r["not_guessed"]),
			"details": "",
		})

	for _, r in first_by_day.iterrows():
		rows.append({
			"stat": "first_guess",
			"rank": "",
			"wordle": wordle_label(r),
			"value": int(r["count"]),
			"players": "",
			"not_guessed": "",
			"details": r["who"],
		})

	out = pd.DataFrame(rows, columns=["stat", "rank", "wordle", "value", "players", "not_guessed", "details"])
	out.to_csv("wordle_server_summary.csv", index=False)
	print(f"Wrote wordle_server_summary.csv (rows={len(out)})")


if __name__ == "__main__":
	main()