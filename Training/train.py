# 2. Toma la data salida del etl y guardada en el bucket y entrena el modelo -> modelo = debe ser corrido con un eventbridge una vez al mes
import pandas as pd
import boto3
import io
import datetime
from datetime import date, timedelta
from credentials import aws_access_key_id, aws_secret_access_key, region_name
import numpy as np
import pickle
from gluonts.dataset.pandas import PandasDataset
from gluonts.torch.model.deepar import DeepAREstimator
from gluonts.torch.distributions import NegativeBinomialOutput


class Train:

    @staticmethod
    def read_data_s3():
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

            print("Data leida con exito")

            return df

        except Exception as e:
            print(f'Error al cargar el archivo desde S3: {str(e)}')
            return None

    def train(df):

        train_ds = PandasDataset.from_long_dataframe(df,
                                                     target='y',
                                                     item_id='unique_id',
                                                     timestamp='ds',
                                                     freq='W')

        estimator = DeepAREstimator(freq='W',  # la frecuencia de los datos es semanal por lo que el modelo debe ser semanal tambien
                                    # el modelo va a usar las ultimas 10 semanas para predecir las siguientes 10, window de 10
                                    context_length=10,
                                    prediction_length=10,  # va a predecir las proximas 10 semanas
                                    num_layers=4,  # el modelo posee tres capas con un default de 40 nodos por capa
                                    dropout_rate=0.2,  # seteo de 20% de las units en una layer en cero de forma random
                                    trainer_kwargs={
                                        'max_epochs': 210},  # 210 epochs
                                    distr_output=NegativeBinomialOutput())  # el default es Distribucion t-student, pero al usar negative binomial permite que las predicciones no tomen valores negativos

        predictor = estimator.train(train_ds)

        print("Entrenamiento Glounts DeepAr - Completo")

        return predictor

    def save_model(predictor):

        # Serializa el predictor en un objeto bytes usando Pickle
        model_bytes = pickle.dumps(predictor)

        # Configura las credenciales de AWS y el nombre del bucket
        bucket_name = 'proyectotati'
        s3_path = 'model/predictor.pkl'  # Ruta donde se guardará el modelo en S3

        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          region_name=region_name)

        # Sube el modelo serializado a S3
        s3.put_object(Bucket=bucket_name, Key=s3_path, Body=model_bytes)

        print(f"Modelo guardado en S3 en: s3://{bucket_name}/{s3_path}")
