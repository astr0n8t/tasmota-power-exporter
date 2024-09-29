#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import signal
import httpx
import asyncio
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily
from prometheus_client import generate_latest, CollectorRegistry
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import PlainTextResponse, Response
import uvicorn
from os import getenv


class TasmotaCollector(object):
    def __init__(self, ip, user=None, password=None):
        self.ip = ip
        self.user = user
        self.password = password

    def collect(self):
        response = asyncio.run(self.fetch())

        for key in response:
            metric_name = "tasmota_" + key.lower().replace(" ", "_")
            metric = response[key].split()[0]
            unit = None
            if len(response[key].split()) > 1:
                unit = response[key].split()[1]

            if (
                "today" in metric_name
                or "yesterday" in metric_name
                or "total" in metric_name
            ):
                r = CounterMetricFamily(metric_name, key, labels=["device"], unit=unit)
            else:
                r = GaugeMetricFamily(metric_name, key, labels=["device"], unit=unit)
            r.add_metric([self.ip], metric)
            yield r

    async def fetch(self):
        url = f"http://{self.ip}/?m=1"
        async with httpx.AsyncClient() as client:
            if self.user and self.password:
                auth = httpx.BasicAuth(self.user, self.password)
            else:
                auth = None

            page = await client.get(url, auth=auth)

            if page.status_code != 200:
                raise HTTPException(
                    status_code=page.status_code,
                    detail="Failed to fetch data from device",
                )

            values = {}
            string_values = str(page.text).split("{s}")
            for i in range(1, len(string_values)):
                try:
                    label = string_values[i].split("{m}")[0]
                    value = string_values[i].split("{m}")[1].split("{e}")[0]
                    if "<td" in value:
                        value = value.replace("</td><td style='text-align:left'>", "")
                        value = value.replace("</td><td>&nbsp;</td><td>", "")
                    values[label] = value
                except IndexError:
                    continue
            return values


app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
def root():
    return (
        "Welcome to Tasmota prometheus exporter!\n"
        "Use the /probe endpoint with the 'target' query parameter to get metrics from a Tasmota device.\n"
        "Example: /probe?target=192.168.1.1\n"
    )


@app.get("/probe")
def probe(target: str = Query(...), user: str = None, password: str = None):
    try:
        registry = CollectorRegistry()
        collector = TasmotaCollector(target, user, password)
        registry.register(collector)
        metrics = generate_latest(registry)
        return Response(content=metrics, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def signal_handler(signal, frame):
    print(f"Signal {signal} caught, shutting down gracefully...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    port = int(getenv("EXPORTER_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
