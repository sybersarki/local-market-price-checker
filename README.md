# Local Market Price Checker

A simple REST API that lets people report and look up prices of everyday
items (food, commodities, etc.) across different local markets.

## Problem it solves

Buyers and traders often have no easy way to check what an item "should"
cost across nearby markets, which makes it easier to get overcharged or to
under-price goods unknowingly. This app lets anyone submit a price report
(item, market, location, price) and lets anyone else search reported
prices before they go shopping or selling.

## Tech stack

- **Python 3.12 / Flask** — REST API
- **SQLite** — lightweight embedded database (no external DB service needed)
- **Gunicorn** — production WSGI server
- **Docker** — containerization
- Deployed on **[Render / Railway — fill in once deployed]**

## Live demo

🔗 `https://<your-deployed-url>.onrender.com` — *(update after deployment)*

## API Endpoints

| Method | Endpoint            | Description                                   |
|--------|----------------------|------------------------------------------------|
| GET    | `/`                  | Health check                                   |
| POST   | `/prices`            | Add a new price report                         |
| GET    | `/prices`            | List/search price reports                      |
| GET    | `/prices/<id>`       | Get a single price report                      |
| DELETE | `/prices/<id>`       | Delete a price report                          |

### Search / filter

`GET /prices` supports optional query params:
- `?item=rice`
- `?market=ariaria`
- `?location=aba`

These can be combined, e.g. `GET /prices?item=rice&location=aba`.

### Example: add a price report

```bash
curl -X POST http://localhost:5000/prices \
  -H "Content-Type: application/json" \
  -d '{
        "item": "Rice (50kg bag)",
        "market": "Ariaria Market",
        "location": "Aba, Abia",
        "price": 75000,
        "unit": "bag"
      }'
```

Response:

```json
{
  "id": 1,
  "item": "Rice (50kg bag)",
  "market": "Ariaria Market",
  "location": "Aba, Abia",
  "price": 75000.0,
  "unit": "bag",
  "reported_at": "2026-08-08T12:39:46.500635+00:00"
}
```

### Example: search for a price

```bash
curl "http://localhost:5000/prices?item=rice"
```

## Running locally (without Docker)

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 app.py
```

The API will be available at `http://localhost:5000`.

## Running with Docker

Build the image:

```bash
docker build -t market-price-checker .
```

Run the container:

```bash
docker run -p 5000:5000 market-price-checker
```

The API will be available at `http://localhost:5000`.

## Running the image from Docker Hub

*(after you've pushed it — see below)*

```bash
docker pull <your-dockerhub-username>/market-price-checker
docker run -p 5000:5000 <your-dockerhub-username>/market-price-checker
```

## Pushing to Docker Hub

```bash
docker login
docker tag market-price-checker <your-dockerhub-username>/market-price-checker
docker push <your-dockerhub-username>/market-price-checker
```

## Deployment

This project can be deployed to any platform that supports Docker
deployments, such as **Render** or **Railway**:

1. Push this project to a GitHub repository.
2. On Render/Railway, create a new **Web Service** and connect your repo.
3. Choose "Deploy from Dockerfile" (both platforms auto-detect it).
4. Set the port to `5000` (or let the platform use the `PORT` env variable —
   this app already respects `$PORT` if set).
5. Deploy, then copy the live URL into the "Live demo" section above.

## Project structure

```
market-price-checker/
├── app.py              # Flask application (all routes + DB logic)
├── requirements.txt    # Python dependencies
├── Dockerfile           # Container build instructions
├── .dockerignore
└── README.md
```

## Author

Paul Umeh — Cloud Computing Track (CC-08), 3MTT Abia / Abia Tech Hub
