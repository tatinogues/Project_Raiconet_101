import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller


##importamos los datos

df_impo_1= pd.read_csv('Data/Modelado/impo 1 - USA FLAT.csv')
df_impo_2= pd.read_csv('Data/Modelado/impo 2 - ORIENTE UPS.csv')
df_impo_3= pd.read_csv('Data/Modelado/impo 3 - CHINA LATIN LOGISTIC.csv')
df_impo_4= pd.read_csv('Data/Modelado/impo 4 - EUROPA UPS.csv')
df_impo_5= pd.read_csv('Data/Modelado/impo 5 - Courier Oriente FLAT Wish.csv')
df_impo_6= pd.read_csv('Data/Modelado/impo 6 - Impo Geobox Flat.csv')
df_impo_7= pd.read_csv('Data/Modelado/impo 7 - UPS MERCOSUR.csv')

df_expo_1= pd.read_csv('Data/Modelado/expo 1 - Exporta Simple - Puerta-Aeropuerto.csv')
df_expo_2= pd.read_csv('Data/Modelado/expo 2 - CARGA AEREA EXPO PREPAID.csv')
df_expo_3= pd.read_csv('Data/Modelado/expo 3 - CARGA AEREA EXPO - Q.csv')
df_expo_4= pd.read_csv('Data/Modelado/expo 4 - 4-Expo - Fedex Economy.csv')
df_expo_5= pd.read_csv('Data/Modelado/expo 5 - 6-Expo-UPS Express.csv')


class DataPrep:
 
    def __init__(self):
        
        lista_df= ['df_impo_1', 'df_impo_2', 'df_impo_3', 'df_impo_4', 'df_impo_5','df_impo_6', 'df_impo_7',
                   'df_expo_1', 'df_expo_2', 'df_expo_3', 'df_expo_4', 'df_expo_5']

        lista_dataframe= [df_impo_1, df_impo_2, df_impo_3, df_impo_4, df_impo_5,df_impo_6, df_impo_7,
                          df_expo_1, df_expo_2, df_expo_3, df_expo_4, df_expo_5]
        
        self.lista_dataframe= lista_dataframe
        self.lista_df= lista_df 
        
    def crear_dataset(self, df, motivo): 
        df= df[['Guias_Fecha', 'Motivo', 'Guias_Peso']]
        df['Guias_Fecha']= pd.to_datetime(df['Guias_Fecha'])
        df= df[df['Motivo']==motivo]
        df.rename(columns = {'Guias_Peso': 'y'}, inplace = True)
        df.drop(columns='Motivo', inplace=True)
        df.reset_index(inplace=True)
        df.drop(columns= 'index', inplace= True)
        #agrupamos por semana => porque las entradas estan separadas, asi q nos quedamos con el total de kilos por fecha
        df= df.groupby(pd.Grouper(key='Guias_Fecha', axis=0, freq='W')).sum()
        df['ds']= df.index
        df = df.reset_index(drop=True)
        df= df[['ds', 'y']]
        return df
    
    def unificar_df(self):
    
        lista_df_clean= []
        n=0
        
        for df in self.lista_dataframe: 
            
            df[['unique_id']]= self.lista_df[n][3:]
            dff = df[['unique_id','ds', 'y']]
            lista_df_clean.append(dff)
            n+=1
        df_unificado= pd.concat(lista_df_clean)
        df_unificado=df_unificado[['ds', 'unique_id', 'y']]
    
        return df_unificado
    
class tests_pre_modelling: 
    @staticmethod
    #test de Dicky Fuller para test de estacionalidad (ADF)
    def check_stationarity(series):
        # Copiado de https://machinelearningmastery.com/time-series-data-stationary-python/

        result = adfuller(series.values)

        print('ADF Statistic: %f' % result[0])
        print('p-value: %f' % result[1])
        print('Critical Values:')
        for key, value in result[4].items():
            print('\t%s: %.3f' % (key, value))

        if (result[1] <= 0.05) & (result[4]['5%'] > result[0]):
            print("\u001b[32mStationary\u001b[0m")
        else:
            print("\x1b[31mNon-stationary\x1b[0m")
            
    #funcion de diferenciacion para convertir las series no estacionarias en estacionarias para correr test ACF y PACF        
    def crear_diff(df): 
        
        df['y_diff']= df['y'].diff().fillna(0)
        print(tests_pre_modelling.check_stationarity(df['y_diff']))
        
        return df

