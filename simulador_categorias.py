def calculo_final_cupons(df,
                        margem = 0.16,
                        valor_cupom = 20,
                        gasto_minimo = 100,
                        conversao_high = 0.10,
                        conversao_medium = 0.05,
                        conversao_low = 0.02,
                        valor_incremento_high = 50,
                        valor_incremento_medium = 50,
                        valor_incremento_low = 50,
                        missao_de_compra = 'AÇOUGUE'):
    
    import numpy as np
    import pandas as pd

    df = df[df['MISSAO_COMPRA'] == missao_de_compra].copy()
    
    df['taxa_conversao'] = np.select(
        [df['Segmento Estratégico'] == 'HIGH', df['Segmento Estratégico'] == 'MEDIUM', df['Segmento Estratégico'] == 'LOW'],
        [conversao_high, conversao_medium, conversao_low],
        default=0)

    df['incremento_cupom'] = np.select(
        [df['Segmento Estratégico'] == 'HIGH', df['Segmento Estratégico'] == 'MEDIUM', df['Segmento Estratégico'] == 'LOW'],
        [valor_incremento_high, valor_incremento_medium, valor_incremento_low],
        default=0)
    
    # Flag indicando se o cliente atinge o gasto mínimo mesmo com o incremento máximo do cupom
    df['flg_conversao'] = np.where((df['TM_MISSAO'] + df['incremento_cupom']) < gasto_minimo, 0, 1 )

    # Incremento real necessário para atingir o gasto mínimo (não o incremento "cheio" do cupom)
    df['incremento_cupom_real'] = np.where(
        df['flg_conversao'] == 1,
        df['incremento_cupom'],
        0)
    
    # Zera a taxa de conversão quando o cliente não consegue atingir o gasto mínimo
    df['taxa_conversao'] = np.where(
        df['flg_conversao'] == 1,
        df['taxa_conversao'], 0)

    df['margem_natural'] = np.where(
        df['flg_conversao'] == 1,
        df['taxa_conversao'] * df['TM'] * margem, 0)

    df['margem_com_cupom'] = np.where(
        df['flg_conversao'] == 1,
        df['taxa_conversao'] * (((df['TM'] + df['incremento_cupom_real']) * margem) - valor_cupom), 0)

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
            

        tabela_1['Taxa de Uso do Cupom'] = (
            tabela_1['Uso de cupons']
            / tabela_1['Total de Disparos']
        )
        
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

        tabela_exibicao = tabela_1.copy()
        if agrupamento != 'Total':
            tabela_exibicao = tabela_exibicao.set_index(agrupamento)
        tabela_exibicao = tabela_exibicao.T

        # Ordem de colunas
        if agrupamento == 'Total':
            ordem_colunas = ['Total de Disparos','Uso de cupons','Taxa de Uso do Cupom','Margem Natural','Margem com Cupom','Redução de Margem','Margem Natural Media','Margem com Cupom Media','Diferença de Margem Media']
        else:
            ordem_colunas = ['Total de Disparos','Uso de cupons','Taxa de Uso do Cupom','Margem Natural','Margem com Cupom','Redução de Margem','Margem Natural Media','Margem com Cupom Media','Diferença de Margem Media']
        
        tabela_exibicao = tabela_exibicao.reindex(ordem_colunas)

        if agrupamento == 'Segmento Estratégico':
            tabela_exibicao = tabela_exibicao[['HIGH', 'MEDIUM', 'LOW']]

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
        
        # Formatação porcentagem
        linhas_porcentagem = ['Taxa de Uso do Cupom']

        def percentual_br(x):
            return f'{x:.2%}'.replace('.', ',')

        for linha in linhas_porcentagem:
            tabela_exibicao.loc[linha] = (
                tabela_exibicao.loc[linha]
                .astype(float)
                .map(percentual_br)
            )
        
        return tabela_exibicao
    
    return calculo_tabela(df, 'Total'), calculo_tabela(df, 'Macrossegmento PeopleScope'), calculo_tabela(df, 'Segmento Estratégico')