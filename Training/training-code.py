## etl + train + inference

from train import Train
from inference import Inference

df = Train.read_data_s3()

predictor = Train.train(df)

Train.save_model(predictor)

forecast = Inference.predict(df, predictor)

Inference.save_forecast_s3(forecast)

print(forecast.head())
