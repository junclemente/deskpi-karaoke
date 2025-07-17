# Changelog

All notable changes to this project will be documented in this file.

## [v0.2.0] - 2025-07-16

### Added

- Autostart script waits for Wi-Fi before launching PiKaraoke
- Zenity popups to inform the user
- Wi-Fi GUI opens if no connection is found
- Desktop autostart integration

### Changed

- install.sh now copies the launcher script instead of embedding it

### Removed

- CI ShellCheck linting step (temporarily)

### Fixed

- Git pull conflict on install.sh due to chmod
- ShellCheck false-positive for `source`
