Watch steaming videos on your Apple TV

---

## Getting Started

Install `watch` using `pip`:

```
> pip install -U git+https://github.com/sesh/watch@master
```


## Usage

Figure our your Apple TV's IP address (Settings > Network) then export it to `APPLE_TV_IP`:

```
> export APPLE_TV_IP=10.1.1.12
```

Play a stream on your Apple TV from the command line with:

```
> watch https://www.youtube.com/watch?v=UfJ-i4Y6DGU
```

Currently `watch` supports videos from a wide range of sources including YouTube, Vimeo, Streamable and other
online streaming services supported by [youtube-dl](https://github.com/rg3/youtube-dl).


### Full Usage

`watch` offers options for overriding the IP address of your Apple TV and starting the video somewhere other
that the beginning:

```
Usage:
    watch <video_url> [--verbose] [--apple-tv=<atv>] [--start=<start>]

Options:
    --start=<start>       Time (hh:mm:ss) or percentage complete (0.xx) to start through the stream [default: 0.0]
    --apple-tv=<atv>      Override the APPLE_TV_IP environment variable
    --verbose             Enable detailed logging for debugging
```

You'll want to include `export APPLE_TV_IP=10.1.1.12` in your `~/.bash_profile` (or equivalent).


## Thanks

- The fantastic [youtube-dl](https://github.com/rg3/youtube-dl) powers the grabbing of most video URLs
- Clément Vasseur's [Unofficial AirPlay Protocol Specification](https://nto.github.io/AirPlay.html) was invaluable
  when writing the Airplay related code.
