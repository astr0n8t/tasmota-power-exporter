# Tasmota Power Exporter

A custom exporter for Prometheus for the Tasmota open source smart plug firmware.

Allows you to collect metrics directly from individual smart plugs without the use of HomeAssistant or something similar.

## Grafana Dashboard

Available in [grafana.json](./grafana.json)

![grafana](./grafana.png)

## Deployment

The GitHub actions pipeline automatically builds Docker images for ARM and x86 devices for simplified deployment.

Docker-Compose:
```
  tasmota:
    image: ghcr.io/astr0n8t/tasmota-power-exporter:latest
    container_name: tasmota-power
    restart: always
    ports:
    - 8000:8000
    environment:
    - EXPORTER_PORT: 8000 #optional, default to 8000
```

Prometheus Config:
```
- job_name: "tasmota"
    metrics_path: /probe
    scheme: http # change it to https if needed
    static_configs:
      - targets:
        - 192.168.1.180
        - 192.168.1.190
        - xxx.yyy.zzz.hhh
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: device
      - target_label: __address__
        replacement: 127.0.0.1:8000
    # If password protected
    # - target_label: __param_user
    #   replacement: 'admin'
    # - target_label: __param_password
    #   replacement: 'mysupernotsimplepassword'
```

we can specify our targets in target section.

## Development

Perform the following:

```
git clone https://github.com/astr0n8t/tasmota-power-exporter.git
cd tasmota-power-exporter
pip install -r requirements.txt
pip install -r requirements-dev.txt # unit tests
```

All of the exporter code is found in [metrics.py](./metrics.py).

## Contributors

- [Nathan Higley](https://github.com/astr0n8t)
- [brokenpip3](https://github.com/brokenpip3)
