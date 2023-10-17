##  toma el modelo guardado en pickle y hace predicciones con la data completa guardado en pre_trained

import pandas as pd
import boto3
import io
import datetime
from datetime import date, timedelta
from credentials import aws_access_key_id, aws_secret_access_key, region_name
import numpy as np
import pickle

from gluonts.dataset.pandas import PandasDataset
from gluonts.dataset.common import ListDataset
from gluonts.torch.model.deepar import DeepAREstimator
from gluonts.torch.distributions import NegativeBinomialOutput
from gluonts.evaluation import make_evaluation_predictions

class Inference:
    
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
            
    @staticmethod
    def load_modelo():
        '''Lee el modelo guardado como pkl desde el bucket de S3'''

        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name=region_name)

        bucket_name = 'proyectotati'
        s3_path = 'model/predictor.pkl'
        
        try:

            response = s3.get_object(Bucket=bucket_name, Key=s3_path)

            response = s3.get_object(Bucket=bucket_name, Key=s3_path)
            modelo_bytes = response['Body'].read()

            # Carga el modelo desde los bytes descargados
            modelo = pickle.load(io.BytesIO(modelo_bytes)) 
            
            print("Modelo obtenido con exito :)")

            return modelo

        except Exception as e:
            print(f'Error al leer modelo desde S3: {str(e)}')
            return None
        
    def predict(data, predictor):
        
        '''Realiza el forecast a partir de la data y el modelo entrenado'''
        
        pred_ds = PandasDataset.from_long_dataframe(data,
                                             target='y',
                                             item_id='unique_id', 
                                             timestamp='ds',
                                             freq='W')
        
        pred = list(predictor.predict(pred_ds))

        all_preds = list()
        for item in pred:
            unique_id = item.item_id
            p = item.samples.mean(axis=0)
            p10 = np.percentile(item.samples, 10, axis=0)
            p90 = np.percentile(item.samples, 90, axis=0)
            p25 = np.percentile(item.samples, 25, axis=0)
            p75 = np.percentile(item.samples, 75, axis=0)
            dates = pd.date_range(start=item.start_date.to_timestamp(), periods=len(p), freq='W')
            family_pred = pd.DataFrame({'ds': dates, 
                                        'unique_id': unique_id,
                                        'pred': p,
                                        'p25': p25,
                                        'p75': p75,
                                        'p10': p10, 
                                        'p90': p90})
            all_preds += [family_pred]
            
        all_preds = pd.concat(all_preds, ignore_index=True)

        return all_preds
    
    def save_forecast_s3(forecast):
        '''Sube las predicciones a un bucket de s3'''

        # Crea un cliente de S3
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key, region_name=region_name)

        # Nombre de tu bucket en S3
        bucket_name = 'proyectotati'

        # Convierte el DataFrame en un archivo CSV (u otro formato si prefieres)
        csv_buffer = io.StringIO()
        forecast.to_csv(csv_buffer, index=False)

        # Nombre que tendrá el archivo en S3
        s3_path = 'forecast/all_preds.csv'

        # Carga el archivo en S3
        s3.upload_fileobj(io.BytesIO(
            csv_buffer.getvalue().encode()), bucket_name, s3_path)

        print('Forecast Uploaded to s3 bucket')
        
        
        
        
            

data= Inference.read_data_s3()
predictor= Inference.load_modelo()
forecast= Inference.predict(data, predictor)

Inference.save_forecast_s3(forecast)

print(forecast.head())

