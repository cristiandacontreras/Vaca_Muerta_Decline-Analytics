FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
# Ejecuta la limpieza primero y luego arranca el dashboard
CMD ["sh", "-c", "python src/data_cleaning.py && python dashboard/app.py"]