import csv

def process_results(file_path):
    results = {}
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row:
                name = row[0]
                scores = list(map(float, row[1:]))
                results[name] = scores
    return results

def format_record(wins, total_weeks):
    losses = total_weeks - wins
    return f"{wins}-{losses}"

def find_best_and_worst_records_for_team(teams, team_name):
    first_team_scores = teams[team_name]
    all_teams = list(teams.keys())
    all_teams.remove(team_name)
    num_weeks = len(first_team_scores)

    # Identify forced wins and forced losses
    forced_wins = [False] * num_weeks
    forced_losses = [False] * num_weeks

    for week in range(num_weeks):
        weekly_scores = [teams[team][week] for team in teams]
        if first_team_scores[week] == max(weekly_scores):
            forced_wins[week] = True
        elif first_team_scores[week] == min(weekly_scores):
            forced_losses[week] = True

    # Helper function to get opponent score for a given week
    def get_opponent_score(opponent, week):
        return teams[opponent][week]

    # BEST RECORD: Build a schedule maximizing wins (without repeats)
    best_schedule = []
    best_record = 0
    available_opponents = all_teams.copy()

    for week in range(num_weeks - 1):  # Process weeks 1 to 13 (not week 14 yet)
        if forced_wins[week]:
            opponent = available_opponents.pop(0)  # Arbitrary choice for forced win
        else:
            beatable_opponents = [team for team in available_opponents if first_team_scores[week] > get_opponent_score(team, week)]
            if beatable_opponents:
                opponent = beatable_opponents[0]  # Arbitrary choice among beatable opponents
            else:
                opponent = available_opponents[0]  # Fallback if no beatable opponents

        best_schedule.append(opponent)
        if opponent in available_opponents:
            available_opponents.remove(opponent)

        if first_team_scores[week] > get_opponent_score(opponent, week):
            best_record += 1

    # Determine Week 14 opponent
    week_14_opponent = best_schedule[0]
    if first_team_scores[num_weeks - 1] > get_opponent_score(week_14_opponent, num_weeks - 1):
        best_record += 1

    # Check for swappable weeks to improve best record
    for i in range(len(best_schedule)):
        for j in range(i + 1, len(best_schedule)):
            temp_schedule = best_schedule[:]
            temp_schedule[i], temp_schedule[j] = temp_schedule[j], temp_schedule[i]
            temp_record = sum([1 for k in range(num_weeks - 1) if first_team_scores[k] > get_opponent_score(temp_schedule[k], k)])
            if temp_record + (1 if first_team_scores[num_weeks - 1] > get_opponent_score(temp_schedule[0], num_weeks - 1) else 0) > best_record:
                best_schedule = temp_schedule
                best_record = temp_record + (1 if first_team_scores[num_weeks - 1] > get_opponent_score(temp_schedule[0], num_weeks - 1) else 0)

    # WORST RECORD: Build a schedule minimizing wins (without repeats)
    worst_schedule = []
    worst_record = 0
    available_opponents = all_teams.copy()

    for week in range(num_weeks - 1):  # Process weeks 1 to 13 (not week 14 yet)
        if forced_losses[week]:
            opponent = available_opponents.pop(0)  # Arbitrary choice for forced loss
        else:
            stronger_opponents = [team for team in available_opponents if first_team_scores[week] <= get_opponent_score(team, week)]
            if stronger_opponents:
                opponent = stronger_opponents[0]  # Arbitrary choice among stronger opponents
            else:
                opponent = available_opponents[0]  # Fallback if no stronger opponents

        worst_schedule.append(opponent)
        if opponent in available_opponents:
            available_opponents.remove(opponent)

        if first_team_scores[week] > get_opponent_score(opponent, week):
            worst_record += 1

    # Determine Week 14 opponent
    week_14_opponent_worst = worst_schedule[0]
    if first_team_scores[num_weeks - 1] > get_opponent_score(week_14_opponent_worst, num_weeks - 1):
        worst_record += 1

    # Check for swappable weeks to worsen worst record
    for i in range(len(worst_schedule)):
        for j in range(i + 1, len(worst_schedule)):
            temp_schedule = worst_schedule[:]
            temp_schedule[i], temp_schedule[j] = temp_schedule[j], temp_schedule[i]
            temp_record = sum([1 for k in range(num_weeks - 1) if first_team_scores[k] > get_opponent_score(temp_schedule[k], k)])
            if temp_record + (1 if first_team_scores[num_weeks - 1] > get_opponent_score(temp_schedule[0], num_weeks - 1) else 0) < worst_record:
                worst_schedule = temp_schedule
                worst_record = temp_record + (1 if first_team_scores[num_weeks - 1] > get_opponent_score(temp_schedule[0], num_weeks - 1) else 0)

    # Format records as W-L
    best_record_str = format_record(best_record, num_weeks)
    worst_record_str = format_record(worst_record, num_weeks)

    return {
        "best_record": best_record_str,
        "best_schedule": best_schedule,
        "best_week_14_opponent": week_14_opponent,
        "worst_record": worst_record_str,
        "worst_schedule": worst_schedule,
        "worst_week_14_opponent": week_14_opponent_worst,
    }

def print_schedules(schedule, wins, title, first_team_scores, teams, week_14_opponent):
    print(f"{title} Schedule (Total Wins: {wins}):")
    for week, opponent in enumerate(schedule, start=1):
        result = "Win against" if first_team_scores[week-1] > teams[opponent][week-1] else "Loss to"
        print(f"Week {week}: {first_team_scores[week-1]} vs {teams[opponent][week-1]} ({result} {opponent})")
    week_14_result = "Win against" if first_team_scores[13] > teams[week_14_opponent][13] else "Loss to"
    print(f"Week 14: {first_team_scores[13]} vs {teams[week_14_opponent][13]} ({week_14_result} {week_14_opponent})")

# Process CSV and get team data
teams = process_results("results.csv")

# Iterate over each team to find and print best and worst records
for team in teams.keys():
    print(f"Calculating for {team}...")
    output = find_best_and_worst_records_for_team(teams, team)
    print()
    print_schedules(output["best_schedule"], output["best_record"], f"Best for {team}", teams[team], teams, output["best_week_14_opponent"])
    print()
    print_schedules(output["worst_schedule"], output["worst_record"], f"Worst for {team}", teams[team], teams, output["worst_week_14_opponent"])
    print()
