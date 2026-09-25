from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'data'/'processed'

def test_financial_has_latest_quarters():
    df=pd.read_csv(D/'financial_quarterly.csv')
    assert {'1T25','2T25','3T25','4T25','1T26','2T26'}.issubset(set(df.period))

def test_ebitda_margin_consistency():
    df=pd.read_csv(D/'financial_quarterly.csv').dropna(subset=['revenue','ebitda','ebitda_margin'])
    assert ((df.ebitda/df.revenue)-df.ebitda_margin).abs().max() < 1e-3

def test_cashflow_latest():
    df=pd.read_csv(D/'cashflow_quarterly.csv')
    assert {'1T26','2T26'}.issubset(set(df.period))
