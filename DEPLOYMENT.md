# Deployment notes

- Set a unique, secret `SECRET_KEY` in your hosting provider's environment variables.
- Configure persistent storage for `real_trader.db`; ephemeral filesystems can erase data on restart.
- Use a production WSGI server such as Gunicorn (`pip install gunicorn`).
- Enable HTTPS and review authentication, backups, privacy, and hosting security before real users use the app.
- Do not store broker passwords, API keys, or payment details in this starter project.
