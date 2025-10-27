import csv
import random
from collections import defaultdict, Counter
import json
import argparse

def read_scores(filename, num_weeks):
    """
    Read team scores from CSV file.
    Expected format: teamname,score1,score2,score3,score4,score5,score6,score7
    """
    teams = {}
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            team_name = row[0]
            scores = [float(score) for score in row[1:num_weeks + 1]]
            teams[team_name] = scores
    return teams

def generate_random_schedule(team_names, num_weeks=7):
    """
    Generate a random schedule where each team plays once per week.
    Returns a list of weeks, where each week is a list of matchups (tuples).
    """
    schedule = []
    for week in range(num_weeks):
        teams_copy = team_names.copy()
        random.shuffle(teams_copy)
        
        # Pair teams into matchups
        week_matchups = []
        for i in range(0, len(teams_copy), 2):
            week_matchups.append((teams_copy[i], teams_copy[i+1]))
        schedule.append(week_matchups)
    
    return schedule

def simulate_season(teams_scores, schedule):
    """
    Simulate a single season given team scores and a schedule.
    Returns a dictionary of team records {team_name: (wins, losses)}
    """
    records = {team: [0, 0] for team in teams_scores.keys()}  # [wins, losses]
    
    for week_num, week_matchups in enumerate(schedule):
        for team1, team2 in week_matchups:
            score1 = teams_scores[team1][week_num]
            score2 = teams_scores[team2][week_num]
            
            if score1 > score2:
                records[team1][0] += 1  # team1 wins
                records[team2][1] += 1  # team2 loses
            else:
                records[team2][0] += 1  # team2 wins
                records[team1][1] += 1  # team1 loses
    
    # Convert to tuples (wins, losses)
    return {team: tuple(record) for team, record in records.items()}

def run_simulations(teams_scores, num_weeks, num_simulations=100000):
    """
    Run Monte Carlo simulations and track all possible records for each team.
    Also tracks worst losses and closest wins.
    """
    team_names = list(teams_scores.keys())
    
    # Store all possible records for each team
    team_record_counts = {team: Counter() for team in team_names}
    
    # Track worst losses and closest wins for each team
    worst_losses = {team: {'margin': 0, 'opponent': None, 'week': None, 'team_score': None, 'opp_score': None} 
                    for team in team_names}
    closest_wins = {team: {'margin': float('inf'), 'opponent': None, 'week': None, 'team_score': None, 'opp_score': None} 
                    for team in team_names}
    
    print(f"Running {num_simulations:,} simulations...")
    print(f"Teams: {len(team_names)}")
    print(f"Weeks: {num_weeks}")
    print()
    
    for sim in range(num_simulations):
        if (sim + 1) % 100000 == 0:
            print(f"Completed {sim + 1:,} simulations...")
        
        # Generate random schedule
        schedule = generate_random_schedule(team_names, num_weeks)
        
        # Simulate the season and track matchup details
        season_results = simulate_season(teams_scores, schedule)
        
        # Track records
        for team, record in season_results.items():
            team_record_counts[team][record] += 1
        
        # Analyze each matchup for worst losses and closest wins
        for week_num, week_matchups in enumerate(schedule):
            for team1, team2 in week_matchups:
                score1 = teams_scores[team1][week_num]
                score2 = teams_scores[team2][week_num]
                margin = abs(score1 - score2)
                
                if score1 > score2:
                    # team1 wins
                    if margin < closest_wins[team1]['margin']:
                        closest_wins[team1] = {
                            'margin': margin,
                            'opponent': team2,
                            'week': week_num + 1,
                            'team_score': score1,
                            'opp_score': score2
                        }
                    # team2 loses
                    if margin > worst_losses[team2]['margin']:
                        worst_losses[team2] = {
                            'margin': margin,
                            'opponent': team1,
                            'week': week_num + 1,
                            'team_score': score2,
                            'opp_score': score1
                        }
                else:
                    # team2 wins
                    if margin < closest_wins[team2]['margin']:
                        closest_wins[team2] = {
                            'margin': margin,
                            'opponent': team1,
                            'week': week_num + 1,
                            'team_score': score2,
                            'opp_score': score1
                        }
                    # team1 loses
                    if margin > worst_losses[team1]['margin']:
                        worst_losses[team1] = {
                            'margin': margin,
                            'opponent': team2,
                            'week': week_num + 1,
                            'team_score': score1,
                            'opp_score': score2
                        }
    
    print(f"\nSimulation complete!")
    return team_record_counts, worst_losses, closest_wins

