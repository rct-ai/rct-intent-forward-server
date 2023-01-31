FROM python:3.8.10
USER root

WORKDIR /workspace
COPY . /workspace
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8077

CMD ['flask', 'run', '--host=0.0.0.0 -p 8077']