from config import CODE
from engine.paper_engine import PaperTrader

if __name__ == "__main__":
    trader = PaperTrader(CODE)
    print("Starting Paper Trading...")
    trader.run()