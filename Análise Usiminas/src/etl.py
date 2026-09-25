from pathlib import Path
import re, shutil
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw' / 'Base de Dados para Modelagem 2T26.xlsx'
OUT = ROOT / 'data' / 'processed'
Q = re.compile(r'^[1-4]T\d{2}$')

def qcols(df, row):
    return [(j, v) for j, v in df.iloc[row-1].items() if isinstance(v, str) and Q.match(v)]

def period_sort(s):
    return pd.to_datetime(s.str[-2:].astype(int).map(lambda x: 2000+x).astype(str) + '-' + s.str[0].astype(int).map({1:'03',2:'06',3:'09',4:'12'}) + '-01')

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    # DRE
    df=pd.read_excel(RAW,sheet_name='DRE Consolidada TRI',header=None); cols=qcols(df,2)
    rows=[]
    metric_rows=[3,6,7,8,14,15,20,22,23,27,28,29,30]
    for r in metric_rows:
        label=str(df.iat[r-1,1]).strip()
        for j,q in cols:
            v=df.iat[r-1,j]
            if pd.notna(v): rows.append([q,label,float(v)])
    dre=pd.DataFrame(rows,columns=['period','metric','value']).pivot_table(index='period',columns='metric',values='value',aggfunc='last').reset_index()
    dre=dre.rename(columns={'Receita Líquida de Vendas':'revenue','Custo dos Produtos Vendidos':'cogs','Lucro ou Prejuízo Bruto':'gross_profit','Margem Bruta':'gross_margin','Lucro Operacional antes das Despesas Financeiras':'operating_profit','Margem Operacional':'operating_margin','Lucro ou Prejuízo Operacional':'ebt','Lucro ou Prejuízo Líquido do Exercício':'net_income','Margem Líquida':'net_margin','EBITDA (Instrução CVM 527)':'ebitda','Margem EBITDA':'ebitda_margin','EBITDA Ajustado (proporcional de controladas em conjunto)':'adjusted_ebitda','Margem EBITDA Ajustado':'adjusted_ebitda_margin'})
    dre['sort']=period_sort(dre.period); dre=dre.sort_values('sort').drop(columns='sort'); dre.to_csv(OUT/'financial_quarterly.csv',index=False)
    # Cash flow
    df=pd.read_excel(RAW,sheet_name='Fluxo de Caixa TRI',header=None); cols=qcols(df,2); wanted=['Caixa Proveniente das Atividades Operacionais','Caixa Líquido Proveniente das Atividades Operacionais','Caixa Líquido Aplicado nas Atividades de Investimentos','Caixa Líquido Proveniente das (Aplicado nas) Atividades de Financiamentos','Aumento (redução) Líquido de Caixa e Equivalentes de Caixa']; rows=[]
    for i in range(len(df)):
        label=str(df.iat[i,0]).strip() if pd.notna(df.iat[i,0]) else ''
        if label in wanted:
            for j,q in cols:
                v=df.iat[i,j]
                if pd.notna(v): rows.append([q,label,float(v)])
    cf=pd.DataFrame(rows,columns=['period','metric','value']).pivot_table(index='period',columns='metric',values='value',aggfunc='last').reset_index().rename(columns={wanted[0]:'operating_cash_before_interest_tax',wanted[1]:'operating_cash_flow',wanted[2]:'investing_cash_flow',wanted[3]:'financing_cash_flow',wanted[4]:'net_cash_change'}); cf['sort']=period_sort(cf.period); cf=cf.sort_values('sort').drop(columns='sort'); cf.to_csv(OUT/'cashflow_quarterly.csv',index=False)
    # generic sheets
    def simple(sheet, header_row, label_col, row_filter=None):
        d=pd.read_excel(RAW,sheet_name=sheet,header=None); cs=qcols(d,header_row); rr=[]
        for i in range(header_row,len(d)):
            lab=d.iat[i,label_col]
            if pd.isna(lab) or (row_filter and not row_filter(str(lab).strip())): continue
            for j,q in cs:
                v=d.iat[i,j]
                if pd.notna(v) and isinstance(v,(int,float,np.integer,np.floating)): rr.append([q,str(lab).strip(),float(v)])
        return pd.DataFrame(rr,columns=['period','metric','value'])
    cap=simple('CAPEX',2,1,lambda x:x=='Total').rename(columns={'metric':'segment','value':'capex_mn'}); cap.to_csv(OUT/'capex_quarterly.csv',index=False)
    wg=simple('Capital de Giro',2,1,lambda x:x=='Capital de Giro').rename(columns={'metric':'indicator','value':'working_capital_bn'}); wg[['period','working_capital_bn']].to_csv(OUT/'working_capital_quarterly.csv',index=False)
    cpv=simple('CPV Siderurgia',3,1,lambda x:x not in ['Custo do Produto Vendido (CPV - %)','R$ mi','R$/ton']); cpv.rename(columns={'metric':'cost_component','value':'share'}).to_csv(OUT/'cpv_quarterly.csv',index=False)
    prod=simple('Vendas por Produto',3,1,lambda x:x not in ['Total','Mercado Interno (mil toneladas)','Exportações (mil toneladas)']).rename(columns={'metric':'product','value':'thousand_tons'}); prod.to_csv(OUT/'product_sales_quarterly.csv',index=False)
    seg=simple('Vendas por Segmento',3,1,lambda x:x in ['Automotivo','Grande Rede','Industrial']).rename(columns={'metric':'segment','value':'share'}); seg.to_csv(OUT/'segment_mix_quarterly.csv',index=False)
    # debt dates
    d=pd.read_excel(RAW,sheet_name='Dívida',header=None); rr=[]
    for j in range(2,d.shape[1]):
        h=d.iat[1,j]
        if pd.isna(h): continue
        vals=[d.iat[r,j] for r in (8,9,10)]
        if all(pd.notna(v) and isinstance(v,(int,float,np.integer,np.floating)) for v in vals):
            dt=pd.to_datetime(h,errors='coerce',dayfirst=True)
            if pd.isna(dt) and isinstance(h,str): dt=pd.to_datetime(h,format='%d-%b-%y',errors='coerce')
            rr.append([dt,*map(float,vals)])
    debt=pd.DataFrame(rr,columns=['date','gross_debt','cash','net_debt']).dropna(subset=['date']); debt.to_csv(OUT/'debt_quarterly.csv',index=False)
    # raw production sheet
    pd.read_excel(RAW,sheet_name='Produção e Capacidades SID',header=None).to_csv(OUT/'production_capacity_raw.csv',index=False,header=False)

if __name__=='__main__': build()
