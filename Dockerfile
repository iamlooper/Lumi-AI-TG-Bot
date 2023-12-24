FROM python:3.12.0

WORKDIR /app/

COPY requirements.txt .

EXPOSE 8080
 
CMD bash -c "$(curl -fsSL https://raw.githubusercontent.com/iamlooper/VIC-TG-Bot/main/run.sh)"