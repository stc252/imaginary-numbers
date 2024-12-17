import csv

def process_results():
    results = {}

    with open("results.csv",mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row:
                name = row[0]
                scores = list(map(float, row[1:]))
                results[name] = scores
    return results

# Example dictionary with team names as keys and lists of weekly scores as values
teams = process_results()
# Function to compare teams' scores week by week
def compare_teams(teams):
    number_of_weeks = len(next(iter(teams.values())))
    results = {team: {'wins': 0, 'losses': 0} for team in teams}

    for week in range(number_of_weeks):
        weekly_scores = {team: scores[week] for team, scores in teams.items()}

        for team1 in teams:
            for team2 in teams:
                if team1 != team2:
                    if weekly_scores[team1] > weekly_scores[team2]:
                        results[team1]['wins'] += 1
                        results[team2]['losses'] += 1
                    elif weekly_scores[team1] < weekly_scores[team2]:
                        results[team1]['losses'] += 1
                        results[team2]['wins'] += 1

    return results

# Function to print the results sorted by wins
def print_sorted_results(results):
    sorted_results = sorted(results.items(), key=lambda item: item[1]['wins'], reverse=True)
    for team, record in sorted_results:
        print(f"{team}: {record['wins']} wins, {record['losses']} losses")

# Compare teams and get the results
results = compare_teams(teams)

# Print the sorted results
print_sorted_results(results)

def format_record(wins, total_weeks):
    losses = total_weeks - wins
    return f"{wins}-{losses}"

def find_best_and_worst_records(teams):
    first_team_name = list(teams.keys())[0]
    first_team_scores = teams[first_team_name]
    all_teams = list(teams.keys())
    all_teams.remove(first_team_name)
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

        # Ensure the opponent is in the list before removing it
        if opponent in available_opponents:
            available_opponents.remove(opponent)

        if first_team_scores[week] > get_opponent_score(opponent, week):
            best_record += 1

    # Week 14 handling: Week 14 opponent must be the same as Week 1 opponent
    week_14_opponent = best_schedule[0]  # Week 14 opponent is the same as Week 1 opponent
    best_schedule.append(week_14_opponent)
    if first_team_scores[num_weeks - 1] > get_opponent_score(week_14_opponent, num_weeks - 1):
        best_record += 1

    # WORST RECORD: Build a schedule minimizing wins (without repeats)
    worst_schedule = []
    worst_record = 0
    available_opponents = all_teams.copy()

    for week in range(num_weeks - 1):  # Process weeks 1 to 13 (not week 14 yet)
        if forced_wins[week]:
            opponent = available_opponents.pop(0)  # Arbitrary choice for forced win
        else:
            stronger_opponents = [team for team in available_opponents if first_team_scores[week] <= get_opponent_score(team, week)]
            if stronger_opponents:
                opponent = stronger_opponents[0]  # Arbitrary choice among stronger opponents
            else:
                opponent = available_opponents[0]  # Fallback if no stronger opponents

        worst_schedule.append(opponent)

        # Ensure the opponent is in the list before removing it
        if opponent in available_opponents:
            available_opponents.remove(opponent)

        if first_team_scores[week] > get_opponent_score(opponent, week):
            worst_record += 1

    # Week 14 handling: Week 14 opponent must be the same as Week 1 opponent
    week_14_opponent = worst_schedule[0]  # Week 14 opponent is the same as Week 1 opponent
    worst_schedule.append(week_14_opponent)
    if first_team_scores[num_weeks - 1] > get_opponent_score(week_14_opponent, num_weeks - 1):
        worst_record += 1

    # Format records as W-L
    best_record_str = format_record(best_record, num_weeks)
    worst_record_str = format_record(worst_record, num_weeks)

    return {
        "best_record": best_record_str,
        "best_schedule": best_schedule,
        "worst_record": worst_record_str,
        "worst_schedule": worst_schedule,
    }

# Example usage

output = find_best_and_worst_records(teams)
print("Best Record:", output["best_record"])
print("Best Schedule:", output["best_schedule"])
print("Worst Record:", output["worst_record"])
print("Worst Schedule:", output["worst_schedule"])


def verify_worst_schedule(teams, first_team_name, worst_schedule):
    first_team_scores = teams[first_team_name]
    num_weeks = len(first_team_scores)
    wins = 0
    print("Verifying Worst Schedule:")

    for week in range(num_weeks - 1):  # Exclude week 14 for verification
        opponent = worst_schedule[week]
        opponent_score = teams[opponent][week]
        team_score = first_team_scores[week]

        # Check if the team won or lost this week
        if team_score > opponent_score:
            result = "Win"
            wins += 1
        else:
            result = "Loss"

        print(f"Week {week + 1}: {first_team_name} ({team_score}) vs {opponent} ({opponent_score}) -> {result}")

    # Week 14 handling
    week_14_opponent = worst_schedule[0]  # Week 14 opponent must be same as Week 1 opponent
    week_14_score = first_team_scores[num_weeks - 1]
    week_14_opponent_score = teams[week_14_opponent][num_weeks - 1]

    if week_14_score > week_14_opponent_score:
        result = "Win"
        wins += 1
    else:
        result = "Loss"

    print(f"Week 14: {first_team_name} ({week_14_score}) vs {week_14_opponent} ({week_14_opponent_score}) -> {result}")

    # Return the final wins count
    return wins


# Example usage:
output = find_best_and_worst_records(teams)
worst_schedule = output["worst_schedule"]
first_team_name = list(teams.keys())[0]

# Verify the worst schedule by checking the results week by week
wins = verify_worst_schedule(teams, first_team_name, worst_schedule)
print(f"Total Wins in Worst Schedule: {wins}")
