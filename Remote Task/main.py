from etl import ETL

df_guias, df_motivos = ETL.extract()
df = ETL.transform(df_guias, df_motivos)

ETL.load(df)