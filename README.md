# Codex Stalker

<p align="center">
  <img src="https://github.com/user-attachments/assets/a04647da-f951-48b9-bdd5-76d1e28e4faa" />
</p>

> A tool for monitoring and getting notifications about what is happening with your [Codex](https://codex.storage) node.
> Mainly focusing on Codex's Marketplace — tracking purchases, sales, etc.

## Installation

The easiest is to run a Docker image, which should work out of the box:

```sh
$ docker run -it auhau/codex-stalker
```

For Linux machines, you need to run it with extra parameter:

```shell
$ docker run -it --add-host=host.docker.internal:host-gateway auhau/codex-stalker

```

This expect that your Codex node is running on the same machine under the default port `8080`.
You can customize this using the `CODEX_API_URL` env. variable as seen below.

## Configuration

| ENV. Variable name                       | Default                  | Description                                                                                            |
|------------------------------------------|--------------------------|--------------------------------------------------------------------------------------------------------|
| `AVAILABILITY_SIZE_THRESHOLD_PERCENTAGE` | `20`                     | Percentage threshold under which when the availability's capacity falls bellow, notifications kicks in |
| `DB`                                     | `database.db`            | Place where the SQLite DB will be persisted                                                            |
| `CODEX_API_URL`                          | `http://localhost:8080/` | URL where Codex's API endpoint listens on                                                              |
| `POLL_INTERVAL`                          | `5`                      | Interval in seconds how often stalker checks for new values                                            |
| `FULL_IDS`                               | None                     | If set, then will refer to the detected entities with their full IDs and will not shorten them         |
| `DISABLE_CONSOLE`                        | None                     | Disable console output of the detected events                                                          |

## Notifiers

### NTFY.sh

[ntfy.sh](https://ntfy.sh/) is a service for delivering push notifications across all sort of devices. 
You can also easily self-host it, if interested.

To enable this notifier, configure a topic for your notifications with env. variable `NTFY_TOPIC`.
Other options are:

 - `NTFY_TOPIC` - topic under which the notification will be sent
 - `NTFY_HOST` (default: `https://ntfy.sh/`) - host instance of NTFY.sh
 - `NTFY_USER` - if the host instance requires authentication, here you specify the username
 - `NTFY_PASSWORD` - if the host instance requires authentication, here you specify the password

## What is monitored?

This Stalker watches a few metrics around Codex's Availabilities, Slots, and Purchases. It notifies about these events:

- **Availabilities**
    - Availability's free size fell below the threshold (`AVAILABILITY_SIZE_THRESHOLD_PERCENTAGE`).
    - New Availability was added.
- **Purchases**
    - A new purchase was created.
    - Existing purchase's state changed.
- **Slots**
    - A new slot was filled by your node, and it is hosting it now.
    - Existing slot's state changed.
