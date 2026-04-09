# Changelog

All notable changes to the fluss-api package will be documented in this file.

## [0.2.3] - 2026-04-09

### Changed

- Removed build artifacts (`__pycache__/`, `.egg-info/`) from the repository
- Updated `.gitignore` to exclude `__pycache__/`, `*.pyc`, `*.egg-info/`, `dist/`, and `build/`

## [0.2.2] - 2025

### Changed

- Version bump for cleaner package versioning

## [0.2.1.2]

### Fixed

- Fixed API call URLs

## [0.2.1.1]

### Fixed

- Fixed package publishing configuration

## [0.2.1]

### Changed

- Updated wording and descriptions

## [0.2.0]

### Changed

- Migrated to new Fluss API v1 domain (`v1.fluss-api.com`)
- Added `async_open_device()` and `async_close_device()` methods
- Added `async_get_device_status()` method
- Improved error handling for DNS resolution failures
- New API documentation: https://fluss.io/docs

## [0.1.9.20]

- Baseline version integrated into Home Assistant

[0.2.3]: https://github.com/fluss/Fluss_Python_Library/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/fluss/Fluss_Python_Library/compare/v0.2.1.2...v0.2.2
[0.2.1.2]: https://github.com/fluss/Fluss_Python_Library/compare/v0.2.1.1...v0.2.1.2
[0.2.1.1]: https://github.com/fluss/Fluss_Python_Library/compare/v0.2.1...v0.2.1.1
[0.2.1]: https://github.com/fluss/Fluss_Python_Library/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/fluss/Fluss_Python_Library/compare/v0.1.9.20...v0.2.0
[0.1.9.20]: https://github.com/fluss/Fluss_Python_Library/commit/633338c
