"""
Web-based TradingView Backtest System using Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_fetcher import TradingViewDataFetcher
from backtest_engine import BacktestEngine
from strategies import (
    simple_moving_average_crossover,
    rsi_strategy,
    bollinger_bands_strategy,
    buy_and_hold,
    macd_strategy,
    stochastic_strategy,
    ema_crossover_strategy,
    multi_indicator_strategy
)
from tvDatafeed import Interval
from pinescript_parser import create_strategy_from_pinescript


# Page config
st.set_page_config(
    page_title="TradingView Backtest System",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .trade-profit {
        color: green;
        font-weight: bold;
    }
    .trade-loss {
        color: red;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def fetch_data(symbol, exchange, interval_value, n_bars):
    """Fetch data with caching"""
    fetcher = TradingViewDataFetcher()
    return fetcher.get_data(symbol, exchange, interval_value, n_bars)


def display_detailed_summary(results, symbol, exchange, interval_display, data):
    """Display detailed backtest summary"""
    st.subheader("📊 Detailed Backtest Summary")

    # Create tabs for different summary sections
    tab1, tab2, tab3 = st.tabs(["📈 Performance", "💰 Financial Metrics", "📉 Risk Analysis"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Trading Performance")
            perf_data = {
                "Metric": [
                    "Initial Capital",
                    "Final Equity",
                    "Net Profit/Loss",
                    "Total Return",
                    "Annualized Return (approx)",
                ],
                "Value": [
                    f"${results['initial_capital']:,.2f}",
                    f"${results['final_equity']:,.2f}",
                    f"${results['final_equity'] - results['initial_capital']:,.2f}",
                    f"{results['total_return_pct']:.2f}%",
                    f"{results['total_return_pct'] * (365/len(data)):.2f}%" if len(data) > 0 else "N/A"
                ]
            }
            st.dataframe(pd.DataFrame(perf_data), hide_index=True, use_container_width=True)

        with col2:
            st.markdown("### Trade Statistics")
            trade_stats = {
                "Metric": [
                    "Total Trades",
                    "Winning Trades",
                    "Losing Trades",
                    "Win Rate",
                    "Profit Factor"
                ],
                "Value": [
                    str(results['total_trades']),
                    str(results['winning_trades']),
                    str(results['losing_trades']),
                    f"{results['win_rate_pct']:.2f}%",
                    f"{abs(results['avg_win'] * results['winning_trades'] / (results['avg_loss'] * results['losing_trades'])):.2f}" if results['losing_trades'] > 0 and results['avg_loss'] != 0 else "N/A"
                ]
            }
            st.dataframe(pd.DataFrame(trade_stats), hide_index=True, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Win/Loss Analysis")
            total_wins = results['avg_win'] * results['winning_trades']
            total_losses = results['avg_loss'] * results['losing_trades']

            win_loss_data = {
                "Metric": [
                    "Average Win",
                    "Average Loss",
                    "Largest Win",
                    "Largest Loss",
                    "Total Wins",
                    "Total Losses"
                ],
                "Value": [
                    f"${results['avg_win']:,.2f}",
                    f"${results['avg_loss']:,.2f}",
                    f"${max([t.pnl for t in results['trades']], default=0):,.2f}",
                    f"${min([t.pnl for t in results['trades']], default=0):,.2f}",
                    f"${total_wins:,.2f}",
                    f"${total_losses:,.2f}"
                ]
            }
            st.dataframe(pd.DataFrame(win_loss_data), hide_index=True, use_container_width=True)

        with col2:
            st.markdown("### Position Metrics")
            if results['trades']:
                avg_hold_time = sum([
                    (t.exit_time - t.entry_time).total_seconds() / 3600
                    for t in results['trades']
                    if t.exit_time and t.entry_time
                ]) / len([t for t in results['trades'] if t.exit_time])

                position_data = {
                    "Metric": [
                        "Avg Hold Time",
                        "Longest Trade",
                        "Shortest Trade",
                        "Avg Trade Return",
                    ],
                    "Value": [
                        f"{avg_hold_time:.1f} hours",
                        f"{max([(t.exit_time - t.entry_time).total_seconds() / 3600 for t in results['trades'] if t.exit_time and t.entry_time], default=0):.1f} hours",
                        f"{min([(t.exit_time - t.entry_time).total_seconds() / 3600 for t in results['trades'] if t.exit_time and t.entry_time], default=0):.1f} hours",
                        f"{sum([t.pnl for t in results['trades']]) / len(results['trades']):,.2f} $"
                    ]
                }
                st.dataframe(pd.DataFrame(position_data), hide_index=True, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Risk Metrics")
            equity_curve = results['equity_curve']
            returns = equity_curve['equity'].pct_change().dropna()
            sharpe_ratio = (returns.mean() / returns.std() * (252 ** 0.5)) if len(returns) > 0 and returns.std() != 0 else 0

            risk_data = {
                "Metric": [
                    "Max Drawdown",
                    "Sharpe Ratio (approx)",
                    "Volatility",
                    "Risk/Reward Ratio"
                ],
                "Value": [
                    f"{results['max_drawdown_pct']:.2f}%",
                    f"{sharpe_ratio:.2f}",
                    f"{returns.std() * 100:.2f}%" if len(returns) > 0 else "N/A",
                    f"{abs(results['avg_win'] / results['avg_loss']):.2f}" if results['avg_loss'] != 0 else "N/A"
                ]
            }
            st.dataframe(pd.DataFrame(risk_data), hide_index=True, use_container_width=True)

        with col2:
            st.markdown("### Market Information")
            market_data = {
                "Metric": [
                    "Symbol",
                    "Exchange",
                    "Timeframe",
                    "Data Points",
                    "Date Range"
                ],
                "Value": [
                    symbol,
                    exchange if exchange else "Default",
                    interval_display,
                    str(len(data)),
                    f"{data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}"
                ]
            }
            st.dataframe(pd.DataFrame(market_data), hide_index=True, use_container_width=True)


def plot_interactive_chart(data, trades, strategy_name, results):
    """Create interactive plotly chart with buy/sell signals"""

    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=(f'{strategy_name} - Price Chart with Buy/Sell Signals', 'Equity Curve')
    )

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name='Price',
            increasing_line_color='green',
            decreasing_line_color='red'
        ),
        row=1, col=1
    )

    # Add buy signals
    buy_signals = [t for t in trades if t.entry_time is not None]
    if buy_signals:
        buy_times = [t.entry_time for t in buy_signals]
        buy_prices = [t.entry_price for t in buy_signals]
        fig.add_trace(
            go.Scatter(
                x=buy_times,
                y=buy_prices,
                mode='markers',
                name='Buy',
                marker=dict(
                    symbol='triangle-up',
                    size=15,
                    color='green',
                    line=dict(width=2, color='darkgreen')
                )
            ),
            row=1, col=1
        )

    # Add sell signals
    sell_signals = [t for t in trades if t.exit_time is not None]
    if sell_signals:
        sell_times = [t.exit_time for t in sell_signals]
        sell_prices = [t.exit_price for t in sell_signals]
        fig.add_trace(
            go.Scatter(
                x=sell_times,
                y=sell_prices,
                mode='markers',
                name='Sell',
                marker=dict(
                    symbol='triangle-down',
                    size=15,
                    color='red',
                    line=dict(width=2, color='darkred')
                )
            ),
            row=1, col=1
        )

    # Add profit/loss annotations
    for trade in trades:
        if trade.exit_time:
            pnl_pct = (trade.pnl / (trade.entry_price * trade.size)) * 100
            color = 'green' if trade.pnl > 0 else 'red'

            fig.add_annotation(
                x=trade.exit_time,
                y=trade.exit_price,
                text=f'{pnl_pct:+.1f}%',
                showarrow=True,
                arrowhead=2,
                arrowcolor=color,
                font=dict(size=10, color=color),
                bgcolor='white',
                bordercolor=color,
                borderwidth=2,
                row=1, col=1
            )

    # Add equity curve
    equity_df = results['equity_curve']
    fig.add_trace(
        go.Scatter(
            x=equity_df['time'],
            y=equity_df['equity'],
            mode='lines',
            name='Equity',
            line=dict(color='purple', width=2),
            fill='tonexty'
        ),
        row=2, col=1
    )

    # Add initial capital line
    fig.add_hline(
        y=results['initial_capital'],
        line_dash="dash",
        line_color="gray",
        annotation_text="Initial Capital",
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )

    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Equity ($)", row=2, col=1)

    return fig


def main():
    # Header
    st.markdown('<p class="main-header">📈 TradingView Backtest System</p>', unsafe_allow_html=True)

    # Sidebar for inputs
    st.sidebar.header("⚙️ Configuration")

    # Symbol and Exchange input (direct, no search)
    st.sidebar.subheader("📊 Stock/Crypto Symbol")

    symbol = st.sidebar.text_input(
        "Symbol",
        value="BTCUSD",
        help="Enter stock symbol (e.g., AAPL, TSLA, GOOGL) or crypto (e.g., BTCUSD, ETHUSD)",
        placeholder="e.g., AAPL, TSLA, BTCUSD"
    ).strip().upper()

    exchange_options = {
        "Auto/Default": "",
        "BINANCE (Crypto)": "BINANCE",
        "NASDAQ (Stocks)": "NASDAQ",
        "NYSE (Stocks)": "NYSE",
        "COINBASE (Crypto)": "COINBASE"
    }

    exchange_display = st.sidebar.selectbox(
        "Market/Exchange",
        options=list(exchange_options.keys()),
        help="Select market/exchange or use Auto/Default for automatic detection"
    )
    exchange = exchange_options[exchange_display]

    # Interval selection
    interval_options = {
        "1 Minute": Interval.in_1_minute,
        "5 Minutes": Interval.in_5_minute,
        "15 Minutes": Interval.in_15_minute,
        "1 Hour": Interval.in_1_hour,
        "4 Hours": Interval.in_4_hour,
        "Daily": Interval.in_daily,
        "Weekly": Interval.in_weekly
    }
    interval_display = st.sidebar.selectbox(
        "Time Interval",
        options=list(interval_options.keys()),
        index=5  # Daily
    )
    interval = interval_options[interval_display]

    # Number of bars
    n_bars = st.sidebar.number_input(
        "Number of Bars",
        min_value=50,
        max_value=5000,
        value=365,
        step=50
    )

    # Initial capital
    initial_capital = st.sidebar.number_input(
        "Initial Capital ($)",
        min_value=1,
        max_value=1000000,
        value=10000,
        step=100
    )

    # Commission
    commission = st.sidebar.number_input(
        "Commission (%)",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.01
    ) / 100

    # Strategy selection
    st.sidebar.subheader("📈 Trading Strategy")

    strategy_mode = st.sidebar.radio(
        "Strategy Source",
        ["Pre-built Strategies", "Custom Pine Script"],
        horizontal=False
    )

    custom_strategy_func = None
    strategy_name = None

    if strategy_mode == "Pre-built Strategies":
        strategy_options = {
            "Simple Moving Average Crossover": simple_moving_average_crossover,
            "RSI Strategy": rsi_strategy,
            "Bollinger Bands": bollinger_bands_strategy,
            "MACD Strategy": macd_strategy,
            "Stochastic Oscillator": stochastic_strategy,
            "EMA Crossover": ema_crossover_strategy,
            "Multi-Indicator (RSI+MACD+EMA)": multi_indicator_strategy,
            "Buy and Hold": buy_and_hold,
            "Compare All Strategies": None
        }

        strategy_name = st.sidebar.selectbox(
            "Select Strategy",
            options=list(strategy_options.keys()),
            index=8  # Compare All
        )

    else:
        # Pine Script input
        st.sidebar.write("Paste your TradingView Pine Script below:")

        default_pine = """// Paste your Pine Script here
