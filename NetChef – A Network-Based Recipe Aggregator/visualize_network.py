import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from datetime import datetime, timedelta
import argparse
import random

# Set seaborn style
sns.set_theme(style="whitegrid")


def generate_sample_api_data(num_records=500):
    """Generate realistic sample API request data"""
    endpoints = [
        '/recipes?ingredient=lunch',
        '/recipes?ingredient=dinner',
        '/recipes?ingredient=breakfast',
        '/recipes/categories',
        '/recipes/random'
    ]

    status_codes = [200, 200, 200, 200, 200, 200, 404, 500, 401]
    methods = ['GET', 'GET', 'GET', 'GET', 'POST']
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)',
        'PostmanRuntime/7.28.4',
        'curl/7.68.0'
    ]

    # Generate timestamps over last 24 hours
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    timestamps = [start_time + timedelta(seconds=random.randint(0, 86400)) for _ in range(num_records)]
    timestamps.sort()

    # Generate data with more weight to lunch/dinner endpoints
    endpoint_choices = random.choices(
        endpoints,
        weights=[40, 40, 10, 5, 5],  # More lunch/dinner requests
        k=num_records
    )

    # Create DataFrame
    data = {
        'timestamp': timestamps,
        'endpoint': endpoint_choices,
        'method': random.choices(methods, k=num_records),
        'status_code': random.choices(status_codes, k=num_records),
        'response_time_ms': [random.randint(50, 2000) for _ in range(num_records)],
        'user_agent': random.choices(user_agents, k=num_records),
        'client_ip': [
            f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            for _ in range(num_records)]
    }

    df = pd.DataFrame(data)
    return df


def create_output_dir():
    """Create output directory if it doesn't exist"""
    os.makedirs("output", exist_ok=True)
    return "output"


def generate_filename(prefix, extension="png"):
    """Generate timestamped filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def plot_endpoint_usage(df, output_dir):
    """Plot endpoint usage bar chart"""
    try:
        plt.figure(figsize=(10, 6))
        endpoint_counts = df['endpoint'].value_counts()
        ax = sns.barplot(x=endpoint_counts.values, y=endpoint_counts.index, palette="viridis")

        # Add value labels on bars
        for i, v in enumerate(endpoint_counts.values):
            ax.text(v + 0.5, i, str(v), color='black', va='center')

        plt.title("API Endpoint Usage Count", pad=20)
        plt.xlabel("Count")
        plt.ylabel("Endpoint")
        plt.tight_layout()

        output_path = os.path.join(output_dir, generate_filename("endpoint_usage"))
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Saved endpoint usage plot to {output_path}")
    except Exception as e:
        print(f"Error generating endpoint usage plot: {str(e)}")


def plot_response_times(df, output_dir):
    """Plot response time distribution"""
    try:
        plt.figure(figsize=(10, 6))
        sns.boxplot(
            x='response_time_ms',
            y='endpoint',
            data=df[df['endpoint'].isin(['/recipes?ingredient=lunch', '/recipes?ingredient=dinner'])],
            palette="coolwarm"
        )
        plt.title("Response Time Distribution (ms)\nLunch vs Dinner Endpoints", pad=20)
        plt.xlabel("Response Time (ms)")
        plt.ylabel("Endpoint")
        plt.tight_layout()

        output_path = os.path.join(output_dir, generate_filename("response_times"))
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Saved response times plot to {output_path}")
    except Exception as e:
        print(f"Error generating response times plot: {str(e)}")


def plot_requests_over_time(df, output_dir):
    """Plot requests over time"""
    try:
        # Filter for lunch and dinner endpoints
        filtered_df = df[df['endpoint'].isin(['/recipes?ingredient=lunch', '/recipes?ingredient=dinner'])]

        if not filtered_df.empty:
            filtered_df['time_bin'] = filtered_df['timestamp'].dt.floor('H')
            time_series = filtered_df.groupby(['time_bin', 'endpoint']).size().unstack(fill_value=0)

            plt.figure(figsize=(12, 6))
            time_series.plot(kind='line', marker='o', ax=plt.gca(), markersize=5)
            plt.title("API Requests Over Time", pad=20)
            plt.ylabel("Request Count")
            plt.xlabel("Time")
            plt.legend(title="Endpoint", bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()

            output_path = os.path.join(output_dir, generate_filename("requests_over_time"))
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Saved requests over time plot to {output_path}")
    except Exception as e:
        print(f"Error generating requests over time plot: {str(e)}")


def plot_status_codes(df, output_dir):
    """Plot status code distribution"""
    try:
        plt.figure(figsize=(8, 6))
        status_counts = df['status_code'].value_counts()
        ax = sns.barplot(x=status_counts.index.astype(str), y=status_counts.values, palette="rocket")

        # Add value labels on bars
        for p in ax.patches:
            ax.annotate(f"{int(p.get_height())}",
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', xytext=(0, 5), textcoords='offset points')

        plt.title("HTTP Status Code Distribution", pad=20)
        plt.ylabel("Count")
        plt.xlabel("Status Code")
        plt.tight_layout()

        output_path = os.path.join(output_dir, generate_filename("status_codes"))
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Saved status codes plot to {output_path}")
    except Exception as e:
        print(f"Error generating status codes plot: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="API Request Analysis Visualizer")
    parser.add_argument("-i", "--input", default="api_requests.csv",
                        help="Input CSV file path (default: api_requests.csv)")
    parser.add_argument("-g", "--generate", action="store_true",
                        help="Generate sample data if input file doesn't exist")
    args = parser.parse_args()

    # Create output directory
    output_dir = create_output_dir()

    # Check if input file exists
    if not os.path.exists(args.input):
        if args.generate:
            print(f"\nGenerating sample data file: {args.input}")
            df = generate_sample_api_data()
            df.to_csv(args.input, index=False)
            print(f"Created sample data with {len(df)} records")
        else:
            print(f"\nERROR: Input file not found at: {os.path.abspath(args.input)}")
            print("Please either:")
            print(f"1. Place your CSV file at {os.path.abspath(args.input)}")
            print("2. Use -g flag to generate sample data automatically")
            print("3. Specify the correct path using -i argument")
            sys.exit(1)
    else:
        # Load existing data
        try:
            df = pd.read_csv(args.input)
            print(f"\nLoaded data from {os.path.abspath(args.input)}")
        except Exception as e:
            print(f"\nERROR: Could not read input file: {str(e)}")
            sys.exit(1)

    # Convert timestamp if exists
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        print(f"Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")

    print(f"Total records: {len(df)}")

    # Generate plots
    plot_endpoint_usage(df, output_dir)
    plot_response_times(df, output_dir)
    plot_requests_over_time(df, output_dir)
    plot_status_codes(df, output_dir)

    print("\nAnalysis completed successfully!")


if __name__ == "__main__":
    main()