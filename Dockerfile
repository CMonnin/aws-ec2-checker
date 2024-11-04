FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Print Python version and installed packages for debugging
RUN python --version && pip list

# Start the bot
CMD ["python", "run.py"]

