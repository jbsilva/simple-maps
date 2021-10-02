# Simple Maps

[![MIT License](https://img.shields.io/badge/license-MIT-007EC7.svg?style=flat-square)](/LICENSE)
[![Code Style Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black/)
[![PyPI version](https://badge.fury.io/py/simple-maps.svg)](https://pypi.org/project/simple-maps)
[![Downloads](https://pepy.tech/badge/simple-maps)](https://pepy.tech/project/simple-maps)
[![BuyMeACoffee](https://img.shields.io/badge/%E2%98%95-buymeacoffee-ffdd00)](https://www.buymeacoffee.com/jbsilva)

This program allows the creation of maps with markers directly from the command
line.


## Installation

```console
$ pip install simple-maps
```

## Features

Simple Maps interacts with the cartes.io API to provide the following
functionality:

- Create a map with parameters: `map create`
- Get information about a map: `map get`
- Delete a map: `map delete`
- Create a marker on a map: `marker create`
- List all markers on a map: `marker list`
- Edit marker description: `marker edit`
- Delete a marker: `marker delete`


**Usage**:

```console
$ simple_maps [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `map`
* `marker`

## `simple_maps map`

**Usage**:

```console
$ simple_maps map [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a map.
* `delete`: Delete a single map.
* `get`: Get a single map.

### `simple_maps map create`

Create a map.

**Usage**:

```console
$ simple_maps map create [OPTIONS]
```

**Options**:

* `--title TEXT`: The title of the map
* `--slug TEXT`: The map slug. Currently un-used
* `--description TEXT`: The description of the map and its purpose
* `--privacy [public|unlisted|private]`: The privacy level of the map: public, unlisted, private
* `--users-can-create-markers [yes|no|only_logged_in]`: The setting that defines who can create markers
* `--help`: Show this message and exit.

### `simple_maps map delete`

Delete a single map.

**Usage**:

```console
$ simple_maps map delete [OPTIONS]
```

**Options**:

* `--token TEXT`: Token  [required]
* `--map-id TEXT`: Map id  [required]
* `--help`: Show this message and exit.

### `simple_maps map get`

Get a single map.

**Usage**:

```console
$ simple_maps map get [OPTIONS]
```

**Options**:

* `--map-id TEXT`: Id of the map  [required]
* `--help`: Show this message and exit.

## `simple_maps marker`

**Usage**:

```console
$ simple_maps marker [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a marker on a map.
* `delete`: Delete a marker on a map.
* `edit`: Edit a marker on a map.
* `list`: Get all markers on a map.

### `simple_maps marker create`

Create a marker on a map.

**Usage**:

```console
$ simple_maps marker create [OPTIONS]
```

**Options**:

* `--map-token TEXT`: Map token  [required]
* `--map-id TEXT`: Map id  [required]
* `--lat FLOAT RANGE`: The lat position of the marker  [required]
* `--lng FLOAT RANGE`: The lng position of the marker  [required]
* `--category INTEGER`: Category ID. Use category_name if you don't know the ID
* `--category-name TEXT`: Category name
* `--description TEXT`: Marker description
* `--help`: Show this message and exit.

### `simple_maps marker delete`

Delete a marker on a map.

**Usage**:

```console
$ simple_maps marker delete [OPTIONS]
```

**Options**:

* `--token TEXT`: Token  [required]
* `--map-id TEXT`: Map id  [required]
* `--marker-id TEXT`: Marker id  [required]
* `--help`: Show this message and exit.

### `simple_maps marker edit`

Edit a marker on a map.

**Usage**:

```console
$ simple_maps marker edit [OPTIONS]
```

**Options**:

* `--token TEXT`: Marker token  [required]
* `--map-id TEXT`: Map id  [required]
* `--marker-id TEXT`: Marker id  [required]
* `--description TEXT`: Marker description
* `--help`: Show this message and exit.

### `simple_maps marker list`

Get all markers on a map.

**Usage**:

```console
$ simple_maps marker list [OPTIONS]
```

**Options**:

* `--map-id TEXT`: Map id  [required]
* `--show-expired / --no-show-expired`: Show markers that have already expired
* `--help`: Show this message and exit.
