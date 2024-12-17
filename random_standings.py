import csv
import random
from collections import defaultdict, Counter


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


def generate_random_schedule(teams):
    num_weeks = 13
    num_teams = len(teams)
    schedule = {team: [] for team in teams}

    # Generate matchups for each week
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

    # Week 14: Repeat Week 1 matchups
    for team in teams:
        schedule[team].append(schedule[team][0])

    return schedule


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
    total_standings = {team: {'wins': 0, 'losses': 0} for team in teams}
    win_records = defaultdict(list)

    for _ in range(num_simulations):
        random_schedule = generate_random_schedule(teams)
        standings = calculate_standings(teams, random_schedule)
        for team in standings:
            total_standings[team]['wins'] += standings[team]['wins']
            total_standings[team]['losses'] += standings[team]['losses']
            win_records[team].append(standings[team]['wins'])

    # Average the standings
    avg_standings = {team: {'avg_wins': total_standings[team]['wins'] / num_simulations,
                            'avg_losses': total_standings[team]['losses'] / num_simulations,
                            'min_wins': min(win_records[team]),
                            'max_wins': max(win_records[team]),
                            'mode_wins': Counter(win_records[team]).most_common(1)[0][0]}
                     for team in total_standings}

    return avg_standings


def print_avg_standings(avg_standings):
    sorted_avg_standings = sorted(avg_standings.items(), key=lambda x: x[1]['avg_wins'], reverse=True)
    for team, record in sorted_avg_standings:
        print(f"{team}: {record['avg_wins']:.2f} avg wins, {record['avg_losses']:.2f} avg losses")
        print(f"Min wins: {record['min_wins']}, Max wins: {record['max_wins']}, Mode wins: {record['mode_wins']}")


# Process CSV and get team data
teams = process_results("results.csv")

# Run simulations
num_simulations = 10000
avg_standings = run_simulations(teams, num_simulations)

# Print average standings
print_avg_standings(avg_standings)
