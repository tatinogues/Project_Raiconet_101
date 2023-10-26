import boto3
import pandas as pd
import io
from functions.credentials import aws_access_key_id, aws_secret_access_key, region_name


def get_data_s3():

    '''Descarga un archivo desde un bucket de S3 y carga los datos en un DataFrame'''

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key,
                      region_name=region_name)

    bucket_name = 'proyectotati'
    s3_path = 'pre_trained_data/data.csv'

    try:
        response = s3.get_object(Bucket=bucket_name, Key=s3_path)

        # Lee el contenido del archivo en un DataFrame
        df = pd.read_csv(io.BytesIO(response['Body'].read()))
        df['ds'] = pd.to_datetime(df['ds'])

        lista_df = ['impo_1', 'impo_2', 'impo_3', 'impo_4', 'impo_5', 'impo_6', 'impo_7',
                    'expo_1', 'expo_2', 'expo_3', 'expo_4', 'expo_5']

        nombres_motivos = ['USA FLAT', 'ORIENTE UPS', 'CHINA LATIN LOGISTIC  CO via UPS/FEDEX', 'EUROPA UPS',
                           'Courier Oriente FLAT Wish/Latin logistic', 'Impo Geobox Flat ', 'UPS MERCOSUR',
                           'Exporta Simple - Puerta-Aeropuerto', 'CARGA AEREA EXPO PREPAID', 'CARGA AEREA EXPO - Q',
                           '4-Expo - Fedex Economy', '6-Expo-UPS Express']

        dic_num_motivos = {lista_df[i]: nombres_motivos[i]
                           for i in range(len(lista_df))}

        df['unique_id'] = df['unique_id'].map(dic_num_motivos)

        df.rename(columns={"unique_id": "family"}, inplace=True)

        ##agrego el seleccionar todos
        fecha_agregada = df.groupby(['ds'])['y'].sum().reset_index()
        fecha_agregada['family'] = 'Seleccionar todos'
        dff = pd.concat([df, fecha_agregada], ignore_index=True)

        print("Data leida con exito")

        return dff

    except Exception as e:
        print(f'Error al cargar el archivo desde S3: {str(e)}')
        return None

def get_forecast_s3():
    '''Lee el forecast guardado en el bucket para mostrar las predicciones en la grafica'''

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key,
                      region_name=region_name)

    bucket_name = 'proyectotati'
    s3_path = 'forecast/all_preds.csv'

    try:

        response = s3.get_object(Bucket=bucket_name, Key=s3_path)

        # Lee el contenido del archivo en un DataFrame
        df = pd.read_csv(io.BytesIO(response['Body'].read()))
        df['ds'] = pd.to_datetime(df['ds'])

        lista_df = ['impo_1', 'impo_2', 'impo_3', 'impo_4', 'impo_5', 'impo_6', 'impo_7',
                    'expo_1', 'expo_2', 'expo_3', 'expo_4', 'expo_5']

        nombres_motivos = ['USA FLAT', 'ORIENTE FEDEX', 'CHINA LATIN LOGISTIC  CO via UPS/FEDEX', 'EUROPA UPS',
                           'Courier Oriente FLAT Wish/Latin logistic', 'Impo Geobox Flat ', 'UPS MERCOSUR',
                           'Exporta Simple - Puerta-Aeropuerto', 'CARGA AEREA EXPO PREPAID', 'CARGA AEREA EXPO - Q',
                           '4-Expo - Fedex Economy', '6-Expo-UPS Express']

        dic_num_motivos = {lista_df[i]: nombres_motivos[i]
                           for i in range(len(lista_df))}

        df['unique_id'] = df['unique_id'].map(dic_num_motivos)

        df.rename(columns={"unique_id": "family"}, inplace=True)

        ##agrego el seleccionar todos

        fecha_agregada = df.groupby(['ds'])[['pred', 'p25', 'p75', 'p10', 'p90']].sum().reset_index()
        fecha_agregada['family'] = 'Seleccionar todos'
        dff = pd.concat([df, fecha_agregada], ignore_index=True)

        print("Forecast leido con exito")

        return dff

    except Exception as e:
        print(f'Error al cargar el archivo desde S3: {str(e)}')
        return None


def get_analytics_s3():
    '''Lee la data de analytics guardado en el bucket'''

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key,
                      region_name=region_name)

    bucket_name = 'proyectotati'
    s3_path = 'analytics/data_mes_historico.csv'

    try:

        response = s3.get_object(Bucket=bucket_name, Key=s3_path)

        # Lee el contenido del archivo en un DataFrame
        df = pd.read_csv(io.BytesIO(response['Body'].read()))


        print("Data Analytics leido con exito")

        return df

    except Exception as e:
        print(f'Error al cargar el archivo desde S3: {str(e)}')
        return None


