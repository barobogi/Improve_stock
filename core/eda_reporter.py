import os
import pandas as pd
import matplotlib.pyplot as plt

class EDAReporter:
    def __init__(self, ticker: str, df: pd.DataFrame, output_dir: str = "output/charts"):
        self.ticker = ticker
        self.df = df
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_chart(self) -> str:
        """
        Generate a matplotlib chart with Price, MA, and Bollinger Bands.
        Returns the absolute path to the saved image.
        """
        plt.figure(figsize=(12, 6))
        
        # Plot Close Price
        plt.plot(self.df.index, self.df['Close'], label='Close Price', color='white', linewidth=2)
        
        # Plot MAs
        if 'MA_20' in self.df.columns:
            plt.plot(self.df.index, self.df['MA_20'], label='MA 20', color='yellow', linestyle='--')
        if 'MA_60' in self.df.columns:
            plt.plot(self.df.index, self.df['MA_60'], label='MA 60', color='magenta', linestyle='-.')
            
        # Plot Bollinger Bands
        if 'BB_Upper' in self.df.columns and 'BB_Lower' in self.df.columns:
            plt.plot(self.df.index, self.df['BB_Upper'], label='BB Upper', color='cyan', alpha=0.5)
            plt.plot(self.df.index, self.df['BB_Lower'], label='BB Lower', color='cyan', alpha=0.5)
            plt.fill_between(self.df.index, self.df['BB_Lower'], self.df['BB_Upper'], color='cyan', alpha=0.1)
        
        # Styling
        plt.title(f"{self.ticker} Time Series Analysis", color='white', fontsize=16)
        plt.xlabel("Date", color='white')
        plt.ylabel("Price", color='white')
        plt.legend(facecolor='black', edgecolor='white', labelcolor='white')
        
        # Dark background
        ax = plt.gca()
        ax.set_facecolor('#1e1e1e')
        plt.gcf().patch.set_facecolor('#1e1e1e')
        ax.tick_params(colors='white')
        
        # Save
        chart_path = os.path.abspath(os.path.join(self.output_dir, f"{self.ticker}_eda_chart.png"))
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path

    def generate_report(self) -> str:
        """
        Generate a text-based markdown report summarizing the recent signals.
        """
        recent = self.df.iloc[-1]
        
        report = f"## 📈 {self.ticker} EDA 리포트\n\n"
        report += f"- **최근 종가**: {recent['Close']:.2f}\n"
        
        if 'MA_20' in recent:
            report += f"- **20일 이동평균선**: {recent['MA_20']:.2f}\n"
        if 'BB_Upper' in recent and 'BB_Lower' in recent:
            report += f"- **볼린저 밴드**: 하단 {recent['BB_Lower']:.2f} ~ 상단 {recent['BB_Upper']:.2f}\n"
            
        if 'Signal' in recent:
            signal_text = "매수 (과매도 탈출)" if recent['Signal'] == 1 else "매도 (과매수 이탈)" if recent['Signal'] == -1 else "관망 (특이사항 없음)"
            report += f"- **현재 시그널**: {signal_text}\n"
            
        return report

if __name__ == "__main__":
    import yfinance as yf
    from time_series_analyzer import TimeSeriesAnalyzer
    
    print("Testing EDAReporter with AAPL...")
    data = yf.download("AAPL", start="2023-11-01", end="2024-01-01")
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
        
    # Process
    analyzer = TimeSeriesAnalyzer(data)
    df_analyzed = analyzer.process_all()
    
    # Report
    reporter = EDAReporter("AAPL", df_analyzed)
    chart_path = reporter.generate_chart()
    text_report = reporter.generate_report()
    
    print(f"Chart saved to: {chart_path}")
    print("\n--- Report ---\n")
    print(text_report)
