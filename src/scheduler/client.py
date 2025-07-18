import logging
import inngest

# Create an Inngest client
inngest_client = inngest.Inngest(
    app_id="social_share",
    logger=logging.getLogger("gunicorn"),
)