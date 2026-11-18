# Changelog

All notable changes to Life Progress are recorded here.

The format is based on Keep a Changelog, and the project uses semantic versioning.

## [Unreleased]

## [0.1.1] - 2026-11-19

### Added
- Added candidate-image regression testing before release and deployment.
- Added an in-app Changelog page.
- Added Changelog links to the application navigation and footer.

### Changed
- Added the current application version beneath the Life Progress name in the application header.
- Changed the profile name placeholder from "Matt" to the generic "Name".

### Fixed
- Fixed candidate-image test execution so the application package is imported from the container working directory.
- Fixed the Changelog page returning HTTP 500 by avoiding the Jinja dictionary `items()` name collision.
- Fixed the Changelog page returning HTTP 500 because the Jinja template treated the changelog `items` value as the dictionary `items()` method.

### Security
- Removed the Docker host's private network address from public source and documentation; deployment binding is now configurable through `LIFE_PROGRESS_BIND`.

## [0.1.0] - 2026-11-18

### Added
- Initial Life Progress self-hosted web application.
- Personal profile with date of birth and configurable lifespan.
- Age and lifetime statistics in days, weeks, and months.
- Life progress and current-year progress indicators.
- Responsive life-in-weeks visualization.
- Important-person tracking with configurable age milestones.
- Custom milestone tracking.
- Remaining day, week, Saturday, and Christmas calculations.
- SQLite persistence.
- Responsive dark and light interface.
- Dockerfile and Docker Compose deployment.
- Container health check and `/health` endpoint.
- Initial README.
- MIT license.
