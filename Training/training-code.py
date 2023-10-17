## etl + train + inference

from etl import ETL
from train import Train
from inference import Inference

df_guias, df_motivos = ETL.extract()
df = ETL.transform(df_guias, df_motivos)

ETL.load(df)

predictor = Train.train(df)

Train.save_model(predictor)

forecast = Inference.predict(df, predictor)

Inference.save_forecast_s3(forecast)

print(forecast.head())
