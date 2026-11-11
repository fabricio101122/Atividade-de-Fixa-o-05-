import os
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs('saida', exist_ok=True)

df = pd.read_csv('transacoes.csv', encoding='latin1')

df['valor'] = df['valor'].fillna(df.groupby('estado_cliente')['valor'].transform('median'))

df['data_transacao'] = pd.to_datetime(df['data_transacao']).dt.tz_localize('America/Sao_Paulo')
df['dia_semana'] = df['data_transacao'].dt.day_name()
df['mes'] = df['data_transacao'].dt.month

df['plataforma'] = 'Mobile'

df = df.drop_duplicates(keep='first').reset_index(drop=True)

risco_dict = {'C100': 'Baixo', 'C101': 'Alto', 'C102': 'Médio', 'C103': 'Baixo', 'C104': 'Médio'}
df['nivel_risco'] = df['id_cliente'].map(risco_dict)

df.to_csv('saida/transacoes_tratadas.csv', index=False, encoding='utf-8')

filtro = df[(df['mes'] == 9) & ((df['estado_cliente'] == 'SP') | (df['estado_cliente'] == 'RJ')) & (df['valor'] > 5000)]
filtro.to_csv('saida/filtro_setembro_sp_rj.csv', index=False, encoding='utf-8')

pivot = pd.pivot_table(df, values='valor', index='mes', columns='nivel_risco',
                       aggfunc='sum', margins=True, margins_name='Total', fill_value=0)
pivot.to_csv('saida/pivot_mes_risco.csv', encoding='utf-8')
print(pivot)

grupo = df.groupby('estado_cliente')['valor']
df['zscore'] = (df['valor'] - grupo.transform('mean')) / grupo.transform('std', ddof=0)
anomalias = df[df['zscore'] > 2.5]
anomalias.to_csv('saida/anomalias_zscore.csv', index=False, encoding='utf-8')
print('Anomalias:', len(anomalias))

diario = df.groupby(df['data_transacao'].dt.tz_localize(None).dt.normalize())['valor'].sum()
media_7 = diario.rolling(7).mean()

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(diario.index, diario.values, label='Total diário')
ax.plot(media_7.index, media_7.values, label='Média móvel 7 dias')
ax.set_ylim(bottom=0)
ax.set_title('Transações diárias e média móvel de 7 dias')
ax.set_xlabel('Data')
ax.set_ylabel('Valor (R$)')
ax.legend()
fig.savefig('saida/grafico_diario.png', dpi=150)
