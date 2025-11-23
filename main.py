"""
European Population Data Analysis System
Author: Student Project
Date: 2025
Description: Analysis of European population trends using Eurostat open data
"""

# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class DataLoader:
    """
    Class responsible for loading and initial validation of data.
    Follows Single Responsibility Principle from SOLID.
    """
    
    def __init__(self, url):
        """
        Initialize DataLoader with data source URL.
        
        Args:
            url (str): URL to the dataset
        """
        self.url = url
        self.raw_data = None
    
    def load_data(self):
        """
        Load data from URL and perform basic validation.
        
        Returns:
            pd.DataFrame: Loaded dataset
        """
        try:
            print(f"Loading data from: {self.url}")
            self.raw_data = pd.read_csv(self.url)
            print(f"Data loaded successfully. Shape: {self.raw_data.shape}")
            return self.raw_data
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def get_data_info(self):
        """Display basic information about loaded data."""
        if self.raw_data is not None:
            print("\n=== Dataset Information ===")
            print(f"Rows: {self.raw_data.shape[0]}")
            print(f"Columns: {self.raw_data.shape[1]}")
            print(f"\nColumn names: {list(self.raw_data.columns)}")
            print(f"\nFirst few rows:")
            print(self.raw_data.head())


class DataProcessor:
    """
    Class for data cleaning, filtering, and transformation.
    Implements data processing operations following DRY principle.
    """
    
    def __init__(self, data):
        """
        Initialize DataProcessor with dataset.
        
        Args:
            data (pd.DataFrame): Raw dataset
        """
        self.data = data.copy()
        self.processed_data = None
    
    def clean_data(self):
        """Remove missing values and duplicates."""
        print("\n=== Data Cleaning ===")
        initial_rows = len(self.data)
        
        # Remove duplicates
        self.data = self.data.drop_duplicates()
        
        # Remove rows with missing values
        self.data = self.data.dropna()
        
        final_rows = len(self.data)
        print(f"Removed {initial_rows - final_rows} rows")
        print(f"Final dataset size: {final_rows} rows")
        
        return self.data
    
    def filter_by_year(self, start_year=None, end_year=None):
        """
        Filter data by year range.
        
        Args:
            start_year (int): Starting year
            end_year (int): Ending year
        
        Returns:
            pd.DataFrame: Filtered data
        """
        # Check for different year column names
        year_col = None
        for col in ['TIME_PERIOD', 'time', 'year', 'Year']:
            if col in self.data.columns:
                year_col = col
                break
        
        if year_col is None:
            print("No year column found")
            return self.data
        
        if start_year:
            self.data = self.data[self.data[year_col] >= start_year]
        if end_year:
            self.data = self.data[self.data[year_col] <= end_year]
        
        print(f"Filtered data by year: {len(self.data)} rows")
        return self.data
    
    def filter_european_countries(self):
        """Filter only European countries."""
        european_countries = [
            'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus',
            'Czechia', 'Denmark', 'Estonia', 'Finland', 'France',
            'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy',
            'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands',
            'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia',
            'Spain', 'Sweden', 'United Kingdom', 'Norway', 'Switzerland'
        ]
        
        # Try different possible country column names
        country_col = None
        for col in ['geo', 'country', 'Country', 'GEO']:
            if col in self.data.columns:
                country_col = col
                break
        
        if country_col:
            self.data = self.data[
                self.data[country_col].isin(european_countries)
            ]
            print(f"Filtered European countries: {len(self.data)} rows")
        
        return self.data
    
    def aggregate_by_country(self):
        """
        Aggregate population data by country.
        
        Returns:
            pd.DataFrame: Aggregated data
        """
        country_col = self._get_country_column()
        value_col = self._get_value_column()
        
        if country_col and value_col:
            agg_data = self.data.groupby(country_col)[value_col].agg([
                'mean', 'min', 'max', 'sum'
            ]).reset_index()
            
            agg_data.columns = [
                'Country', 'Average', 'Minimum', 'Maximum', 'Total'
            ]
            
            return agg_data
        
        return self.data
    
    def _get_country_column(self):
        """Helper method to identify country column."""
        for col in ['geo', 'country', 'Country', 'GEO', 'Country Name']:
            if col in self.data.columns:
                return col
        return None
    
    def _get_value_column(self):
        """Helper method to identify value column."""
        for col in ['OBS_VALUE', 'value', 'population', 'Population', 'Value']:
            if col in self.data.columns:
                return col
        return None


