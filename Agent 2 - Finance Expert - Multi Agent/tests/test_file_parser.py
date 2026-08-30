from finance_multi_agent.utils.file_parser import parse_stock_file


def test_parse_stock_file(tmp_path):
    p = tmp_path / "stocks.txt"
    p.write_text("RELIANCE.NS, TCS.NS, badticker, RELIANCE.NS", encoding="utf-8")
    tickers, invalid = parse_stock_file(str(p))
    assert tickers == ["RELIANCE.NS", "TCS.NS"]
    assert invalid == ["BADTICKER"]
