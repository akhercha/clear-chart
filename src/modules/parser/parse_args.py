import argparse


def parse_args():
    """
    Uses argparse to parse the CLI arguments of the main script.
    Returns the arguments.
    """
    parser = argparse.ArgumentParser(description="description of script")

    parser.add_argument(
        "pair",
        type=str,
        help="binance pair to show (ex: SUSHIUSDT, ETHBTC..)",
    )

    return parser.parse_args()
