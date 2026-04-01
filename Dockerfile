# Используем Python
FROM python:3.10-slim

# Устанавливаем системные зависимости и Go
RUN apt-get update && apt-get install -y \
  golang \
  git \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Настраиваем пути для Go
ENV GOPATH=/root/go
ENV PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

# Устанавливаем все инструменты разведки (как в оригинале)
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
  go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest && \
  go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
  go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest && \
  go install -v github.com/tomnomnom/assetfinder@latest && \
  go install -v github.com/tomnomnom/waybackurls@latest && \
  go install -v github.com/lc/subjs@latest

# Копируем файлы бота
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Запуск
CMD ["python", "preceon_bot.py"]
