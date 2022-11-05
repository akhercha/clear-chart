class Movement:
    """_summary_
    """
    def __init__(self, type, start, end, delta, candles):
        self.type = type
        self.start = start
        self.end = end
        self.delta = round(delta, 2)
        self.candles = candles

    def __str__(self):
        return (
            f"Movement {self.type} : from {self.start} to {self.end} "
            f"({'+' if self.type == 'ASC' else '-'} {self.delta}$) "
            f"with {self.candles} candles."
        )
