def calculo_final_cupons(df,
                        margem = 0.16,
                        valor_cupom = 20,
                        conversao_high = 0.10,
                        conversao_medium = 0.05,
                        conversao_low = 0.02,
                        valor_incremento_high = 50,
                        valor_incremento_medium = 50,
                        valor_incremento_low = 50,
                        missao_de_compra = 'AÇOUGUE'):
    
    df = df[df['MISSAO_COMPRA'] == missao_de_compra].copy()
    
    df['taxa_conversao'] = np.select(
        [df['SEGMENTO_ESTRATEGICO'] == 'HIGH', df['SEGMENTO_ESTRATEGICO'] == 'MEDIUM', df['SEGMENTO_ESTRATEGICO'] == 'LOW'],
        [conversao_high, conversao_medium, conversao_low],
        default=0)

    df['incremento_cupom'] = np.select(
        [df['SEGMENTO_ESTRATEGICO'] == 'HIGH', df['SEGMENTO_ESTRATEGICO'] == 'MEDIUM', df['SEGMENTO_ESTRATEGICO'] == 'LOW'],
        [valor_incremento_high, valor_incremento_medium, valor_incremento_low],
        default=0)

    df['margem_natural'] = df['taxa_conversao'] * df['TM'] * margem
    df['margem_com_cupom'] = (df['taxa_conversao'] * (df['TM'] +  df['incremento_cupom']) * margem) - valor_cupom
    df['reducao_margem'] = df['margem_com_cupom'] - df['margem_natural']

    def calculo_tabela(df, agrupamento):

        if agrupamento == 'Total':
            tabela_1 = (df.agg({'MISSAO_COMPRA': 'count', 'taxa_conversao': 'sum', 'margem_natural': 'sum', 'margem_com_cupom': 'sum', 'reducao_margem': 'sum' }).to_frame().T ) 
            tabela_1.insert(0, 'Total', 'Total')

        else:
            tabela_1 = (df.groupby(agrupamento, as_index=False)
                .agg({'MISSAO_COMPRA': 'count',
                    'taxa_conversao': 'sum',
                    'margem_natural': 'sum',
                    'margem_com_cupom': 'sum',
                    'reducao_margem': 'sum'})
            )
                
        tabela_1 = tabela_1.rename(columns={
                    'MISSAO_COMPRA': 'Total de Disparos',
                    'taxa_conversao': 'Uso de cupons',
                    'margem_natural': 'Margem Natural',
                    'margem_com_cupom': 'Margem com Cupom',
                    'reducao_margem': 'Redução de Margem'})
            

        tabela_1['Margem Natural Media'] = (
            tabela_1['Margem Natural']
            / tabela_1['Uso de cupons']
        )

        tabela_1['Margem com Cupom Media'] = (
            tabela_1['Margem com Cupom']
            / tabela_1['Uso de cupons']
        )

        tabela_1['Diferença de Margem Media'] = (
            tabela_1['Redução de Margem']
            / tabela_1['Uso de cupons']
        )

        tabela_exibicao = tabela_1.T.copy()

        # Uso de cupons como inteiro
        tabela_exibicao.loc['Uso de cupons'] = (
            tabela_exibicao.loc['Uso de cupons']
            .astype(float)
            .round()
            .astype(int)
        )

        # Formatação monetária
        linhas_monetarias = [
            'Margem Natural',
            'Margem com Cupom',
            'Redução de Margem',
            'Margem Natural Media',
            'Margem com Cupom Media',
            'Diferença de Margem Media'
        ]

        def moeda_br(x):
            return f'R$ {x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

        for linha in linhas_monetarias:
            tabela_exibicao.loc[linha] = (
                tabela_exibicao.loc[linha]
                .astype(float)
                .map(moeda_br)
            )

        return tabela_exibicao
    
    return calculo_tabela(df, 'Total'), calculo_tabela(df, 'MACROSSEGMENTO_PEOPLESCOPE'), calculo_tabela(df, 'SEGMENTO_ESTRATEGICO')