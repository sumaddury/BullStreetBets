import os
import json
import statistics
from datetime import datetime
import csv as _csv
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))

INPUT_CSV = os.path.join(PROJECT_ROOT, 'tmp', 'traffic_avg_per_day.csv')
BETA = 1.0
PLOT_PATH = os.path.join(PROJECT_ROOT, 'static', 'spike_plot.png')
REPORT_JSON = os.path.join(PROJECT_ROOT, 'tmp', 'spike_report.json')


def load_monthly_rates(csv_path):
    """Load avg_per_day per month and return sorted list of (date, rate)"""
    records = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = _csv.DictReader(f)
        for row in reader:
            try:
                year = int(row['year'])
                month = int(row['month'])
                rate = float(row['avg_per_day'])
            except (KeyError, ValueError):
                continue
            records.append((datetime(year, month, 1), rate))
    records.sort(key=lambda x: x[0])
    return records


def compute_baseline_stats(rates):
    return {
        'mean': statistics.mean(rates),
        'stdev': statistics.stdev(rates),
        'variance': statistics.pvariance(rates),
        'median': statistics.median(rates),
        'min': min(rates),
        'max': max(rates)
    }


def detect_spike(rates, beta):
    baseline = rates[:-1]
    latest = rates[-1]
    stats = compute_baseline_stats(baseline)
    threshold = stats['mean'] + beta * stats['stdev']
    recommendation = 'straddle' if latest > threshold else 'no_action'
    return recommendation, stats, latest, threshold


def plot_timeseries(dates, rates, stats, threshold):
    plt.figure(figsize=(6, 3), dpi=100)
    plt.plot(dates, rates, marker='o', label='avg_per_day')
    plt.axhline(stats['mean'], linestyle='--', label='baseline mean')
    plt.axhline(threshold, linestyle='-.', label=f'mean + {BETA}*std')
    plt.title('Monthly Average Traffic per Day')
    plt.xlabel('Month')
    plt.ylabel('Avg Weighted Traffic per Day')
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=100, bbox_inches='tight')
    plt.close()


def main():
    if not os.path.isfile(INPUT_CSV):
        raise FileNotFoundError(f"Avg-per-day CSV not found: {INPUT_CSV}")
    data = load_monthly_rates(INPUT_CSV)
    if len(data) < 2:
        raise RuntimeError(f"Need at least two months of data, but found {len(data)}")
    dates, rates = zip(*data)

    recommendation, stats, latest, threshold = detect_spike(rates, BETA)
    plot_timeseries(dates, rates, stats, threshold)

    last_date = dates[-1]
    report = {
        'year': last_date.year,
        'month': last_date.month,
        'latest_rate': latest,
        'beta': BETA,
        'mean': stats['mean'],
        'stdev': stats['stdev'],
        'variance': stats['variance'],
        'median': stats['median'],
        'min': stats['min'],
        'max': stats['max'],
        'threshold': threshold,
        'recommendation': recommendation,
        'plot_path': PLOT_PATH,
        'input_csv': INPUT_CSV
    }
    with open(REPORT_JSON, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

if __name__ == '__main__':
    main()