class modelos:
    
    def sarimax_model(df, order,seasonal_order,  motivo, comparison_tbl):
    
        #queremos saber cuanto tiempo de procesamiento lleva correr cada modelo para eso usamos el time.clock 
        tic = time.clock()
        
        num_samples= len(df)
        train_len = int(0.8* num_samples)
        
        train = df['y'][:train_len]
        ma_model =  sm.tsa.statespace.SARIMAX(train,
                                            order=order, 
                                            seasonal_order=seasonal_order).fit()

        print(ma_model.summary())
        pred = ma_model.predict(start=train_len, end=num_samples, dynamic=False)
        
        
        actual_values = df['y'][train_len -1:]
        predicted_values = pred
        
        #definimos las metricas con las que vamos a evaluar la performance 
        
        mae = mean_absolute_error(actual_values, predicted_values)
        rmse = np.sqrt(mean_squared_error(actual_values, predicted_values))
        smape = calculate_smape(actual_values, predicted_values)
        toc =  time.clock() #frenamos el cronometro y a continuacion creamos la variable que guarda el tiempo transcurrido desde que empezo a correr el modelo hasta q termino
        exetime = '{0:.4f}'.format(toc-tic)
        
        
        # creamos un diccionario donde guardar las variables y resultados del modelo que corrimos
        raw_data = {
                'Serie': motivo,
                'Modelo': f'SARIMAX {order}',
                'MAE':  mae ,
                'RMSE': rmse,
                'sMAPE': smape, 
                'Processing Time': exetime
                }
        
        #creamos un df de una sola row correspondiente a los datos del modelo corrido         
        df_tbl = pd.DataFrame(raw_data,
            columns =['Serie','Modelo','MAE','RMSE', 'sMAPE', 'Processing Time'],
            index = [i_index + 1])
        #le hacemos un append al df que ya definimos afuera de la funcion y que sera ingresado como input, de esta forma cada vez q corremos un modelo los datos se guardan en una nueva linea sin afectar los datos anteriores.
        
        comparison_tbl = pd.concat([comparison_tbl, df_tbl], ignore_index=True)
        
        #graficamos los resultados obtenidos 
        f, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 4))
        sns.lineplot(x=df.ds[train_len:num_samples], y=df.y[train_len:num_samples], marker='o', label='test', color='grey')
        sns.lineplot(x=df.ds[:train_len], y=train, marker='o', label='train')
        sns.lineplot(x=df.ds[train_len:num_samples], y=pred, marker='o', label='pred')
        ax.set_xlim([df.ds.iloc[0], df.ds.iloc[-1]])
        ax.set_title(f'{motivo}: SARIMAX {order} Model')
        plt.tight_layout()
        plt.show()
        
        return comparison_tbl
        
    


    
## Metrics    
class Metrics: 
    def __init__(self, actual_values, forecasted_values):
        
        self.actual_values= actual_values
        self.forecasted_values= forecasted_values


    def calculate_smape(self):
        absolute_percentage_errors = []
    
        for actual, forecasted in zip(self.actual_values, self.forecasted_values):
            numerator = abs(actual - forecasted)
            denominator = (abs(actual) + abs(forecasted)) + 1e-9  # Agregar una constante para evitar división por cero
            ape = numerator / (denominator / 2)
            absolute_percentage_errors.append(ape)
    
        smape = sum(absolute_percentage_errors) / len(absolute_percentage_errors)
        return smape

    def wmape(self):
        return np.abs(self.actual_values - self.forecasted_values).sum() / np.abs(self.actual_values).sum()


##guardar metricas de NN en comparison_tbl
from sklearn.metrics import mean_squared_error, mean_absolute_error    
 
def guardar_metricas(comparison_tbl, all_preds, exetime, model_name):
    
        lista_family= []
        lista_mae=[]
        lista_rmse=[]
        lista_smape=[]
        lista_exetime=[]
            
        def calculate_smape(actual_values, forecasted_values):
            absolute_percentage_errors = []
            
            for actual, forecasted in zip(actual_values, forecasted_values):
                numerator = abs(actual - forecasted)
                denominator = (abs(actual) + abs(forecasted)) + 1e-9  # Agregar una constante para evitar división por cero
                ape = numerator / (denominator / 2)
                absolute_percentage_errors.append(ape)
            
            smape = sum(absolute_percentage_errors) / len(absolute_percentage_errors)
            return smape
            
        for fam in list(all_preds.unique_id.unique()): 
            df_pred= all_preds[all_preds['unique_id']== fam]
            actual_values= df_pred['y']
            predicted_values= df_pred['pred']
                
            mae = mean_absolute_error(actual_values, predicted_values)
            rmse = np.sqrt(mean_squared_error(actual_values, predicted_values))
            smape = calculate_smape(actual_values, predicted_values)
                
            lista_family.append(fam)
            lista_mae.append(mae)
            lista_rmse.append(rmse)
            lista_smape.append(smape)
            lista_exetime.append(exetime)
            
        raw_data = {'Serie': lista_family,
                    'Modelo': model_name,
                    'MAE':  lista_mae,
                    'RMSE': lista_rmse,
                    'sMAPE': lista_smape, 
                    'Processing Time': lista_exetime}
            
        df_tbl = pd.DataFrame(raw_data)
            
        comparison_tbl = pd.concat([comparison_tbl, df_tbl], ignore_index=True)
            
        return comparison_tbl