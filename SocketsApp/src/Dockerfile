FROM python@sha256:5e2dbd4bbdd9c0e67412aea9463906f74a22c60f89eb7b5bbb7d45b66a2b68a6 as BUILDER

WORKDIR /app

RUN apt update && \
  apt install -y tcpdump
RUN echo "HI" >> hello.txt

FROM python@sha256:5e2dbd4bbdd9c0e67412aea9463906f74a22c60f89eb7b5bbb7d45b66a2b68a6

WORKDIR /app
COPY --from=BUILDER / /
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./ ./

CMD [ "python", "-u", "./main.py" ]

