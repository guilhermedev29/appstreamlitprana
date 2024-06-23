
FROM python:3.8

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8501

# Comando para executar o Streamlit
CMD ["streamlit", "run","app.py"]
