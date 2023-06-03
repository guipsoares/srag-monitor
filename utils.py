# type: ignore
import polars as pl
import pandas as pd
import pathlib


PATH = pathlib.Path(__file__).parent.resolve()

ESTADOS = [
    'Todos', 'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT',
    'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
    'SP', 'SE', 'TO'
]

ANOS = [2020, 2021, 2022, 2023,'Todos']

FAIXAS_ETARIAS = ['Adulto', 'Idoso', 'Criança', 'Todos']


def generate_dataframe(estado: str, faixa_etaria: str) -> pd.DataFrame:
    
    df = _group_by_columns(estado, faixa_etaria)
    df = _update_index(df)

    return df


def _group_by_columns(estado, faixa_etaria) -> pd.DataFrame:
    group_by_ = []
    if estado != 'Todos':
        group_by_ = group_by_ + ['SG_UF_NOT']

    if faixa_etaria != 'Todos':
        group_by_ = group_by_ + ['FAIXA_ETARIA']

    pos = pl.scan_parquet(f'{PATH}/data/df_positivos_att.parquet')
    df = (pos.
        with_columns(
        [
            pl.when(pl.col('IDADE_ANO') <= 16)
            .then('CRIANÇA')
            .when(pl.col('IDADE_ANO').is_between(17, 60))
            .then('ADULTO')
            .otherwise('IDOSO')
            .alias('FAIXA_ETARIA'),
        ])
        .groupby(
            ['ANO_SIN_PRI', 'SEM_SIN_PRI', 'SEM_PRI'] + group_by_
        )
        .agg(
            [
                pl.count().alias("N_INTERNACOES"),
                pl.col('POS_FLUA').mean(),
                pl.col('POS_FLUB').mean(),
                pl.col('POS_SARS2').mean(),
                pl.col('POS_VSR').mean(),
                pl.col('POS_PARA1').mean(),
                pl.col('POS_PARA2').mean(),
                pl.col('POS_PARA3').mean(),
                pl.col('POS_ADENO').mean(),
                pl.col('POS_DEMAIS').mean()
            ]
        )
        .sort(['ANO_SIN_PRI', 'SEM_SIN_PRI'])
        .filter(pl.col('ANO_SIN_PRI') >= 2020)
    ).collect().to_pandas()

    if faixa_etaria != 'Todos':
        df = df[df['FAIXA_ETARIA'] == str.upper(faixa_etaria)]

    if estado != 'Todos':
        df = df[df['SG_UF_NOT'] == estado]

    return df


def _update_index(df):
    df['tmp'] = df['SEM_PRI'].apply(lambda x: x.split('/')[1])   
    df.index = pd.to_datetime(df['tmp'], format='%Y-%m-%d')

    return df
