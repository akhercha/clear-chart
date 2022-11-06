import sys
import os
import matplotlib.pyplot as plt

from dotenv import load_dotenv
from binance.client import Client

from modules.Movement import Movement
from modules.parser import parse_args

load_dotenv(".env")
API_KEY = os.environ.get("BINANCE_API_KEY")
API_SECRET = os.environ.get("BINANCE_API_SECRET")

INDEX_CLOSING_PRICE = 4
START_CANDLE_TIME = "2 year ago UTC"
CANDLE_TIME_FRAME = Client.KLINE_INTERVAL_1WEEK


def cut_in_movements(prices: list) -> list:
    """
    Cuts a sequence of price candles into big "movements" (lines).

    Args:
        prices (list): List of float representing the evolution of the prices.

    Returns:
        list: Return the list of the movements created.
    """
    i = 0
    moves = []
    while i < (len(prices) - 1):
        start = i
        if prices[i + 1] > prices[i]:
            while (i < len(prices) - 1) and (prices[i + 1] > prices[i]):
                i += 1
            moves.append(
                Movement(
                    "ASC",
                    prices[start],
                    prices[i],
                    abs(prices[start] - prices[i]),
                    i - start,
                )
            )
        else:
            while (i < len(prices) - 1) and (prices[i + 1] < prices[i]):
                i += 1
            if (i < len(prices) - 1) and (prices[i + 1] == prices[i]):
                i += 1
            moves.append(
                Movement(
                    "DESC",
                    prices[start],
                    prices[i],
                    abs(prices[start] - prices[i]),
                    i - start,
                )
            )
    return moves


def get_smoothed_movements(moves: list, big_delta: float, threshold=0.1) -> list:
    """
    Allows to summarize multiples movement into a big one.

    Args:
        moves (list): List of movements.
        big_delta (float): Difference between top & bottom price.
        threshold (float, optional): Allows to adjust how much we will smooth the
                                     movements. The lower it is, the less movements
                                     we will have. Defaults to 0.1.

    Returns:
        list: Summed up list of movements.
    """
    i = 1
    while i < len(moves):
        if (i < 1) or (i >= len(moves) - 2):
            i += 1
            continue
        m_percent = abs(moves[i].delta / big_delta)
        if m_percent < threshold:
            if moves[i].delta < moves[i + 1].delta:
                moves[i - 1].end = moves[i + 2].start
                moves[i - 1].candles += moves[i].candles
                moves[i - 1].candles += moves[i + 1].candles
                moves[i - 1].delta = round(
                    abs(moves[i - 1].end - moves[i - 1].start), 2
                )
            else:
                moves[i + 2].start = moves[i - 1].end
                moves[i + 2].candles += moves[i].candles
                moves[i + 2].candles += moves[i + 1].candles
                moves[i + 2].delta = round(
                    abs(moves[i + 2].end - moves[i + 2].start), 2
                )
            del moves[i]
            del moves[i]
            i -= 1
        i += 1
    return moves


def plot_price_chart(prices: list, moves=None):
    """
    Uses matplotlib to print the price chart along with the movements.

    Args:
        prices (list): List of float representing the evolution of the prices.
        moves (list, optional): List of the movements to print. Defaults to None.
    """
    X = list(range(1, len(prices) + 1))
    plt.plot(X, prices, color="blue")
    if moves is not None:
        display_movements(moves, prices)
    plt.show()


def display_movements(moves: list, prices: list):
    """
    Uses matplotlib to print the movements created from the script.

    Args:
        moves (list): List of movements.
        prices (list): List of float representing the evolution of the prices.
    """
    number_of_candles = 0
    for m in moves:
        number_of_candles += m.candles
    X = list(range(1, number_of_candles + 1))
    z = 1
    for m in moves:
        plt.plot(
            [z, z + m.candles],
            [m.start, m.end],  # linestyle='dashed',
            color=("green" if m.type == "ASC" else "red"),
        )
        z += m.candles
    smoothed_moves = get_smoothed_movements(moves, max(prices) - min(prices))
    z = 1
    for m in smoothed_moves:
        plt.plot(
            [z, z + m.candles], [m.start, m.end], linestyle="dashed", color="orange"
        )
        z += m.candles


def main():
    """
    Main function.
    """
    cli_args = parse_args()
    symbol_pair = cli_args.pair
    client = Client(API_KEY, API_SECRET)
    plt.title(f"Pair {symbol_pair}")
    plt.xlabel(f"Time since {START_CANDLE_TIME}")
    plt.ylabel("Price")
    prices = [
        float(k[INDEX_CLOSING_PRICE])
        for k in client.get_historical_klines(
            symbol_pair, CANDLE_TIME_FRAME, START_CANDLE_TIME
        )
    ]
    moves = cut_in_movements(prices)
    plot_price_chart(prices, moves)


if __name__ == "__main__":
    main()