class DataAnalyzer:
    """
    Class for statistical analysis and insights generation.
    Separates analysis logic from visualization.
    """
    
    def __init__(self, data):
        """
        Initialize DataAnalyzer with processed data.
        
        Args:
            data (pd.DataFrame): Processed dataset
        """
        self.data = data
    
    def calculate_statistics(self):
        """
        Calculate descriptive statistics.
        
        Returns:
            dict: Statistical summary
        """
        stats = {}
        
        numeric_cols = self.data.select_dtypes(
            include=[np.number]
        ).columns
        
        for col in numeric_cols:
            stats[col] = {
                'mean': self.data[col].mean(),
                'median': self.data[col].median(),
                'std': self.data[col].std(),
                'min': self.data[col].min(),
                'max': self.data[col].max()
            }
        
        return stats
    
    def find_top_countries(self, n=10):
        """
        Find top N countries by population.
        
        Args:
            n (int): Number of top countries
        
        Returns:
            pd.DataFrame: Top countries
        """
        processor = DataProcessor(self.data)
        country_col = processor._get_country_column()
        value_col = processor._get_value_column()
        
        if country_col and value_col:
            top = self.data.nlargest(n, value_col)[[country_col, value_col]]
            return top
        
        return None
    
    def calculate_growth_rate(self):
        """
        Calculate population growth rate over time.
        
        Returns:
            pd.DataFrame: Growth rates by country
        """
        processor = DataProcessor(self.data)
        country_col = processor._get_country_column()
        value_col = processor._get_value_column()
        
        # Find year column
        year_col = None
        for col in ['TIME_PERIOD', 'time', 'year', 'Year']:
            if col in self.data.columns:
                year_col = col
                break
        
        if country_col and value_col and year_col:
            # Sort by country and year
            sorted_data = self.data.sort_values([country_col, year_col])
            
            # Calculate growth rate
            sorted_data['growth_rate'] = sorted_data.groupby(
                country_col
            )[value_col].pct_change() * 100
            
            return sorted_data
        
        return self.data