def analyze_results(team_record_counts, num_simulations):
    """
    Analyze and display the results.
    """
    print("\n" + "="*80)
    print("FANTASY FOOTBALL SIMULATION RESULTS")
    print("="*80)
    
    for team in sorted(team_record_counts.keys()):
        print(f"\n{team}:")
        print("-" * 60)
        
        records = team_record_counts[team]
        
        # Sort by wins (descending), then by losses (ascending)
        sorted_records = sorted(records.items(), 
                               key=lambda x: (-x[0][0], x[0][1]))
        
        # Calculate statistics
        total_wins = sum(wins * count for (wins, losses), count in records.items())
        avg_wins = total_wins / num_simulations
        
        print(f"Average wins: {avg_wins:.2f}")
        print(f"\nRecord Distribution:")
        print(f"{'Record':<15} {'Count':<15} {'Probability':<15}")
        
        for (wins, losses), count in sorted_records[:10]:  # Top 10 most common
            probability = count / num_simulations * 100
            print(f"{wins}-{losses:<13} {count:<15,} {probability:>6.2f}%")
        
        if len(sorted_records) > 10:
            print(f"... and {len(sorted_records) - 10} other possible records")
    
    # Summary statistics
    print("\n" + "="*80)
    print("TEAM RANKINGS BY AVERAGE WINS")
    print("="*80)
    
    team_avg_wins = []
    for team, records in team_record_counts.items():
        total_wins = sum(wins * count for (wins, losses), count in records.items())
        avg_wins = total_wins / num_simulations
        team_avg_wins.append((team, avg_wins))
    
    team_avg_wins.sort(key=lambda x: -x[1])
    
    for rank, (team, avg_wins) in enumerate(team_avg_wins, 1):
        print(f"{rank:2d}. {team:<25} {avg_wins:.3f} avg wins")

def display_extremes(worst_losses, closest_wins):
    """
    Display the worst loss and closest win for each team.
    """
    print("\n" + "="*80)
    print("WORST LOSSES AND CLOSEST WINS")
    print("="*80)
    
    for team in sorted(worst_losses.keys()):
        print(f"\n{team}:")
        print("-" * 60)
        
        # Display worst loss
        wl = worst_losses[team]
        if wl['opponent']:
            print(f"Worst Loss:")
            print(f"  Week {wl['week']} vs {wl['opponent']}")
            print(f"  Score: {wl['team_score']:.2f} - {wl['opp_score']:.2f}")
            print(f"  Margin: -{wl['margin']:.2f} points")
        else:
            print(f"Worst Loss: N/A (no losses recorded)")
        
        print()
        
        # Display closest win
        cw = closest_wins[team]
        if cw['opponent'] and cw['margin'] != float('inf'):
            print(f"Closest Win:")
            print(f"  Week {cw['week']} vs {cw['opponent']}")
            print(f"  Score: {cw['team_score']:.2f} - {cw['opp_score']:.2f}")
            print(f"  Margin: +{cw['margin']:.2f} points")
        else:
            print(f"Closest Win: N/A (no wins recorded)")

def save_results(team_record_counts, num_simulations, output_file='results.json'):
    """
    Save detailed results to a JSON file.
    """
    results = {}
    for team, records in team_record_counts.items():
        results[team] = {
            f"{wins}-{losses}": {
                "count": count,
                "probability": count / num_simulations
            }
            for (wins, losses), count in records.items()
        }
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to {output_file}")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Fantasy Football Schedule Simulator')
    parser.add_argument('--csv', type=str, default='scores.csv',
                        help='Path to CSV file with team scores (default: scores.csv)')
    parser.add_argument('--weeks', type=int, default=7,
                        help='Number of weeks to simulate (default: 7)')
    parser.add_argument('--simulations', type=int, default=100000,
                        help='Number of simulations to run (default: 100000)')
    parser.add_argument('--output', type=str, default='results.json',
                        help='Output JSON file name (default: results.json)')
    
    args = parser.parse_args()
    
    print("Fantasy Football Schedule Simulator")
    print("="*80)
    
    # Read team scores
    print(f"\nReading scores from {args.csv}...")
    teams_scores = read_scores(args.csv, args.weeks)
    print(f"Loaded {len(teams_scores)} teams")
    
    # Run simulations
    team_record_counts, worst_losses, closest_wins = run_simulations(teams_scores, args.weeks, args.simulations)
    
    # Analyze and display results
    analyze_results(team_record_counts, args.simulations)
    
    # Display worst losses and closest wins
    display_extremes(worst_losses, closest_wins)
    
    # Save results
    save_results(team_record_counts, args.simulations, args.output)