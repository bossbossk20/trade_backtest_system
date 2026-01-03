"""
Pine Script Parser - Convert Pine Script to Python dynamically
"""

import re


class PineScriptParser:
    """Parse and convert Pine Script strategies to Python"""

    def __init__(self):
        self.indicators = []
        self.entry_conditions = []
        self.exit_conditions = []
        self.variables = {}

    def parse(self, pinescript_code):
        """Parse Pine Script code and extract components"""
        lines = pinescript_code.strip().split('\n')

        for line in lines:
            line = line.strip()

            # Skip comments and empty lines
            if line.startswith('//') or not line:
                continue

            # Skip version and strategy declarations
            if line.startswith('//@version') or line.startswith('strategy('):
                continue

            # Parse variable assignments with indicators
            if '=' in line and ('ta.' in line or 'input' in line):
                self._parse_variable(line)

            # Parse entry conditions
            if 'strategy.entry' in line or ('if' in line and 'strategy.entry' in pinescript_code[pinescript_code.find(line):]):
                self._parse_entry(line)

            # Parse exit conditions
            if 'strategy.close' in line or 'strategy.exit' in line:
                self._parse_exit(line)

    def _parse_variable(self, line):
        """Parse variable assignment"""
        # Remove spaces around =
        line = re.sub(r'\s*=\s*', '=', line)

        # Extract variable name
        var_name = line.split('=')[0].strip()
        expression = line.split('=')[1].strip()

        # Skip input declarations for now
        if 'input' in expression:
            return

        self.variables[var_name] = expression

    def _parse_entry(self, line):
        """Parse entry condition"""
        # Look for common patterns
        if 'ta.crossover' in line:
            self.entry_conditions.append('crossover')
        elif 'ta.crossunder' in line:
            self.entry_conditions.append('crossunder')
        elif '>' in line or '<' in line:
            self.entry_conditions.append(line)

    def _parse_exit(self, line):
        """Parse exit condition"""
        if 'ta.crossunder' in line or 'ta.crossover' in line:
            self.exit_conditions.append(line)

    def generate_python_code(self, pinescript_code):
        """Generate Python strategy function from Pine Script"""

        # Simple template-based converter for common patterns
        code = '''
def pine_script_strategy(data, index, position):
    """
    Auto-generated from Pine Script
    """
    # Need minimum bars
    if index < 50:
        return 'hold'

    close = data['close'].iloc[:index+1]
    high = data['high'].iloc[:index+1]
    low = data['low'].iloc[:index+1]
    open_data = data['open'].iloc[:index+1]

'''

        # Detect common patterns and generate code
        if 'ta.ema' in pinescript_code and 'ta.crossover' in pinescript_code:
            # EMA Crossover strategy
            fast_period = self._extract_number(pinescript_code, 'ta.ema', 0) or 12
            slow_period = self._extract_number(pinescript_code, 'ta.ema', 1) or 26

            code += f'''
    # EMA Crossover Strategy (detected)
    fast_ma = close.ewm(span={fast_period}, adjust=False).mean()
    slow_ma = close.ewm(span={slow_period}, adjust=False).mean()

    current_fast = fast_ma.iloc[-1]
    current_slow = slow_ma.iloc[-1]
    prev_fast = fast_ma.iloc[-2]
    prev_slow = slow_ma.iloc[-2]

    if position is None:
        # Buy on crossover
        if prev_fast <= prev_slow and current_fast > current_slow:
            return 'buy'
    else:
        # Sell on crossunder
        if prev_fast >= prev_slow and current_fast < current_slow:
            return 'sell'
'''

        elif 'ta.sma' in pinescript_code and 'ta.crossover' in pinescript_code:
            # SMA Crossover strategy
            fast_period = self._extract_number(pinescript_code, 'ta.sma', 0) or 20
            slow_period = self._extract_number(pinescript_code, 'ta.sma', 1) or 50

            code += f'''
    # SMA Crossover Strategy (detected)
    fast_ma = close.rolling(window={fast_period}).mean()
    slow_ma = close.rolling(window={slow_period}).mean()

    current_fast = fast_ma.iloc[-1]
    current_slow = slow_ma.iloc[-1]
    prev_fast = fast_ma.iloc[-2]
    prev_slow = slow_ma.iloc[-2]

    if position is None:
        if prev_fast <= prev_slow and current_fast > current_slow:
            return 'buy'
    else:
        if prev_fast >= prev_slow and current_fast < current_slow:
            return 'sell'
'''

        elif 'ta.rsi' in pinescript_code:
            # RSI strategy
            period = self._extract_number(pinescript_code, 'ta.rsi') or 14
            oversold = 30
            overbought = 70

            if '<' in pinescript_code:
                oversold = self._extract_number(pinescript_code, '<', after_rsi=True) or 30
            if '>' in pinescript_code:
                overbought = self._extract_number(pinescript_code, '>', after_rsi=True) or 70

            code += f'''
    # RSI Strategy (detected)
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window={period}).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window={period}).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]

    if position is None:
        if current_rsi < {oversold}:
            return 'buy'
    else:
        if current_rsi > {overbought}:
            return 'sell'
'''

        elif 'ta.macd' in pinescript_code:
            # MACD strategy
            code += '''
    # MACD Strategy (detected)
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=9, adjust=False).mean()

    current_macd = macd_line.iloc[-1]
    current_signal = signal_line.iloc[-1]
    prev_macd = macd_line.iloc[-2]
    prev_signal = signal_line.iloc[-2]

    if position is None:
        if prev_macd <= prev_signal and current_macd > current_signal:
            return 'buy'
    else:
        if prev_macd >= prev_signal and current_macd < current_signal:
            return 'sell'
'''

        else:
            # Generic template
            code += '''
    # Could not auto-detect strategy pattern
    # Please use the conversion guide to manually convert
    # For now, using a simple buy and hold
    if position is None and index == 50:
        return 'buy'
'''

        code += '''
    return 'hold'
'''

        return code

    def _extract_number(self, text, indicator, occurrence=0, after_rsi=False):
        """Extract numeric parameter from Pine Script"""
        try:
            pattern = rf'{re.escape(indicator)}\([^,)]*,?\s*(\d+)'
            matches = re.findall(pattern, text)
            if matches and len(matches) > occurrence:
                return int(matches[occurrence])

            # Try to find standalone numbers
            pattern = r'\b(\d+)\b'
            matches = re.findall(pattern, text)
            if matches:
                # Filter out version numbers
                numbers = [int(m) for m in matches if int(m) not in [1, 5]]
                if numbers and len(numbers) > occurrence:
                    return numbers[occurrence]
        except:
            pass
        return None


