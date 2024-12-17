import csv
import random
from collections import defaultdict, Counter

def process_results(file_path):
    results = {}
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row:
                name = row[0].strip()
                scores = list(map(float, row[1:]))
                results[name] = scores
    return results

def read_real_schedule(file_path):
    schedule = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)  # Skip header row
        for row in csv_reader:
            week_schedule = [(row[i].strip(), row[i + 1].strip()) for i in range(1, len(row), 2)]
            schedule.append(week_schedule)
    return schedule

def verify_team_names(teams, schedule):
    all_teams_in_schedule = set()
    for week in schedule:
        for team1, team2 in week:
            all_teams_in_schedule.add(team1)
            all_teams_in_schedule.add(team2)
    missing_teams = all_teams_in_schedule - set(teams.keys())
    if missing_teams:
        print("Warning: The following teams are in the schedule but not in the results data:", missing_teams)
    return missing_teams

def calculate_actual_standings(teams, schedule):
    standings = {team: {'wins': 0, 'losses': 0} for team in teams}
    num_weeks = len(schedule)

    for week in range(num_weeks):
        for team1, team2 in schedule[week]:
            if team1 in teams and team2 in teams:  # Ensure both teams exist in the results data
                if teams[team1][week] > teams[team2][week]:
                    standings[team1]['wins'] += 1
                    standings[team2]['losses'] += 1
                else:
                    standings[team1]['losses'] += 1
                    standings[team2]['wins'] += 1

    return standings

def calculate_standings(teams, schedule):
    standings = {team: {'wins': 0, 'losses': 0} for team in teams}
    num_weeks = 14

    for week in range(num_weeks):
        weekly_matchups = set()
        for team in teams:
            opponent = schedule[team][week]
            if (team, opponent) not in weekly_matchups and (opponent, team) not in weekly_matchups:
                if teams[team][week] > teams[opponent][week]:
                    standings[team]['wins'] += 1
                    standings[opponent]['losses'] += 1
                else:
                    standings[team]['losses'] += 1
                    standings[opponent]['wins'] += 1
                weekly_matchups.add((team, opponent))

    return standings

def run_simulations(teams, num_simulations):
    win_records = defaultdict(list)

    for _ in range(num_simulations):
        random_schedule = generate_random_schedule(teams)
        standings = calculate_standings(teams, random_schedule)
        for team in standings:
            win_records[team].append(standings[team]['wins'])

    win_probabilities = {
        team: {wins: count / num_simulations * 100 for wins, count in Counter(win_records[team]).items()}
        for team in win_records
    }

    return win_probabilities

def identify_lucky_teams(teams, schedule):
    lucky_results = []
    num_weeks = len(schedule)
    lucky_counts = defaultdict(lambda: {'Lucky': 0, 'Unlucky': 0})

    for week in range(num_weeks):
        week_result = {'week': week + 1, 'teams': []}
        weekly_scores = {team: teams[team][week] for team in teams}
        for team, score in weekly_scores.items():
            wins_against_league = sum(score > opponent_score for opponent, opponent_score in weekly_scores.items() if opponent != team)
            actual_wins = 0
            actual_losses = 0
            for team1, team2 in schedule[week]:
                if team == team1 or team == team2:
                    if teams[team1][week] > teams[team2][week]:
                        actual_wins += 1 if team == team1 else 0
                        actual_losses += 1 if team == team2 else 0
                    else:
                        actual_wins += 1 if team == team2 else 0
                        actual_losses += 1 if team == team1 else 0
            expected_wins = wins_against_league / (len(teams) - 1)
            luck = 'Lucky' if expected_wins <= 0.33 and actual_wins > 0 else 'Unlucky' if expected_wins >= 0.67 and actual_losses > 0 else 'Neutral'
            if luck in ['Lucky', 'Unlucky']:
                lucky_counts[team][luck] += 1
            week_result['teams'].append({
                'team': team,
                'score': score,
                'wins_against_league': wins_against_league,
                'expected_wins': expected_wins,
                'actual_wins': actual_wins,
                'actual_losses': actual_losses,
                'luck': luck
            })
        lucky_results.append(week_result)

    return lucky_results, lucky_counts

def print_lucky_results(lucky_results):
    for week in lucky_results:
        print(f"Week {week['week']}:")
        for result in week['teams']:
            print(
                f"  {result['team']} (score: {result['score']}, actual wins: {result['actual_wins']}, expected wins: {result['expected_wins']:.2f}, actual losses: {result['actual_losses']}) - {result['luck']}")

def print_lucky_counts(lucky_counts):
    print("\nSummary of Lucky Wins and Unlucky Losses:")
    for team, counts in lucky_counts.items():
        print(f"{team}: {counts['Lucky']} Lucky wins, {counts['Unlucky']} Unlucky losses")

def generate_random_schedule(teams):
    num_weeks = 13
    num_teams = len(teams)
    schedule = {team: [] for team in teams}

    for week in range(num_weeks):
        available_teams = list(teams.keys())
        random.shuffle(available_teams)
        week_matchups = []
        while available_teams:
            team1 = available_teams.pop()
            team2 = available_teams.pop()
            week_matchups.append((team1, team2))

        for team1, team2 in week_matchups:
            schedule[team1].append(team2)
            schedule[team2].append(team1)

    for team in teams:
        schedule[team].append(schedule[team][0])

    return schedule

def calculate_lucky_sums(lucky_results):
    luck_sums = defaultdict(lambda: {'lucky': 0, 'unlucky': 0})

    for week in lucky_results:
        for result in week['teams']:
            if result['luck'] == 'Lucky':
                luck_sums[result['team']]['lucky'] += 1
            elif result['luck'] == 'Unlucky':
                luck_sums[result['team']]['unlucky'] += 1

    return luck_sums

def print_lucky_sums(luck_sums):
    print("\nSum of Lucky Wins and Unlucky Losses for Each Team:")
    for team, luck in luck_sums.items():
        print(f"{team}: {luck['lucky']} Lucky Wins, {luck['unlucky']} Unlucky Losses")

# File paths
results_file = 'results.csv'
schedule_file = 'real_schedule.csv'

# Process CSV and get team data
teams = process_results(results_file)

# Read the real schedule from the CSV file
real_schedule = read_real_schedule(schedule_file)

# Verify team names
missing_teams = verify_team_names(teams, real_schedule)
if missing_teams:
    raise ValueError("Team names mismatch detected. Please check the results and schedule data.")

# Calculate actual standings based on the real schedule
actual_standings = calculate_actual_standings(teams, real_schedule)

# Identify lucky teams based on their league-wide performance
lucky_results, lucky_counts = identify_lucky_teams(teams, real_schedule)

# Print the lucky results
print_lucky_results(lucky_results)

# Print the summary of lucky wins and unlucky losses
print_lucky_counts(lucky_counts)

# Calculate the sum of lucky wins and unlucky losses for each team
luck_sums = calculate_lucky_sums(lucky_results)

# Print the sum of lucky wins and unlucky losses for each team
print_lucky_sums(luck_sums)
