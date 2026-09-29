FROM python:3.12-slim
WORKDIR /work
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY backend /work/backend
COPY data_pipeline /work/data_pipeline
COPY data/processed /work/data/processed
COPY pyproject.toml /work/pyproject.toml
COPY scripts /work/scripts
ENV PYTHONPATH=/work/backend:/work
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
