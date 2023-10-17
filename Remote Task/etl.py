# 1. Leer datos de la base del raquel y crear el dataset unificado y mandarlo a un bucket de s3

import pyodbc
import pandas as pd
import datetime
from datetime import date, timedelta
import boto3
import io
from credentials import Server, UID, PWD, aws_access_key_id, aws_secret_access_key, region_name

cnxn_str = ("Driver={SQL Server};"
            f"Server={Server};"
            "Database=Raico;"
            f"UID={UID};"
            f"PWD={PWD};")


class ETL:

    @staticmethod
    def extract():
        '''Extrae la data del sistema del raquel'''

        cnxn = pyodbc.connect(cnxn_str)

        print('Connection to local db done')

        query_guias = '''
                  SELECT [Guias_Id]
                    ,[Guias_Numero]
                    ,[Guias_Fecha]
                    ,Guias.Motivos_Id
                    ,[Guias_Peso]
                    ,[Guias_VolLargo]
                    ,[Guias_VolAncho]
                    ,[Guias_VolAlto]
                    ,[Guias_PesoVol]
                    ,Guias.Clientes_Id
                    ,[Guias_ExpoTotVta]
                    ,[Guias_ImpoTotVta]
                    ,[Guias_VentaI]
                FROM [Raico].[dbo].[Guias]
                WHERE Guias_Fecha> '2019' 
                '''

        df_guias = pd.read_sql_query(query_guias, cnxn)

        query_motivos = '''
                    select Motivos_Id, MotivosFac.MotivosFac_Id, MotivosFac_Nombre
                    from motivos
                    inner join MotivosFac
                    on MotivosFac.MotivosFac_Id= Motivos.MotivosFac_Id
                    '''
        df_motivos = pd.read_sql_query(query_motivos, cnxn)

        df_guias['Guias_Fecha'] = pd.to_datetime(df_guias['Guias_Fecha'])

        print('Data Extraction done')

        return df_guias, df_motivos

    def transform(df_guias, df_motivos):
        '''Prepara y limpia los datos para el modelo Glounts'''

        dic_motivos = dict(
            df_motivos[['Motivos_Id', 'MotivosFac_Nombre']].values)
        df_guias['unique_id'] = df_guias['Motivos_Id'].map(dic_motivos)

        df = df_guias
        df.reset_index(inplace=True)
        df.drop(columns='index', inplace=True)
        df['Guias_Fecha'] = pd.to_datetime(df['Guias_Fecha'])

        df.rename(columns={'Guias_Peso': 'y',
                           'Guias_Fecha': 'ds'}, inplace=True)

        # agrupamos por semana => porque las entradas estan separadas, asi q nos quedamos con el total de kilos por fecha
        df = df.groupby(['unique_id', pd.Grouper(key='ds', freq='W')])[
            'y'].sum().reset_index()

        end_date = pd.to_datetime(date(2023, 9, 23))
        start_date = pd.to_datetime(date(2019, 1, 1))

        df = df.loc[(df['ds'] >= start_date)]
        df = df.loc[(df['ds'] < end_date)]

        df = df[['ds', 'unique_id', 'y']]

        # hay q renombrar los nombres originales por los unique_id establecidos

        lista_df = ['impo_1', 'impo_2', 'impo_3', 'impo_4', 'impo_5', 'impo_6', 'impo_7',
                    'expo_1', 'expo_2', 'expo_3', 'expo_4', 'expo_5']

        nombres_motivos = ['USA FLAT', 'ORIENTE UPS', 'CHINA LATIN LOGISTIC  CO via UPS/FEDEX', 'EUROPA UPS', 'Courier Oriente FLAT Wish/Latin logistic', 'Impo Geobox Flat ', 'UPS MERCOSUR',
                           'Exporta Simple - Puerta-Aeropuerto', 'CARGA AEREA EXPO PREPAID', 'CARGA AEREA EXPO - Q', '4-Expo - Fedex Economy', '6-Expo-UPS Express']

        dic_num_motivos = {nombres_motivos[i]: lista_df[i]
                           for i in range(len(lista_df))}

        df['unique_id'] = df['unique_id'].map(dic_num_motivos)

        # verificamos que esten mapeados los 12 motivos de interes
       # print(df.unique_id.unique())

        df.dropna(inplace=True)
        df.reset_index(inplace=True)
        df.drop(columns='index', inplace=True)

        df['y'] = df['y'].astype(int)

        # Debo chequear que para cada fecha de la semana haya un valor en kilos y si no lo hay que se complete con 0 porque los datos para el modelo deben ser continuos

        # Crea un rango de fechas semanal
        rango_fechas = pd.date_range(start=start_date, end=end_date, freq='W')

        # Crea un DataFrame con todas las combinaciones posibles de 'ds' y 'unique_id' en el rango de fechas
        combinaciones = pd.MultiIndex.from_product(
            [rango_fechas, df['unique_id'].unique()], names=['ds', 'unique_id'])
        df_combinado = pd.DataFrame(index=combinaciones).reset_index()

        # Fusiona tu DataFrame original con el DataFrame combinado para llenar los valores faltantes
        df2 = df_combinado.merge(df, on=['ds', 'unique_id'], how='left')

        # Llena los valores faltantes con 0
        df2['y'] = df2['y'].fillna(0)

        print('Data Transformation done')

        return df2

    def load(df):
        '''Sube la data limpia a un bucket de s3'''

        # Crea un cliente de S3
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key, region_name=region_name)

        # Nombre de tu bucket en S3
        bucket_name = 'proyectotati'

        # Convierte el DataFrame en un archivo CSV (u otro formato si prefieres)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        # Nombre que tendrá el archivo en S3
        s3_path = 'pre_trained_data/data.csv'

        # Carga el archivo en S3
        s3.upload_fileobj(io.BytesIO(
            csv_buffer.getvalue().encode()), bucket_name, s3_path)

        print('Data loaded done')
        