class DataVisualizer:
    """
    Class for creating visualizations and charts.
    Follows Interface Segregation Principle.
    """
    
    def __init__(self, data):
        """
        Initialize DataVisualizer with data.
        
        Args:
            data (pd.DataFrame): Data to visualize
        """
        self.data = data
        self.processor = DataProcessor(data)
    
    def plot_top_countries(self, n=15):
        """
        Create bar chart of top N countries by population.
        
        Args:
            n (int): Number of countries to display
        """
        country_col = self.processor._get_country_column()
        value_col = self.processor._get_value_column()
        
        if country_col and value_col:
            # Find year column
            year_col = None
            for col in ['TIME_PERIOD', 'time', 'year', 'Year']:
                if col in self.data.columns:
                    year_col = col
                    break
            
            if year_col:
                # Get most recent data point for each country
                latest_data = self.data.sort_values(year_col).groupby(
                    country_col
                ).tail(1)
            else:
                latest_data = self.data
            
            top_n = latest_data.nlargest(n, value_col)
            
            plt.figure(figsize=(12, 6))
            plt.barh(top_n[country_col], top_n[value_col], color='steelblue')
            plt.xlabel('Population', fontsize=12)
            plt.ylabel('Country', fontsize=12)
            plt.title(f'Top {n} European Countries by Population', 
                     fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.show()
            print(f"✓ Top {n} countries chart displayed")
        else:
            print("Cannot create plot: missing required columns")
    
    def plot_trend_over_time(self, countries=None):
        """
        Create line chart showing population trends.
        
        Args:
            countries (list): List of countries to plot
        """
        country_col = self.processor._get_country_column()
        value_col = self.processor._get_value_column()
        
        # Find year column
        year_col = None
        for col in ['TIME_PERIOD', 'time', 'year', 'Year']:
            if col in self.data.columns:
                year_col = col
                break
        
        if country_col and value_col and year_col:
            if countries is None:
                # Select top 5 countries by average population
                top_countries = self.data.groupby(country_col)[
                    value_col
                ].mean().nlargest(5).index.tolist()
                countries = top_countries
            
            plt.figure(figsize=(14, 7))
            
            for country in countries:
                country_data = self.data[self.data[country_col] == country]
                country_data = country_data.sort_values(year_col)
                if len(country_data) > 0:
                    plt.plot(country_data[year_col], 
                            country_data[value_col], 
                            marker='o', label=country, linewidth=2, markersize=4)
            
            plt.xlabel('Year', fontsize=12)
            plt.ylabel('Population', fontsize=12)
            plt.title('Population Trends in European Countries', 
                     fontsize=14, fontweight='bold')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
            print("✓ Population trends chart displayed")
        else:
            print("Cannot create trend plot: missing required columns")
    
    def plot_distribution(self):
        """Create histogram showing population distribution."""
        value_col = self.processor._get_value_column()
        
        if value_col:
            plt.figure(figsize=(10, 6))
            plt.hist(self.data[value_col], bins=30, 
                    edgecolor='black', alpha=0.7, color='coral')
            plt.xlabel('Population', fontsize=12)
            plt.ylabel('Frequency', fontsize=12)
            plt.title('Distribution of Population Values', 
                     fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.show()
            print("✓ Distribution histogram displayed")
        else:
            print("Cannot create distribution plot: missing value column")
    
    def plot_comparison(self):
        """Create comparison chart of selected metrics."""
        country_col = self.processor._get_country_column()
        value_col = self.processor._get_value_column()
        
        if country_col and value_col:
            # Aggregate by country
            agg_data = self.data.groupby(country_col)[value_col].agg([
                'mean', 'min', 'max'
            ]).reset_index()
            
            # Select top 10 for readability
            top_10 = agg_data.nlargest(10, 'mean')
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            x = np.arange(len(top_10))
            width = 0.25
            
            ax.bar(x - width, top_10['min'], width, label='Minimum', color='lightblue')
            ax.bar(x, top_10['mean'], width, label='Average', color='steelblue')
            ax.bar(x + width, top_10['max'], width, label='Maximum', color='darkblue')
            
            ax.set_xlabel('Country', fontsize=12)
            ax.set_ylabel('Population', fontsize=12)
            ax.set_title('Population Comparison: Min, Avg, Max', 
                        fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(top_10[country_col], rotation=45, ha='right')
            ax.legend()
            
            plt.tight_layout()
            plt.show()
            print("✓ Comparison chart displayed")
        else:
            print("Cannot create comparison plot: missing required columns")


class ReportGenerator:
    """
    Class for generating analysis reports.
    Handles output formatting and report creation.
    """
    
    def __init__(self, data, analyzer):
        """
        Initialize ReportGenerator.
        
        Args:
            data (pd.DataFrame): Processed data
            analyzer (DataAnalyzer): Data analyzer instance
        """
        self.data = data
        self.analyzer = analyzer
    
    def generate_summary(self):
        """Generate and print analysis summary."""
        print("\n" + "="*60)
        print("EUROPEAN POPULATION ANALYSIS REPORT")
        print("="*60)
        
        print(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total records analyzed: {len(self.data)}")
        
        # Calculate statistics
        stats = self.analyzer.calculate_statistics()
        
        print("\n--- STATISTICAL SUMMARY ---")
        for col, values in stats.items():
            print(f"\n{col}:")
            print(f"  Mean: {values['mean']:,.2f}")
            print(f"  Median: {values['median']:,.2f}")
            print(f"  Std Dev: {values['std']:,.2f}")
            print(f"  Range: {values['min']:,.2f} - {values['max']:,.2f}")
        
        # Top countries
        print("\n--- TOP 10 COUNTRIES BY POPULATION ---")
        top = self.analyzer.find_top_countries(10)
        if top is not None:
            for idx, row in top.iterrows():
                print(f"{row.iloc[0]}: {row.iloc[1]:,.0f}")
        
        print("\n" + "="*60)


def main():
    """
    Main execution function.
    Orchestrates the entire analysis workflow.
    """
    print("="*60)
    print("EUROPEAN POPULATION DATA ANALYSIS SYSTEM")
    print("="*60)
    
    # Step 1: Load Data
    # Using Eurostat population data
    url = "https://raw.githubusercontent.com/datasets/population/master/data/population.csv"
    
    loader = DataLoader(url)
    raw_data = loader.load_data()
    
    if raw_data is None:
        print("Failed to load data. Exiting.")
        return
    
    loader.get_data_info()
    
    # Step 2: Process Data
    processor = DataProcessor(raw_data)
    processor.clean_data()
    processor.filter_by_year(start_year=2000)
    
    # Filter European countries if country column exists
    if 'Country Name' in processor.data.columns:
        european_countries = [
            'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus',
            'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France',
            'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy',
            'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands',
            'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia',
            'Spain', 'Sweden', 'United Kingdom', 'Norway', 'Switzerland'
        ]
        processor.data = processor.data[
            processor.data['Country Name'].isin(european_countries)
        ]
    
    processed_data = processor.data
    
    # Step 3: Analyze Data
    analyzer = DataAnalyzer(processed_data)
    
    # Step 4: Visualize Results
    visualizer = DataVisualizer(processed_data)
    
    print("\n--- Generating Visualizations ---\n")
    
    # Enable inline plotting for notebooks
    try:
        from IPython import get_ipython
        get_ipython().run_line_magic('matplotlib', 'inline')
    except:
        pass
    
    visualizer.plot_top_countries(n=15)
    
    # Check if Year column exists for trend plot
    year_col = None
    for col in ['TIME_PERIOD', 'time', 'year', 'Year']:
        if col in processed_data.columns:
            year_col = col
            break
    
    if year_col:
        # Plot trends for selected countries
        selected_countries = ['Germany', 'France', 'United Kingdom', 
                            'Italy', 'Spain']
        # Filter to only countries that exist in dataset
        available_countries = [c for c in selected_countries 
                              if c in processed_data['Country Name'].values]
        if available_countries:
            visualizer.plot_trend_over_time(countries=available_countries)
        else:
            visualizer.plot_trend_over_time()  # Use top 5 by default
    
    visualizer.plot_distribution()
    visualizer.plot_comparison()
    
    # Step 5: Generate Report
    report = ReportGenerator(processed_data, analyzer)
    report.generate_summary()
    
    print("\n✓ Analysis completed successfully!")
    print("✓ All visualizations generated!")
    print("✓ Report summary created!")


# Execute the program
if __name__ == "__main__":
    main()
