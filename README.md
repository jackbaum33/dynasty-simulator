usage:
# Default (7 weeks, 100K simulations)
python fantasy_football_simulator.py

# Simulate 5 weeks with your data
python fantasy_football_simulator.py --csv scores.csv --weeks 5

# Simulate 10 weeks with more simulations
python fantasy_football_simulator.py --weeks 10 --simulations 500000

# Full custom run
python fantasy_football_simulator.py --csv mydata.csv --weeks 12 --simulations 250000 --output season_results.json

# See all options
python fantasy_football_simulator.py --help
