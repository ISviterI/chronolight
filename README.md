# chronolight

[![Discord](https://img.shields.io/discord/1488880281376260186?color=7289da&label=discord&logo=discord&logoColor=white)](https://discord.gg/MXv3KTFmPE)

A simple library for working with timelines and delayed calls.

## Installation

```bash
pip install chronolight
```

## Quick Start

```python
import chronolight

# Timeline
tl = chronolight.Timeline()
tl.wait(1)
tl.call(lambda: print("1 second passed"))
tl.wait(0.5)
tl.call(lambda: print("Another 0.5 seconds passed"))
tl.run()

# Delayed call
chronolight.delay(2, lambda: print("After 2 seconds"))
```

## Methods

### `Timeline`

| Method                 | Description          |
|:-----------------------|:---------------------|
| `.wait(seconds)`       | Adds a delay         |
| `.call(func)`          | Adds a function call |
| `.run(threaded=False)` | Runs the timeline    |

### `delay(seconds, function)`

Executes a function after N seconds (in a separate thread).