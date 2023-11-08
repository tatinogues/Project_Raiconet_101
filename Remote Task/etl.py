# 1. Leer datos de la base del raquel y crear el dataset unificado y mandarlo a un bucket de s3

import pyodbc
import pandas as pd
import datetime
from datetime import date, timedelta
import boto3
import numpy as np
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

        query_guias = '''  SELECT [Guias_Id]
                        ,[Guias_Numero]
                        ,[Guias_Fecha]
                        ,Guias.Motivos_Id
			            ,Clientes_Codigo
                        ,Clientes_Nombre
                        ,[Guias_Peso]
                        ,[Guias_VolLargo]
                        ,[Guias_VolAncho]
                        ,[Guias_VolAlto]
                        ,[Guias_PesoVol]
                        ,[Guias_FOB]
                        ,[Guias_ExpoTotVta]
                        ,[Guias_ImpoTotVta]
                        ,[Guias_VentaI]
                        FROM Guias, Clientes
                        WHERE Guias_Fecha> '2019' and Clientes.Clientes_Id= Guias.Clientes_Id
                        '''
        #    and MotivosFac.MotivosFac_Id= Guias.Motivos_Id
        df_guias = pd.read_sql_query(query_guias, cnxn)
        
        query_motivos = '''
                    select Motivos_Id, MotivosFac.MotivosFac_Id, MotivosFac_Nombre, MotivosFac_Codigo
                    from motivos
                    inner join MotivosFac
                    on MotivosFac.MotivosFac_Id= Motivos.MotivosFac_Id
                    '''
        df_motivos = pd.read_sql_query(query_motivos, cnxn)
        
        dic_motivos = dict(df_motivos[['Motivos_Id', 'MotivosFac_Nombre']].values)
        dic_motivos_codigo = dict(df_motivos[['Motivos_Id', 'MotivosFac_Codigo']].values)
        
        df_guias['unique_id'] = df_guias['Motivos_Id'].map(dic_motivos)
        df_guias['Codigo Motivo'] = df_guias['Motivos_Id'].map(dic_motivos_codigo)

        df_guias['Guias_Fecha'] = pd.to_datetime(df_guias['Guias_Fecha'])
        
        print('Data Extraction done :)')

        return df_guias

    def transform(df_guias):
        '''Prepara y limpia los datos para el modelo Glounts'''
        df = df_guias
        df.reset_index(inplace=True)
        df.drop(columns='index', inplace=True)
        df['Guias_Fecha'] = pd.to_datetime(df['Guias_Fecha'])
        df['peso_facturable']= np.maximum(df['Guias_Peso'], df['Guias_PesoVol'])

        df.rename(columns={'peso_facturable': 'y',
                           'Guias_Fecha': 'ds'}, inplace=True)

        # agrupamos por semana => porque las entradas estan separadas, asi q nos quedamos con el total de kilos por fecha
        df = df.groupby(['unique_id', pd.Grouper(key='ds', freq='W')])['y'].sum().reset_index()

        end_date = pd.to_datetime(date.today())
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

        print('Data Transformation for model done')

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

        print('Glounts Data loaded done')
        
    ### segundo proceso -> limpiar la data extraida para la seccion analytics 
    
    def clean_analytics(df_guias):
    

        dic_motivos_tipo= {506: 'Impo',510: 'Impo',557: 'Impo',507: 'Impo',556: 'Impo',589: 'Impo',508: 'Impo',509: 'Impo',505: 'Impo',553: 'Impo',600: 'Impo',550: 'Impo',598: 'Impo',571: 'Impo',572: 'Impo',544: 'Impo',
                          528: 'Impo',594: 'Impo',599: 'Impo',516: 'Impo',409: 'Impo',581: 'Impo',582: 'Impo',111: 'Expo',112: 'Expo',113: 'Expo',114: 'Expo',116: 'Expo',130: 'Expo',
                          131: 'Expo',132: 'Expo',141: 'Expo',150: 'Expo',152: 'Expo',200: 'Expo',202: 'Expo',220: 'Expo',222: 'Expo',223: 'Expo'}
        dic_motivos_tipo2= {506: 'Carga',510: 'Carga',557: 'Carga',507: 'Carga',556: 'Carga',589: 'Carga',508: 'Carga',509: 'Carga',505: 'Carga',553: 'Carga',600: 'Courier Impo',550: 'Courier Impo',
                           598: 'Courier Impo',571: 'Courier Impo',572: 'Courier Impo',544: 'Courier Impo',528: 'Courier Impo',594: 'Courier Impo',599: 'Courier Impo',516: 'Courier Impo',409: 'Carga',581: 'Carga',582: 'Carga',
                           111: 'Courier Expo',112: 'Courier Expo',113: 'Courier Expo',114: 'Courier Expo',116: 'Courier Expo',130: 'Courier Expo',131: 'Courier Expo',132: 'Courier Expo',141: 'Carga',
                           150: 'Carga',152: 'Carga',200: 'Carga',202: 'Carga',220: 'Exporta Simple',222: 'Exporta Simple',223: 'Otro'}
        
        dic_motivos_tipo3={506: 'Carga Aerea',510: 'Carga Aerea',557: 'Carga Aerea',507: 'Carga Aerea',556: 'Carga Aerea',589: 'Carga Aerea',508: 'Carga Aerea',509: 'Carga Aerea',505: 'Carga Aerea',
                          553: 'Carga Aerea',600: 'Courier',550: 'Courier',598: 'Courier',571: 'Courier',572: 'Courier',544: 'Courier',528: 'Courier',594: 'Courier',599: 'Courier',516: 'Courier',409: 'Acarreos',581: 'Maritimo',582: 'Maritimo',111: 'Courier',
                          112: 'Courier',113: 'Courier',114: 'Courier',116: 'Courier',130: 'Courier',131: 'Courier',132: 'Courier',141: 'Carga Aerea',150: 'Carga Aerea',152: 'Carga Aerea',200: 'Carga Courier',
                          202: 'Carga Courier',220: 'Exporta Simple',222: 'Exporta Simple',223: '-'}
        
        
        # 1. Primero, convierte la columna 'Guias_Fecha' a tipo de dato datetime
        df_guias['Guias_Fecha'] = pd.to_datetime(df_guias['Guias_Fecha'])
        
        start_date = pd.to_datetime(date(2023, 1, 1))

        df_guias = df_guias.loc[(df_guias['Guias_Fecha'] >= start_date)]

        df_guias.loc[df_guias['Guias_Fecha'].dt.strftime('%Y-%m') == '2023-12', 'Guias_Fecha'] = '2022-12'
        
        df_guias.rename(columns={'unique_id': 'Nombre Motivo', 
                                'Clientes_Nombre':'Cliente'},
                        inplace=True)

        # Crea una nueva columna 'mes_ano' que contenga el mes y el año de 'Guias_Fecha'
        df_guias['mes_año'] = df_guias['Guias_Fecha'].dt.strftime('%Y-%m')

        #Define las columnas que quieres incluir en el nuevo DataFrame
        columnas_deseadas = ['mes_año', 'Clientes_Codigo', 'Cliente', 'Codigo Motivo','Nombre Motivo', 
                        #'kilos_facturables',
                        'Guias_Peso','Guias_PesoVol' ,'Guias_FOB', 'Guias_Numero','Guias_VentaI', 'Guias_ExpoTotVta']

        # Crea el DataFrame nuevo agrupando y sumarizando los datos
        df_mes_historico = df_guias[columnas_deseadas].groupby(['mes_año', 'Clientes_Codigo', 'Cliente', 'Codigo Motivo', 'Nombre Motivo']).agg({
                                                                                                                                            #'kilos_facturables': 'sum',
                                                                                                                                            'Guias_Peso': 'sum',
                                                                                                                                            'Guias_PesoVol': 'sum', 
                                                                                                                                            'Guias_FOB': 'sum',
                                                                                                                                            'Guias_Numero': 'count', 
                                                                                                                                            'Guias_VentaI': 'sum',
                                                                                                                                            'Guias_ExpoTotVta': 'sum',
                                                                                                                                        }).reset_index()
        df_mes_historico['venta']= np.maximum(df_mes_historico['Guias_VentaI'], df_mes_historico['Guias_ExpoTotVta'])

        df_mes_historico['Codigo Motivo'] = df_mes_historico['Codigo Motivo'].astype(int)
        df_mes_historico['Tipo']= df_mes_historico['Codigo Motivo'].map(dic_motivos_tipo)
        df_mes_historico['Tipo2']= df_mes_historico['Codigo Motivo'].map(dic_motivos_tipo2)
        df_mes_historico['Tipo3']= df_mes_historico['Codigo Motivo'].map(dic_motivos_tipo3)
        
        df_mes_historico['kilos facturables']= np.maximum(df_mes_historico['Guias_Peso'], df_mes_historico['Guias_PesoVol'])
        
        df_mes_historico['Categoria'] = 'select'  # Establecer un valor predeterminado para todos los casos

        # Aplicar las condiciones
        df_mes_historico.loc[df_mes_historico['kilos facturables'] >= 1000, 'Categoria'] = 'Select'
        df_mes_historico.loc[(df_mes_historico['kilos facturables'] >= 500) & (df_mes_historico['kilos facturables'] < 1000), 'Categoria'] = 'Premium'
        df_mes_historico.loc[(df_mes_historico['kilos facturables'] >= 300) & (df_mes_historico['kilos facturables'] < 500), 'Categoria'] = 'Standard'
        df_mes_historico.loc[(df_mes_historico['kilos facturables'] >= 100) & (df_mes_historico['kilos facturables'] < 300), 'Categoria'] = 'Casual'
        df_mes_historico.loc[(df_mes_historico['kilos facturables'] >= 0) & (df_mes_historico['kilos facturables'] <100), 'Categoria'] = 'Casual'
        
        print('Analytics Data cleaning done')
        
        return df_mes_historico
        
        
    def load_analytics(df):
            
        '''Sube la data limpia para analytics a un bucket de s3'''

        # Crea un cliente de S3
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key, region_name=region_name)

        # Nombre de tu bucket en S3
        bucket_name = 'proyectotati'

        # Convierte el DataFrame en un archivo CSV (u otro formato si prefieres)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        # Nombre que tendrá el archivo en S3
        s3_path = 'analytics/data_mes_historico.csv'

        # Carga el archivo en S3
        s3.upload_fileobj(io.BytesIO(
            csv_buffer.getvalue().encode()), bucket_name, s3_path)

        print('Analytics Data loaded done')
        

df_guias = ETL.extract()

df = ETL.transform(df_guias)

ETL.load(df)

### limpieza y subir datos para analytics

df_guias = ETL.extract()

df_analytics= ETL.clean_analytics(df_guias)

ETL.load_analytics(df_analytics)   