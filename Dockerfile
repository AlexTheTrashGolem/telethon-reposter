FROM python:3.11-slim

# Create working directory
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY reposter.py .

# Run the bot
CMD ["python", "reposter.py"]