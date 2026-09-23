import pandas as pd
import numpy as np

class TimeSeriesAnalyzer:
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with a pandas DataFrame containing OHLCV data.
        Expected columns: ['Open', 'High', 'Low', 'Close', 'Volume']
        """
        # Make a copy to avoid SettingWithCopyWarning
        self.df = df.copy()

    def add_moving_averages(self, windows=[5, 20, 60]):
        """
        Add simple moving averages to the dataframe.
        """
        for w in windows:
            self.df[f'MA_{w}'] = self.df['Close'].rolling(window=w).mean()
        return self.df

    def add_bollinger_bands(self, window=20, num_std=2):
        """
        Add Bollinger Bands (Upper, Lower, and Middle Band).
        """
        self.df['BB_Mid'] = self.df['Close'].rolling(window=window).mean()
        self.df['BB_Std'] = self.df['Close'].rolling(window=window).std()
        self.df['BB_Upper'] = self.df['BB_Mid'] + (self.df['BB_Std'] * num_std)
        self.df['BB_Lower'] = self.df['BB_Mid'] - (self.df['BB_Std'] * num_std)
        return self.df

    def calculate_correlations(self, period=60):
        """
        Calculate rolling correlation between Close price and Volume.
        """
        self.df['Corr_Close_Vol'] = self.df['Close'].rolling(window=period).corr(self.df['Volume'])
        return self.df

    def generate_signals(self):
        """
        Generate simple trading signals based on BB.
        1: Buy (Price crosses above lower band)
        -1: Sell (Price crosses below upper band)
        0: Hold
        """
        # Ensure BB exists
        if 'BB_Lower' not in self.df.columns:
            self.add_bollinger_bands()
            
        self.df['Signal'] = 0
        
        # Buy signal: previous close < lower band, current close > lower band
        buy_condition = (self.df['Close'].shift(1) < self.df['BB_Lower'].shift(1)) & (self.df['Close'] > self.df['BB_Lower'])
        
        # Sell signal: previous close > upper band, current close < upper band
        sell_condition = (self.df['Close'].shift(1) > self.df['BB_Upper'].shift(1)) & (self.df['Close'] < self.df['BB_Upper'])
        
        self.df.loc[buy_condition, 'Signal'] = 1
        self.df.loc[sell_condition, 'Signal'] = -1
        
        return self.df

    def process_all(self):
        """
        Run all analysis and return the final dataframe.
        """
        self.add_moving_averages()
        self.add_bollinger_bands()
        self.calculate_correlations()
        self.generate_signals()
        return self.df

if __name__ == "__main__":
    import yfinance as yf
    print("Testing TimeSeriesAnalyzer with Apple (AAPL) data...")
    # Use single ticker and squeeze multiindex
    data = yf.download("AAPL", start="2023-01-01", end="2024-01-01")
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
        
    analyzer = TimeSeriesAnalyzer(data)
    result = analyzer.process_all()
    print(result.tail())
