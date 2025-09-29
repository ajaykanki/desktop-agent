from worker.main import app
import logging

logging.basicConfig(level=logging.INFO)
app.run_worker(queues=["sum"], name="worker-name")
