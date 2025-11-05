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

# Fantasy Football Schedule Simulator - Web Interface

A Flask web application to simulate and visualize fantasy football schedule outcomes using Monte Carlo analysis.

## Features

- 🎯 Upload CSV with team scores
- 🔢 Configurable number of weeks and simulations
- 📊 Beautiful visual display of record distributions
- 🏆 Team rankings by average wins
- 📈 Probability bars for each possible record
- ⚡ Worst loss and closest win tracking for each team
- 📱 Responsive design

## Installation

1. Install Flask:
```bash
pip install flask
```

## Running the Application

1. Navigate to the directory containing `app.py`
2. Run the Flask app:
```bash
python app.py
```

3. Open your browser and go to:
```
http://localhost:5000
```

## Usage

1. **Prepare Your CSV File**
   - Format: `teamname,score1,score2,score3,...`
   - Each row = one team
   - Each column after team name = that week's score
   
   Example:
   ```
   Team Alpha,105.3,98.7,112.4,89.5,101.2,95.8,108.6
   Team Beta,92.1,110.5,88.3,105.7,97.4,102.9,91.8
   ```

2. **Upload and Configure**
   - Upload your CSV file
   - Set number of weeks (must match CSV columns)
   - Set number of simulations (higher = more accurate but slower)
   - Default: 100,000 simulations

3. **View Results**
   - Team rankings by average wins
   - Detailed record distribution for each team
   - Probability visualization with bars
   - Worst loss and closest win for each team

## File Structure

```
├── app.py                  # Flask application
├── templates/
│   ├── index.html         # Upload page
│   └── results.html       # Results display page
└── uploads/               # Directory for uploaded CSV files (created automatically)
```

## Results Display

For each team, you'll see:

- **Average Wins**: Expected wins across all simulations
- **Record Distribution**: All possible W-L records with:
  - Count: How many simulations resulted in this record
  - Probability: Percentage chance of this record
  - Visual bar: Probability visualization
- **Worst Loss**: Largest margin of defeat
- **Closest Win**: Smallest margin of victory

## Tips

- **More simulations** (500K+) provide more stable results but take longer
- **Fewer simulations** (10K-50K) are good for quick tests
- The app tracks the top 10 most likely records for each team
- All matchups are randomly generated each simulation
- Results are deterministic for the same number of simulations (uses randomization)

## Technical Details

- **Backend**: Flask (Python)
- **Simulation**: Monte Carlo method
- **Styling**: Pure CSS with gradient backgrounds
- **Responsive**: Works on desktop and mobile

## Example Output

After simulation, you'll see:
1. Overall rankings sorted by average wins
2. Individual team cards showing:
   - Record distribution table
   - Probability bars
   - Extreme matchups (worst loss, closest win)

## Customization

You can modify:
- `app.py`: Change simulation logic or add features
- `templates/index.html`: Modify upload form
- `templates/results.html`: Customize results display
- CSS in templates: Change colors, fonts, layout

## Notes

- Uploads are stored in `uploads/` directory
- Each simulation generates a new random schedule
- Results show all possible outcomes based on actual scores
- The app does NOT store results between sessions

Enjoy analyzing your fantasy football league! 🏈