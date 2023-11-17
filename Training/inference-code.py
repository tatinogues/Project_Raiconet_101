## etl + inference

from inference import Inference
 
# Descargar data desde el bucket
df= Inference.read_data_s3()
    
# Obtener el modelo del bucket de s3
predictor = Inference.load_modelo()

# Realizar predicciones
forecast = Inference.predict(df, predictor)

# Guardar predicciones en el bucket de resultados
Inference.save_forecast_s3(forecast)

