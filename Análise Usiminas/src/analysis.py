from pathlib import Path
import pandas as pd, numpy as np
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'data'/'processed'

def load():
    f=pd.read_csv(D/'financial_quarterly.csv'); c=pd.read_csv(D/'cashflow_quarterly.csv'); cap=pd.read_csv(D/'capex_quarterly.csv'); wc=pd.read_csv(D/'working_capital_quarterly.csv'); debt=pd.read_csv(D/'debt_quarterly.csv'); cpv=pd.read_csv(D/'cpv_quarterly.csv'); prod=pd.read_csv(D/'product_sales_quarterly.csv'); return f,c,cap,wc,debt,cpv,prod

def recovery():
    f,c,cap,wc,debt,cpv,prod=load(); periods=['1T25','2T25','3T25','4T25','1T26','2T26']; x=f[f.period.isin(periods)].copy()
    for y in [c,cap,wc]: x=x.merge(y,on='period',how='left')
    cp=cpv[cpv.cost_component.isin(['Carvão e coque','Energia e Combustíveis','Mão de Obra Total','Minérios'])].pivot_table(index='period',columns='cost_component',values='share',aggfunc='last').reset_index(); x=x.merge(cp,on='period',how='left'); x['free_cash_flow_proxy_mn']=(x.operating_cash_flow-x.capex_mn*1000)/1000
    return x

def correlation():
    x=recovery(); cols=['ebitda_margin','revenue','operating_cash_flow','capex_mn','working_capital_bn','Carvão e coque','Energia e Combustíveis','Mão de Obra Total','Minérios']; return x[cols].corr()['ebitda_margin'].sort_values(ascending=False)
