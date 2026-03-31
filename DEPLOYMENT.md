# Deploying TakeOff Demo to Render

## Architecture

Single Docker container serving both the FastAPI backend and the built React frontend on port 10000. The frontend is compiled at build time and served as static files by FastAPI, so all `/api/*` routes hit the backend and everything else returns the SPA.

## Deploy via Render Blueprint

1. Push this repo to GitHub (`github.com/aininja-pro/TO_Demo`)
2. Go to [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint**
3. Connect the `aininja-pro/TO_Demo` repo
4. Render reads `render.yaml` and creates the `takeoff-demo` service
5. Set the `ANTHROPIC_API_KEY` environment variable in the Render dashboard
6. Deploy

## Deploy Manually

1. **Render Dashboard** → **New** → **Web Service**
2. Connect the GitHub repo
3. Settings:
   - **Environment**: Docker
   - **Dockerfile Path**: `./Dockerfile`
   - **Plan**: Starter (or Free for testing)
4. Add environment variable: `ANTHROPIC_API_KEY` = your Anthropic API key
5. Deploy

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Claude API key for AI vision fallback in symbol counting |
| `CORS_ORIGINS` | No | Comma-separated allowed origins (defaults to localhost) |
| `PYTHONUNBUFFERED` | No | Set to `1` for real-time log output (set in render.yaml) |

## SSE Streaming

Render supports Server-Sent Events natively. The pipeline streams progress events through `/api/takeoff/{job_id}/stream`. No special proxy config is needed.

## Local Docker Testing

```bash
docker build -t takeoff-demo .
docker run -p 10000:10000 -e ANTHROPIC_API_KEY=sk-... takeoff-demo
# Open http://localhost:10000
```
