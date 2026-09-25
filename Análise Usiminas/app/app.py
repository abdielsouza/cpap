import streamlit as st
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'data'/'processed'
st.set_page_config(page_title='Usiminas — Performance 2025-2026',layout='wide')
st.title('Usiminas — recuperação operacional e financeira')
st.caption('Estudo exploratório baseado na planilha Base de Dados para Modelagem 2T26.')
f=pd.read_csv(D/'financial_quarterly.csv'); cf=pd.read_csv(D/'cashflow_quarterly.csv'); cap=pd.read_csv(D/'capex_quarterly.csv'); wc=pd.read_csv(D/'working_capital_quarterly.csv'); debt=pd.read_csv(D/'debt_quarterly.csv'); cpv=pd.read_csv(D/'cpv_quarterly.csv')
periods=['1T25','2T25','3T25','4T25','1T26','2T26']; x=f[f.period.isin(periods)].copy()
for y in [cf,cap,wc]: x=x.merge(y,on='period',how='left')
latest=x.iloc[-1]
c1,c2,c3,c4=st.columns(4)
c1.metric('Receita líquida',f"R$ {latest.revenue/1000:,.0f} mi")
c2.metric('EBITDA',f"R$ {latest.ebitda/1000:,.0f} mi",f"{latest.ebitda_margin:.1%} da receita")
c3.metric('Lucro líquido',f"R$ {latest.net_income/1000:,.0f} mi")
c4.metric('Caixa operacional',f"R$ {latest.operating_cash_flow/1000:,.0f} mi")
col1,col2=st.columns(2)
with col1:
 st.subheader('Receita e EBITDA')
 fig,ax=plt.subplots(); ax.plot(x.period,x.revenue/1000,marker='o',label='Receita'); ax.plot(x.period,x.ebitda/1000,marker='o',label='EBITDA'); ax.set_ylabel('R$ milhões'); ax.legend(); st.pyplot(fig)
with col2:
 st.subheader('Margens')
 fig,ax=plt.subplots(); ax.plot(x.period,x.gross_margin*100,marker='o',label='Margem bruta'); ax.plot(x.period,x.ebitda_margin*100,marker='o',label='Margem EBITDA'); ax.plot(x.period,x.net_margin*100,marker='o',label='Margem líquida'); ax.set_ylabel('%'); ax.legend(); st.pyplot(fig)
col1,col2=st.columns(2)
with col1:
 st.subheader('Fluxo de caixa e CAPEX')
 fig,ax=plt.subplots(); ax.bar(x.period,x.operating_cash_flow/1000,label='FCO'); ax.plot(x.period,x.capex_mn,marker='o',label='CAPEX'); ax.set_ylabel('R$ milhões'); ax.legend(); st.pyplot(fig)
with col2:
 st.subheader('Capital de giro')
 fig,ax=plt.subplots(); ax.plot(x.period,x.working_capital_bn,marker='o'); ax.set_ylabel('R$ bilhões'); st.pyplot(fig)

st.subheader('Composição do CPV')
cp=cpv[cpv.period.isin(periods)].pivot_table(index='period',columns='cost_component',values='share',aggfunc='last')
fig,ax=plt.subplots(); cp.plot.area(ax=ax); ax.set_ylabel('Participação no CPV'); ax.legend(loc='center left',bbox_to_anchor=(1,0.5)); st.pyplot(fig)

st.subheader('Dívida líquida')
debt['date']=pd.to_datetime(debt.date); d=debt[debt.date>=pd.Timestamp('2025-01-01')].copy(); st.dataframe(d.assign(gross_debt_mn=d.gross_debt/1000,cash_mn=d.cash/1000,net_debt_mn=d.net_debt/1000)[['date','gross_debt_mn','cash_mn','net_debt_mn']],use_container_width=True)

st.info('Interpretação: este dashboard é descritivo e exploratório. Associação entre variáveis não deve ser interpretada como causalidade.')
