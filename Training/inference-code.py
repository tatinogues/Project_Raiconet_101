## etl + inference

from etl import ETL
from inference import Inference

df_guias, df_motivos = ETL.extract()
df = ETL.transform(df_guias, df_motivos)

ETL.load(df)

predictor = Inference.load_modelo()
forecast = Inference.predict(df, predictor)

Inference.save_forecast_s3(forecast)

print(forecast.head())
