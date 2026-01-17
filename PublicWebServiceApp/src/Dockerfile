FROM python@sha256:5e2dbd4bbdd9c0e67412aea9463906f74a22c60f89eb7b5bbb7d45b66a2b68a6 as BUILDER

WORKDIR /app

COPY .env ./.env
RUN apt update
RUN apt install -y git
RUN . ./.env && git clone https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${GITHUB_REPO}.git

FROM python@sha256:5e2dbd4bbdd9c0e67412aea9463906f74a22c60f89eb7b5bbb7d45b66a2b68a6

WORKDIR /app
COPY --from=BUILDER / /
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN git config --global user.email "DNAC-Git-Script@fakemail.com" && \
  git config --global user.name "DNAC-Git-Script"
COPY ./ ./

CMD [ "python", "-u", "./main.py" ]

