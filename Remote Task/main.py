from etl import ETL

### limpieza y subier datos para el modelo

df_guias = ETL.extract()

df = ETL.transform(df_guias)

ETL.load(df)

### limpieza y subir datos para analytics

df_guias = ETL.extract()

df_analytics= ETL.clean_analytics(df_guias)

ETL.load_analytics(df_analytics)