// Example:
//@version=5
strategy("My Strategy", overlay=true)

fastEMA = ta.ema(close, 12)
slowEMA = ta.ema(close, 26)

if ta.crossover(fastEMA, slowEMA)
    strategy.entry("Long", strategy.long)

if ta.crossunder(fastEMA, slowEMA)
    strategy.close("Long")"""

        pinescript_code = st.sidebar.text_area(
            "Pine Script Code",
            value=default_pine,
            height=250,
            help="Paste your TradingView Pine Script strategy here"
        )

        if st.sidebar.button("🔄 Convert & Preview"):
            with st.sidebar:
                with st.spinner("Converting Pine Script..."):
                    custom_strategy_func, error = create_strategy_from_pinescript(pinescript_code)

                    if error:
                        st.error(f"❌ Conversion Error: {error}")
                    else:
                        st.success("✅ Pine Script converted successfully!")
                        st.info("Click 'Run Backtest' to test your strategy")

        # Store in session state
        if custom_strategy_func:
            st.session_state['custom_strategy'] = custom_strategy_func

        strategy_name = "Custom Pine Script Strategy"

    # Run backtest button
    run_backtest = st.sidebar.button("🚀 Run Backtest", type="primary")

    # Main content
    if run_backtest:
        if not symbol:
            st.error("⚠️ Please select a symbol from the search results, or use manual input in Advanced Options")
            return

        # Fetch data
        with st.spinner(f"Fetching data for {symbol} from {exchange or 'default exchange'}..."):
            try:
                data = fetch_data(symbol, exchange, interval, n_bars)
                st.success(f"✓ Successfully fetched {len(data)} bars")

                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📅 Data Range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
                with col2:
                    st.info(f"💰 Initial Capital: ${initial_capital:,.2f} | Commission: {commission*100:.2f}%")

            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")
                return

        # Run backtest
        if strategy_mode == "Custom Pine Script":
            # Run custom Pine Script strategy
            if 'custom_strategy' not in st.session_state:
                st.warning("⚠️ Please click 'Convert & Preview' first to convert your Pine Script")
                return

            custom_func = st.session_state.get('custom_strategy')
            if not custom_func:
                st.error("❌ No custom strategy found. Please convert your Pine Script first.")
                return

            st.subheader(f"📈 {strategy_name} - Results")

            with st.spinner("Running custom Pine Script strategy..."):
                engine = BacktestEngine(initial_capital=initial_capital, commission=commission)
                results = engine.run(data, custom_func)

            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Return", f"{results['total_return_pct']:.2f}%")
            with col2:
                st.metric("Final Equity", f"${results['final_equity']:,.2f}")
            with col3:
                st.metric("Win Rate", f"{results['win_rate_pct']:.2f}%")
            with col4:
                st.metric("Max Drawdown", f"{results['max_drawdown_pct']:.2f}%")

            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.metric("Total Trades", results['total_trades'])
            with col6:
                st.metric("Winning Trades", results['winning_trades'])
            with col7:
                st.metric("Avg Win", f"${results['avg_win']:.2f}")
            with col8:
                st.metric("Avg Loss", f"${results['avg_loss']:.2f}")

            # Detailed summary
            display_detailed_summary(results, symbol, exchange, interval_display, data)

            # Plot chart
            fig = plot_interactive_chart(data, results['trades'], strategy_name, results)
            st.plotly_chart(fig, use_container_width=True)

            # Trade log
            if results['trades']:
                st.subheader("📝 Trade Log")
                trade_data = []
                for i, trade in enumerate(results['trades'], 1):
                    pnl_pct = (trade.pnl / (trade.entry_price * trade.size)) * 100 if trade.entry_price else 0
                    trade_data.append({
                        '#': i,
                        'Entry Time': str(trade.entry_time),
                        'Entry Price': f"${trade.entry_price:.2f}",
                        'Exit Time': str(trade.exit_time),
                        'Exit Price': f"${trade.exit_price:.2f}",
                        'P&L': f"${trade.pnl:.2f}",
                        'P&L %': f"{pnl_pct:+.2f}%"
                    })

                trade_df = pd.DataFrame(trade_data)
                st.dataframe(trade_df, use_container_width=True, hide_index=True)

        elif strategy_name == "Compare All Strategies":
            # Compare all strategies
            st.subheader("📊 Strategy Comparison")

            results_list = []

            for name, func in strategy_options.items():
                if func is None:  # Skip "Compare All"
                    continue

                with st.spinner(f"Testing {name}..."):
                    engine = BacktestEngine(initial_capital=initial_capital, commission=commission)
                    results = engine.run(data, func)
                    results_list.append({
                        'Strategy': name,
                        'Final Equity': f"${results['final_equity']:,.2f}",
                        'Total Return': f"{results['total_return_pct']:.2f}%",
                        'Total Trades': results['total_trades'],
                        'Win Rate': f"{results['win_rate_pct']:.2f}%",
                        'Max Drawdown': f"{results['max_drawdown_pct']:.2f}%",
                        'Avg Win': f"${results['avg_win']:.2f}",
                        'Avg Loss': f"${results['avg_loss']:.2f}",
                        '_return_value': results['total_return_pct'],
                        '_results': results,
                        '_name': name
                    })

            # Display comparison table
            comparison_df = pd.DataFrame(results_list)
            comparison_display = comparison_df.drop(columns=['_return_value', '_results', '_name'])
            st.dataframe(comparison_display, use_container_width=True, hide_index=True)

            # Find best strategy
            best_idx = comparison_df['_return_value'].idxmax()
            best_strategy = results_list[best_idx]

            st.success(f"🏆 Best Strategy: {best_strategy['_name']} with {best_strategy['Total Return']} return")

            # Strategy selector with tabs
            st.subheader("📊 View Individual Strategy Results")
            st.write("Click on a strategy tab to view its detailed chart and metrics:")

            # Create tabs for each strategy
            tab_names = [item['_name'] for item in results_list]
            tabs = st.tabs(tab_names)

            for idx, (tab, strategy_item) in enumerate(zip(tabs, results_list)):
                with tab:
                    results = strategy_item['_results']
                    strategy_name_display = strategy_item['_name']

                    # Show if this is the best strategy
                    if idx == best_idx:
                        st.success("🏆 Best Performing Strategy")

                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Return", f"{results['total_return_pct']:.2f}%")
                    with col2:
                        st.metric("Final Equity", f"${results['final_equity']:,.2f}")
                    with col3:
                        st.metric("Win Rate", f"{results['win_rate_pct']:.2f}%")
                    with col4:
                        st.metric("Max Drawdown", f"{results['max_drawdown_pct']:.2f}%")

                    col5, col6, col7, col8 = st.columns(4)
                    with col5:
                        st.metric("Total Trades", results['total_trades'])
                    with col6:
                        st.metric("Winning Trades", results['winning_trades'])
                    with col7:
                        st.metric("Avg Win", f"${results['avg_win']:.2f}")
                    with col8:
                        st.metric("Avg Loss", f"${results['avg_loss']:.2f}")

                    # Detailed summary
                    display_detailed_summary(results, symbol, exchange, interval_display, data)

                    # Plot chart
                    fig = plot_interactive_chart(data, results['trades'], strategy_name_display, results)
                    st.plotly_chart(fig, use_container_width=True)

                    # Trade log
                    if results['trades']:
                        st.subheader("📝 Trade Log")
                        trade_data = []
                        for i, trade in enumerate(results['trades'], 1):
                            pnl_pct = (trade.pnl / (trade.entry_price * trade.size)) * 100 if trade.entry_price else 0
                            trade_data.append({
                                '#': i,
                                'Entry Time': str(trade.entry_time),
                                'Entry Price': f"${trade.entry_price:.2f}",
                                'Exit Time': str(trade.exit_time),
                                'Exit Price': f"${trade.exit_price:.2f}",
                                'P&L': f"${trade.pnl:.2f}",
                                'P&L %': f"{pnl_pct:+.2f}%"
                            })

                        trade_df = pd.DataFrame(trade_data)
                        st.dataframe(trade_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("No trades executed for this strategy")

        else:
            # Single strategy
            st.subheader(f"📈 {strategy_name} - Results")

            with st.spinner(f"Running backtest with {strategy_name}..."):
                engine = BacktestEngine(initial_capital=initial_capital, commission=commission)
                strategy_func = strategy_options[strategy_name]
                results = engine.run(data, strategy_func)

            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Return", f"{results['total_return_pct']:.2f}%")
            with col2:
                st.metric("Final Equity", f"${results['final_equity']:,.2f}")
            with col3:
                st.metric("Win Rate", f"{results['win_rate_pct']:.2f}%")
            with col4:
                st.metric("Max Drawdown", f"{results['max_drawdown_pct']:.2f}%")

            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.metric("Total Trades", results['total_trades'])
            with col6:
                st.metric("Winning Trades", results['winning_trades'])
            with col7:
                st.metric("Avg Win", f"${results['avg_win']:.2f}")
            with col8:
                st.metric("Avg Loss", f"${results['avg_loss']:.2f}")

            # Detailed summary
            display_detailed_summary(results, symbol, exchange, interval_display, data)

            # Plot chart
            fig = plot_interactive_chart(data, results['trades'], strategy_name, results)
            st.plotly_chart(fig, use_container_width=True)

            # Trade log
            if results['trades']:
                st.subheader("📝 Trade Log")
                trade_data = []
                for i, trade in enumerate(results['trades'], 1):
                    pnl_pct = (trade.pnl / (trade.entry_price * trade.size)) * 100 if trade.entry_price else 0
                    trade_data.append({
                        '#': i,
                        'Entry Time': str(trade.entry_time),
                        'Entry Price': f"${trade.entry_price:.2f}",
                        'Exit Time': str(trade.exit_time),
                        'Exit Price': f"${trade.exit_price:.2f}",
                        'P&L': f"${trade.pnl:.2f}",
                        'P&L %': f"{pnl_pct:+.2f}%"
                    })

                trade_df = pd.DataFrame(trade_data)
                st.dataframe(trade_df, use_container_width=True, hide_index=True)

    else:
        # Show welcome message
        st.info("👈 Configure your backtest parameters in the sidebar and click 'Run Backtest' to start!")

        st.markdown("""
        ### How to use:
        1. **Enter a stock symbol** (e.g., AAPL, TSLA, GOOGL) or crypto (e.g., BTCUSD, ETHUSD)
        2. **Select the exchange** (NASDAQ, NYSE for stocks; BINANCE, COINBASE for crypto)
        3. **Choose time interval** and number of bars
        4. **Set initial capital** and commission rate
        5. **Select a strategy** or compare all strategies
        6. Click **Run Backtest** to see results!

        ### Available Strategies:
        - **Simple Moving Average Crossover**: Buy when short MA crosses above long MA
        - **RSI Strategy**: Buy when RSI crosses above oversold, sell when crosses below overbought
        - **Bollinger Bands**: Mean reversion strategy using Bollinger Bands
        - **Buy and Hold**: Simple buy and hold strategy
        - **Compare All**: Test all strategies and show the best performer
        """)


if __name__ == "__main__":
    main()
