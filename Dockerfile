FROM python:3.12


WORKDIR /NapTwitter

COPY poetry.lock pyproject.toml /NapTwitter/
RUN pip install --upgrade --no-cache-dir pip==23.1.2 && \
    pip install -U --no-cache-dir poetry==1.5.1 && \
    poetry config --local virtualenvs.create false && \
    poetry install

COPY . .

ENTRYPOINT ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]