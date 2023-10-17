## etl + inference

from inference import Inference

df= Inference.read_data_s3()

predictor = Inference.load_modelo()

forecast = Inference.predict(df, predictor)

Inference.save_forecast_s3(forecast)

print(forecast.head())
