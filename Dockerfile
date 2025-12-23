FROM python:3.9

# Create a non-root user for security (HF requirement)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

WORKDIR /app

# Copy requirements first for faster building
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the app (including the /utils folder)
COPY --chown=user . .

# Expose the HF default port
EXPOSE 7860

CMD ["python", "app.py"]