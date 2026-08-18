# Hieu Nguyen — Portfolio

Terminal-style DevOps portfolio (layout inspired by [hangnt1001.github.io](https://hangnt1001.github.io/#experience), cyan/blue palette from [ducdinh.com](https://ducdinh.com/#contact)).

Built with **Node.js + Express**. Content is taken from `NguyenXuanHieu-CV-DevOpsEngineer.pdf`. Credly badges are linked and served locally.

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
| `/cv/NguyenXuanHieu-CV-DevOpsEngineer.pdf` | Resume download |
| `/api/health` | Health check |
| `/api/profile` | Profile JSON |
| `POST /api/contact` | Contact form (logged to container stdout) |
