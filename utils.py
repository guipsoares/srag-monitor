# type: ignore
import polars as pl
import pandas as pd
import pathlib
from datetime import datetime

PATH = pathlib.Path(__file__).parent.resolve()

ESTADOS = [
    'Todos', 'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT',
    'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
    'SP', 'SE', 'TO'
]


list_pos = [
    'POS_FLUA', 'POS_FLUB', 'POS_SARS2', 'POS_VSR',
    'POS_PARA1', 'POS_PARA2', 'POS_PARA3', 'POS_PARA4' ,
    'POS_ADENO', 'POS_METAP', 'POS_BOCA', 'POS_RINO', 'POS_OUTROS'
]


ANOS = [2022, 2023,'Todos']

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

    pos = pl.scan_csv(f'{PATH}/data/positive_distribution_dts.csv')
    df = (pos
        .filter(pl.col('POS_SUM') > 0)
        .with_columns(
        [
            pl.when(pl.col('IDADE_ANO') <= 16)
            .then('CRIANÇA')
            .when(pl.col('IDADE_ANO').is_between(17, 60))
            .then('ADULTO')
            .otherwise('IDOSO')
            .alias('FAIXA_ETARIA'),
        ])
        .groupby(
            ['DT_FILE','ANO_SIN_PRI','SEM_SIN_PRI'] + group_by_
        )
        .agg(
            [
                pl.col('POS_FLUA').sum(),
                pl.col('POS_FLUB').sum(),
                pl.col('POS_SARS2').sum(),
                pl.col('POS_VSR').sum(),
                pl.col('POS_PARA1').sum(),
                pl.col('POS_PARA2').sum(),
                pl.col('POS_PARA3').sum(),
                pl.col('POS_PARA4').sum(),
                pl.col('POS_ADENO').sum(),
                pl.col('POS_METAP').sum(),
                pl.col('POS_BOCA').sum(),
                pl.col('POS_RINO').sum(),
                pl.col('POS_OUTROS').sum(),
                pl.col('POS_SUM').sum(),
            ]
        )
    ).collect().to_pandas()

    df = (df.rename(
        columns = {'POS_SUM': 'TESTES'}
    )
    .reset_index()
    .assign(
        POS_FLUA = lambda x: x['POS_FLUA']/x['TESTES'],
        POS_FLUB = lambda x: x['POS_FLUB']/x['TESTES'],
        POS_SARS2 = lambda x: x['POS_SARS2']/x['TESTES'],
        POS_VSR = lambda x: x['POS_VSR']/x['TESTES'],
        POS_PARA1 = lambda x: x['POS_PARA1']/x['TESTES'],
        POS_PARA2 = lambda x: x['POS_PARA2']/x['TESTES'],
        POS_PARA3 = lambda x: x['POS_PARA3']/x['TESTES'],
        POS_PARA4 = lambda x: x['POS_PARA4']/x['TESTES'],
        POS_ADENO = lambda x: x['POS_ADENO']/x['TESTES'],
        POS_METAP = lambda x: x['POS_METAP']/x['TESTES'],
        POS_BOCA = lambda x: x['POS_BOCA']/x['TESTES'],
        POS_RINO = lambda x: x['POS_RINO']/x['TESTES'],
        POS_OUTROS = lambda x: x['POS_OUTROS']/x['TESTES'],
        DT_SIN_PRI = lambda x: x.apply(lambda x: datetime.fromisocalendar(int(x['ANO_SIN_PRI']),int(x['SEM_SIN_PRI']), 1), axis=1),
        DT_FILE = lambda x: pd.to_datetime(x['DT_FILE'], format='%Y-%m-%d'),
        ANO_FILE = lambda x: (x['DT_FILE'].dt.isocalendar().year).astype(int), 
        SEM_FILE = lambda x: (x['DT_FILE'].dt.isocalendar().week).astype(int),
        DT_SEM_FILE = lambda x: x.apply(lambda x: datetime.fromisocalendar(int(x['ANO_FILE']),int(x['SEM_FILE']), 1), axis=1),
        DIF_FILE_SIN = lambda x: ((x['DT_SEM_FILE'] - x['DT_SIN_PRI']).dt.days/7).astype(int),
    )
    .sort_values(['DT_SIN_PRI','DT_FILE'], ascending=[True,True])
)
    if faixa_etaria != 'Todos':
        df = df[df['FAIXA_ETARIA'] == str.upper(faixa_etaria)]

    if estado != 'Todos':
        df = df[df['SG_UF_NOT'] == estado]
    return df


def _update_index(df):
    df.index = pd.to_datetime(df['DT_SIN_PRI'], format='%Y-%m-%d')
    df = df.drop_duplicates(subset='DT_SIN_PRI', keep='last')
    return df
