# homebrew-minfwm

Homebrew tap for [minfwm](https://github.com/snusxd/minfwm), an infinite 2D
window canvas for macOS.

## Install

```sh
brew install snusxd/minfwm/minfwm
```

This formula builds the stable source release with CMake. It requires macOS 14
(Sonoma) or newer and supports both Apple Silicon and Intel Macs. After
installation, grant `minfwmd` Accessibility permission in System Settings, then
run `minfwm enable` to install and start its per-user LaunchAgent.

GitHub Actions checks for a newer stable upstream release every 15 minutes and
updates the formula automatically. You can also run the update workflow from
the tap's Actions tab.

The upstream repository does not currently publish a software license.
