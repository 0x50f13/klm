# KLMd

Keyboard Light Management daemon written in rust.
<p>
 Keyboard light management daemon allows to work with drivers in order to set keyboard lightning.
 The main aim of it is to be extensible. Further it would be able to load drivers dynamically, but currently only has a hard-coded driver for MS-1563 keyboard.
</p>

## Requirements

* rust
    * hidapi crate
* [build.sh](https://github.com/Andrewerr/build.sh) (for installation)

## Building and installing

You can build this daemon with `cargo build` or using my [build.sh](https://github.com/Andrewerr/build.sh) building
framework. For installing it use [build.sh](https://github.com/Andrewerr/build.sh):

```
build install
```

## systemd

The daemon has integration with systemd, so you can start it with:

```
systemctl start klmd
```

and enable it with:

```
systemctl enable klmd
```

## API

The daemon itself only listens for external communincation at UNIX-socket stream `/var/run/klmd.sock`.
The workflow of communincation is as follows:

* Client opens connection to klmd
* Client writes packet header: size of packet
* Client writes packet data
* klmd responses with status code for request
* Client closes connection

### Packet structure

Below table illustrates a structure of a request to klmd:

| Size   | Command 1 | Command 1 arguments | ... | Command n | Command n arguments |
|--------|-----------|---------------------|-----|-----------|---------------------|
| 1 byte | 1 byte    | m_1 bytes           | ... | 1 byte    | m_n bytes           |

### Color encoding

Colors are alway encoded as RGB byte triplet(see table below)
|Red |Green |Blue |
|-------|---------|-------|
|1 byte |1 byte |1 byte |

### Command table

| Command | Arguments        | Description                                        |
|---------|------------------|----------------------------------------------------|
| 0x0     | n, then n colors | Sets vector of stored color to given n colors      |
| 0x1     | Color            | Sets primary color, resets stored colors           |
| 0x2     | Color            | Adds color to stored colors vector                 |
| 0x3     | Brightness       | Set keyboard Brightness                            |
| 0x4     | Speed            | Set keyboard speed for color shift or breathe mode |
| 0x5     | Mode             | Set keyboard mode                                  |
| 0x7     | Power            | Set keyboard power                                 |
| 0x8     | -                | Toggle keyboard power, saving state                |
| 0x9     | -                | Get keyboard modes                                 |

**NOTE**: Speed, mode, power and brightness are 1-byte values(see tables below).

### Power table

Power argument possible values.

| Value | Description |
|-------|-------------|
| 0x0   | Power-off   |
| 0x1   | Power-on    |

**NOTE**: to power-on keyboard currently mode should be sent as keyboard state is not yet cached.

### Mode table

| Value | Description              |
|-------|--------------------------|
| 0x0   | Turn offs lightning      |
| 0x1   | Steady lightning         |
| 0x2   | Breathing lightning      |
| 0x3   | Color-shifting lightning |

### Packet size examples

Here you can find examples of how to design packets for klmd.

#### Sending color vector

| ... | Command | Number of colors | Color 1  | ... | Color n  | ... |
|-----|---------|------------------|----------|-----|----------|-----|
| ... | 1 byte  | 1 byte           | 3 bytes  | ... | 3 bytes  | ... |
| ... | 0x1     | n                | r1,g1,b1 | ... | rn,gn,bn | ... |

### Mode changing

| ... | Command | Mode   | ... |
|-----|---------|--------|-----|
| ... | 1 byte  | 1 byte | ... |
| ... | 0x5     | mode   | ... |

## klmd responses

Here the responses of klmd on socket request are explained.

### Modes

You will receive a following frames when getting modes.

| Number of modes | Mode1  | ... | Moden  |
|-----------------|--------|-----|--------|
| 1 byte          | 1 byte | ... | 1 byte |
| Count of modes  | Mode   | ... | Mode   |

#### Table of modes

| Mode code | Description  |
|-----------|--------------|
| 0x1       | Steady state |
| 0x2       | Breathing    |
| 0x3       | Colorshift   |

## TODO

* [x] Systemd, AppArmor, build.sh
* [ ] Dynamically loadable drivers
* [ ] Ability for clients to get keyboard features
* [x] Keyboard state caching
* [ ] Proper UNIX-signal handling