def create_strategy_from_pinescript(pinescript_code):
    """
    Create a Python strategy function from Pine Script code

    Args:
        pinescript_code: Pine Script strategy code

    Returns:
        tuple: (function, error_message)
    """
    try:
        parser = PineScriptParser()
        python_code = parser.generate_python_code(pinescript_code)

        # Create function in local namespace
        local_namespace = {}
        exec(python_code, globals(), local_namespace)

        strategy_func = local_namespace.get('pine_script_strategy')
        if strategy_func:
            return strategy_func, None
        else:
            return None, "Failed to create strategy function"

    except Exception as e:
        return None, f"Error parsing Pine Script: {str(e)}"


if __name__ == "__main__":
    # Test the parser
    test_pine = """
    //@version=5
    strategy("EMA Cross", overlay=true)

    fastLength = input(12, "Fast EMA")
    slowLength = input(26, "Slow EMA")

    fastEMA = ta.ema(close, fastLength)
    slowEMA = ta.ema(close, slowLength)

    if ta.crossover(fastEMA, slowEMA)
        strategy.entry("Long", strategy.long)

    if ta.crossunder(fastEMA, slowEMA)
        strategy.close("Long")
    """

    parser = PineScriptParser()
    python_code = parser.generate_python_code(test_pine)
    print("Generated Python Code:")
    print(python_code)
