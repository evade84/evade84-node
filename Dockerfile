FROM python:3.10

WORKDIR /usr/src/fsoac-node
COPY node ./node/
COPY pyproject.toml pdm.lock* ./

RUN pip install pdm==1.15.1
RUN pdm install --prod --no-isolation

ENTRYPOINT ["pdm", "run", "uvicorn", "node.main:app", "--host", "0.0.0.0", "--port", "80"]