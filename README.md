# Life Progress

Life Progress is a private, self-hosted dashboard that makes the passage of time visible.

Instead of being another task manager or calendar, Life Progress turns your dates into meaningful perspectives: weeks lived, year progress, important milestones, time until people you care about reach significant ages, remaining weekends, and more.

## Features

- Personal profile with date of birth and configurable lifespan marker
- Age, days, months, and weeks lived
- Life progress percentage
- Current-year progress
- Life-in-weeks visualization
- Important people and age milestones
- Custom future milestones
- Remaining days, weeks, Saturdays, and Christmases
- Responsive mobile and desktop interface
- Automatic dark/light appearance
- Local SQLite storage
- Health endpoint
- Docker-first deployment
- No telemetry
- No cloud dependency

## Docker Compose

Clone the repository:

    git clone https://github.com/mx5matt/life-progress.git
    cd life-progress

Create the persistent data directory:

    mkdir -p data
    sudo chown 10001:10001 data

By default, Life Progress binds to `127.0.0.1` on port `8383`.

To bind it to another interface, set `LIFE_PROGRESS_BIND` in the deployment environment. For example, use the appropriate address for your own host. Do not commit private deployment addresses to the repository.

Start Life Progress:

    docker compose up -d --build

Default deployment:

    http://127.0.0.1:8383

## Updating

    git pull
    docker compose up -d --build

## Data

Persistent data is stored in:

    ./data/life-progress.db

Back up that file to preserve the Life Progress database.

## Health check

    GET /health

A healthy instance returns JSON containing `status: ok`.

## Security

Version 0.1.0 is intended for a trusted private network. Authentication is not yet included.

Do not expose the application directly to the public internet until authentication and appropriate HTTPS/reverse-proxy controls are configured.

## License

Life Progress is released under the MIT License. See `LICENSE`.

## Changelog

See `CHANGELOG.md`.
