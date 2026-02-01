# Simple Maps

[![MIT License](https://img.shields.io/badge/license-MIT-007EC7.svg?style=flat-square)](/LICENSE)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/simple-maps.svg)](https://pypi.org/project/simple-maps)
[![Downloads](https://pepy.tech/badge/simple-maps)](https://pepy.tech/project/simple-maps)
[![Code Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen.svg?style=flat-square)](/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![BuyMeACoffee](https://img.shields.io/badge/%E2%98%95-buymeacoffee-ffdd00)](https://www.buymeacoffee.com/jbsilva)

A Python client and CLI for [Cartes.io](https://cartes.io), a free and open-source mapping platform.

Create interactive maps with markers directly from Python code or the command line.

## ✨ Features

- **Full API Coverage** - Maps, markers, categories, users, and more
- **CLI & Library** - Use from the terminal or import in your Python code
- **Zero Config** - Works out of the box, no API key needed for public maps

## 📦 Installation

```bash
pip install simple-maps
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add simple-maps
```

## 🚀 Quick Start

### Python API

```python
from simple_maps import Cartes, MapCreatePayload, MarkerCreatePayload, Privacy

# Initialize the client
api = Cartes()

# Create a new map
response = api.map_create(MapCreatePayload(
    title="Coffee Shops in NYC",
    description="My favorite places to grab coffee",
    privacy=Privacy.PUBLIC,
))

map_id = response["uuid"]
map_token = response["token"]  # Save this to edit the map later

# Add a marker
api.marker_create(map_id, MarkerCreatePayload(
    map_token=map_token,
    lat=40.7128,
    lng=-74.0060,
    category_name="Coffee",
    description="Best espresso in Manhattan",
))

# List all public maps
maps = api.map_list()
```

### Command Line

```bash
# Create a map
simple_maps map create --title "My Map" --privacy public

# Get map details
simple_maps map get --map-id <UUID>

# Add a marker
simple_maps marker create \
    --map-id <UUID> \
    --map-token <TOKEN> \
    --lat 40.7128 \
    --lng -74.0060 \
    --category-name "Location" \
    --description "A point of interest"

# List markers on a map
simple_maps marker list --map-id <UUID>

# Search for maps
simple_maps map search --query "coffee"
```

## 📖 CLI Reference

### Map Commands

| Command                                               | Description                    |
| ----------------------------------------------------- | ------------------------------ |
| `map list`                                            | List all public maps           |
| `map search --query TEXT`                             | Search maps by keyword         |
| `map get --map-id UUID`                               | Get details of a specific map  |
| `map create [OPTIONS]`                                | Create a new map               |
| `map edit --map-id UUID --token TOKEN [OPTIONS]`      | Edit an existing map           |
| `map delete --map-id UUID --token TOKEN`              | Delete a map                   |
| `map claim --map-id UUID --token TOKEN --api-key KEY` | Claim anonymous map ownership  |
| `map static-image --map-id UUID`                      | Get static image URL for a map |

### Marker Commands

| Command                                                                 | Description               |
| ----------------------------------------------------------------------- | ------------------------- |
| `marker list --map-id UUID`                                             | List all markers on a map |
| `marker create --map-id UUID --map-token TOKEN --lat FLOAT --lng FLOAT` | Create a marker           |
| `marker edit --map-id UUID --marker-id ID --token TOKEN`                | Edit a marker             |
| `marker delete --map-id UUID --marker-id ID --token TOKEN`              | Delete a marker           |
| `marker spam --map-id UUID --marker-id ID`                              | Report a marker as spam   |

### Category Commands

| Command                             | Description                |
| ----------------------------------- | -------------------------- |
| `category list --map-id UUID`       | List categories on a map   |
| `category search --query TEXT`      | Search categories globally |
| `category related --category-id ID` | Get related categories     |

### User Commands

| Command                             | Description                 |
| ----------------------------------- | --------------------------- |
| `user list`                         | List all users              |
| `user get --username TEXT`          | Get user profile            |
| `me get --api-key KEY`              | Get authenticated user info |
| `me update --api-key KEY [OPTIONS]` | Update your profile         |

## 🔧 API Reference

### Models

All request payloads use Pydantic models with built-in validation:

```python
from simple_maps import (
    MapCreatePayload,      # Create/edit maps
    MapListParams,         # Filter map listings
    MarkerCreatePayload,   # Create markers (validates coordinates)
    MarkerLocationPayload, # Add location history to markers
    Privacy,               # PUBLIC, UNLISTED, PRIVATE
    Permission,            # YES, NO, LOGGED
)
```

### Cartes Client Methods

```python
api = Cartes(base_url="https://cartes.io/api")  # Custom base URL optional

# Maps
api.map_list(params=None, api_key=None)
api.map_search(query, api_key=None)
api.map_get(map_uuid, api_key=None)
api.map_create(payload=None, api_key=None)
api.map_edit(map_token, map_id, payload, api_key=None)
api.map_delete(map_token, map_id, api_key=None)

# Markers
api.marker_list(map_id, show_expired=None, response_format=None, api_key=None)
api.marker_create(map_id, payload, api_key=None)
api.marker_edit(marker_token, map_id, marker_id, description=None, api_key=None)
api.marker_delete(marker_token, map_id, marker_id, api_key=None)

# Categories
api.category_list(map_id, api_key=None)
api.category_search(query, api_key=None)
api.category_related(category_id, api_key=None)

# Users
api.user_list(api_key=None)
api.user_get(username, with_maps=None, with_markers=None, api_key=None)
api.me_get(api_key)
api.me_update(api_key, username=None, description=None)
```

## 🛡️ Validation

Pydantic validates all inputs automatically:

```python
from simple_maps import MarkerCreatePayload
from pydantic import ValidationError

try:
    # This will raise ValidationError - latitude must be between -90 and 90
    MarkerCreatePayload(
        map_token="token",
        lat=200.0,  # Invalid!
        lng=0.0,
        category=1,
    )
except ValidationError as e:
    print(e)
    # lat: Input should be less than or equal to 90
```

## 🔗 Links

- [Cartes.io](https://cartes.io) - The mapping platform
- [Cartes.io API Docs](https://github.com/M-Media-Group/Cartes.io/wiki/API) - Official API
  documentation
- [GitHub Repository](https://github.com/jbsilva/simple-maps) - Source code
- [PyPI Package](https://pypi.org/project/simple-maps/) - Python package

## 📄 License

MIT License - see [LICENSE](/LICENSE) for details.
