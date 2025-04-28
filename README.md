# BullStreetBets

**A command-line and Flask-based pipeline that:**
1. Expands user keywords via a local LLM
2. Scrapes Reddit posts/comments over the past two years
3. Counts keyword traffic and normalizes per day
4. Detects spikes in monthly keyword volume
5. Selects relevant ETFs based on those keywords
6. Renders a live-streamed log and a Markdown report with statistics and plots

---
**To run: Use Docker**
1. Build and run container
```bash
docker build -t bullstreetbets .
docker run -d \
  -p 3000:5000 \
  -v "$(pwd)/tmp":/app/tmp \
  -v "$(pwd)/static":/app/static \
  -e REDDIT_CLIENT_ID=xxx \
  -e REDDIT_CLIENT_SECRET=yyy \
  -e REDDIT_USER_AGENT=myapp \
  --name bullstreetbets \
  bullstreetbets
```
2. View logs
```bash
docker logs -f bullstreetbets
```
3. Navigate to http://localhost:3000/
---