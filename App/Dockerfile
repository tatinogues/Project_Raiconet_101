#codigo copiado de https://towardsdatascience.com/dockerize-your-dash-app-1e155dd1cea3
#https://us-east-1.console.aws.amazon.com/ecr/repositories/private/427951462215/raico_analytics?region=us-east-1

FROM python:3.9-slim
ENV DASH_DEBUG_MODE False
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . ./
EXPOSE 8050
CMD ["python", "app/app.py"]