from flask import Flask, render_template, request, redirect, url_for
import json
import os
from werkzeug.utils import secure_filename
import csv
from collections import Counter
import random

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import simulation functions
def read_scores(filename, num_weeks):
    """Read team scores from CSV file."""
    teams = {}
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            team_name = row[0]
            scores = [float(score) for score in row[1:num_weeks + 1]]
            teams[team_name] = scores
    return teams

def generate_random_schedule(team_names, num_weeks=7):
    """Generate a random schedule where each team plays once per week."""
    schedule = []
    for week in range(num_weeks):
        teams_copy = team_names.copy()
        random.shuffle(teams_copy)
        
        week_matchups = []
        for i in range(0, len(teams_copy), 2):
            week_matchups.append((teams_copy[i], teams_copy[i+1]))
        schedule.append(week_matchups)
    
    return schedule

def simulate_season(teams_scores, schedule):
    """Simulate a single season given team scores and a schedule."""
    records = {team: [0, 0] for team in teams_scores.keys()}
    
    for week_num, week_matchups in enumerate(schedule):
        for team1, team2 in week_matchups:
            score1 = teams_scores[team1][week_num]
            score2 = teams_scores[team2][week_num]
            
            if score1 > score2:
                records[team1][0] += 1
                records[team2][1] += 1
            else:
                records[team2][0] += 1
                records[team1][1] += 1
    
    return {team: tuple(record) for team, record in records.items()}

def run_simulations(teams_scores, num_weeks, num_simulations=100000):
    """Run Monte Carlo simulations and track all possible records for each team."""
    team_names = list(teams_scores.keys())
    team_record_counts = {team: Counter() for team in team_names}
    
    worst_losses = {team: {'margin': 0, 'opponent': None, 'week': None, 'team_score': None, 'opp_score': None} 
                    for team in team_names}
    closest_wins = {team: {'margin': float('inf'), 'opponent': None, 'week': None, 'team_score': None, 'opp_score': None} 
                    for team in team_names}
    
    for sim in range(num_simulations):
        schedule = generate_random_schedule(team_names, num_weeks)
        season_results = simulate_season(teams_scores, schedule)
        
        for team, record in season_results.items():
            team_record_counts[team][record] += 1
        
        for week_num, week_matchups in enumerate(schedule):
            for team1, team2 in week_matchups:
                score1 = teams_scores[team1][week_num]
                score2 = teams_scores[team2][week_num]
                margin = abs(score1 - score2)
                
                if score1 > score2:
                    if margin < closest_wins[team1]['margin']:
                        closest_wins[team1] = {
                            'margin': margin, 'opponent': team2, 'week': week_num + 1,
                            'team_score': score1, 'opp_score': score2
                        }
                    if margin > worst_losses[team2]['margin']:
                        worst_losses[team2] = {
                            'margin': margin, 'opponent': team1, 'week': week_num + 1,
                            'team_score': score2, 'opp_score': score1
                        }
                else:
                    if margin < closest_wins[team2]['margin']:
                        closest_wins[team2] = {
                            'margin': margin, 'opponent': team1, 'week': week_num + 1,
                            'team_score': score2, 'opp_score': score1
                        }
                    if margin > worst_losses[team1]['margin']:
                        worst_losses[team1] = {
                            'margin': margin, 'opponent': team2, 'week': week_num + 1,
                            'team_score': score1, 'opp_score': score2
                        }
    
    return team_record_counts, worst_losses, closest_wins

def process_results(team_record_counts, worst_losses, closest_wins, num_simulations):
    """Process simulation results into a format suitable for web display."""
    results = []
    
    for team in sorted(team_record_counts.keys()):
        records = team_record_counts[team]
        
        # Sort by wins (descending), then by losses (ascending)
        sorted_records = sorted(records.items(), 
                               key=lambda x: (-x[0][0], x[0][1]))
        
        # Calculate statistics
        total_wins = sum(wins * count for (wins, losses), count in records.items())
        avg_wins = total_wins / num_simulations
        
        # Format record distribution
        record_dist = []
        for (wins, losses), count in sorted_records:
            probability = count / num_simulations * 100
            record_dist.append({
                'record': f"{wins}-{losses}",
                'count': count,
                'probability': probability
            })
        
        # Format worst loss
        wl = worst_losses[team]
        worst_loss = None
        if wl['opponent']:
            worst_loss = {
                'week': wl['week'],
                'opponent': wl['opponent'],
                'team_score': wl['team_score'],
                'opp_score': wl['opp_score'],
                'margin': wl['margin']
            }
        
        # Format closest win
        cw = closest_wins[team]
        closest_win = None
        if cw['opponent'] and cw['margin'] != float('inf'):
            closest_win = {
                'week': cw['week'],
                'opponent': cw['opponent'],
                'team_score': cw['team_score'],
                'opp_score': cw['opp_score'],
                'margin': cw['margin']
            }
        
        results.append({
            'team': team,
            'avg_wins': avg_wins,
            'record_dist': record_dist,
            'worst_loss': worst_loss,
            'closest_win': closest_win
        })
    
    # Sort by average wins
    results.sort(key=lambda x: -x['avg_wins'])
    
    return results

@app.route('/')
def index():
    """Homepage with upload form."""
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    """Handle file upload and run simulation."""
    if 'csv_file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['csv_file']
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get simulation parameters
        num_weeks = int(request.form.get('weeks', 7))
        num_simulations = int(request.form.get('simulations', 100000))
        
        # Read scores and run simulation
        teams_scores = read_scores(filepath, num_weeks)
        team_record_counts, worst_losses, closest_wins = run_simulations(
            teams_scores, num_weeks, num_simulations
        )
        
        # Process results
        results = process_results(team_record_counts, worst_losses, closest_wins, num_simulations)
        
        return render_template('results.html', 
                             results=results, 
                             num_simulations=num_simulations,
                             num_weeks=num_weeks)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)