FROM golang:1.24-bookworm AS native
WORKDIR /native
COPY engines/weather .
RUN CGO_ENABLED=0 go build -o weather-engine .

FROM node:24-slim AS web
WORKDIR /web
COPY web/package*.json ./
RUN npm ci
COPY web .
RUN npm run build

FROM python:3.12-slim
WORKDIR /service
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home service && chown service /service
COPY --chown=service:service app ./app
COPY --from=web --chown=service:service /app/frontend ./app/frontend
COPY --from=native /native/weather-engine /usr/local/bin/weather-engine
ENV NATIVE_ENGINE='["/usr/local/bin/weather-engine"]'
USER service
EXPOSE 8201
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8201"]
