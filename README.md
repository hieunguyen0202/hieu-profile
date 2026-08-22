# Hieu Nguyen — Portfolio


Built with **Node.js + Express**. Content is taken from `resume-coming-soon.png` (CV placeholder). Credly badges are linked and served locally.

## Run with Docker Compose

```bash
cd CKA/hieu-portfolio
docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000).

Stop:

```bash
docker compose down
```

## Run locally (without Docker)

```bash
cd CKA/hieu-portfolio
npm install
npm start
```

Dev reload:

```bash
npm run dev
```


## Endpoints

| Path | Description |
| --- | --- |
| `/` | Portfolio |
| `/cv/resume-coming-soon.png` | Resume placeholder (coming soon) |
| `/api/health` | Health check |
| `/api/profile` | Profile JSON |
| `POST /api/contact` | Contact form (logged to container stdout) |
