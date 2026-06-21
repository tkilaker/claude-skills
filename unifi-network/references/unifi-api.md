# UniFi API Reference

## Key Types

Tim currently has a Site Manager API key. It works with `https://api.ui.com/v1` and the connector proxy.

If a local Network API key is created later, local direct calls use:

```bash
curl -k -H "X-API-KEY: $UNIFI_API_KEY" \
  https://192.168.1.1/proxy/network/integration/v1/info
```

A Site Manager key returns `401` on that local endpoint. Use connector mode instead.

## Site Manager

```bash
curl -H "X-API-KEY: $UNIFI_API_KEY" https://api.ui.com/v1/hosts
curl -H "X-API-KEY: $UNIFI_API_KEY" https://api.ui.com/v1/sites
curl -H "X-API-KEY: $UNIFI_API_KEY" https://api.ui.com/v1/devices
```

The host ID looks like:

```text
1C0B...67FD204A:2117568993
```

## Network Connector

Connector base:

```text
https://api.ui.com/v1/connector/consoles/{hostId}/proxy/network
```

Useful paths:

```text
integration/v1/info
integration/v1/sites
api/s/default/stat/sta
api/s/default/rest/user
api/s/default/stat/device
```

Examples:

```bash
curl -L -g -H "X-API-KEY: $UNIFI_API_KEY" \
  "https://api.ui.com/v1/connector/consoles/$HOST_ID/proxy/network/api/s/default/rest/user"
```

## DHCP Reservations

Known clients live under:

```text
api/s/default/rest/user
api/s/default/rest/user/{_id}
```

Reservation fields observed in Tim's controller:

```json
{
  "use_fixedip": true,
  "fixed_ip": "192.168.1.94"
}
```

Use `PUT` to update an existing client object. Preserve the existing object and patch only `use_fixedip` and `fixed_ip`.

## Docs

- Ubiquiti help: https://help.ui.com/hc/en-us/articles/30076656117655-Getting-Started-with-the-Official-UniFi-API
- Developer portal: https://developer.ui.com/
- Local docs in UniFi Network: Settings -> Integrations
