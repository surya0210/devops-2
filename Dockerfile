FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN pip install flask reportlab pytest

EXPOSE 5000
CMD ["python3", "ACEest_Fitness_API.py"]
