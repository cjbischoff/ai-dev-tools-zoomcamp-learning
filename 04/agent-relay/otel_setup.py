"""OpenTelemetry instrumentation for Agent Relay.

Configures traces, metrics, and structured-log export via OTLP to an
OpenTelemetry Collector.  Environment variables control the endpoint:

- ``OTEL_EXPORTER_OTLP_ENDPOINT`` — OTLP gRPC endpoint (default
  ``http://localhost:4317``)
- ``OTEL_SERVICE_NAME`` — service identity (default ``agent-relay``)

Call :func:`setup_otel` once at application startup, passing the FastAPI app
instance.
"""

from __future__ import annotations

import logging
import os

import opentelemetry.instrumentation.fastapi  # noqa: F401  # side-effect imports
from opentelemetry import _logs as otel_logs
from opentelemetry import metrics as otel_metrics
from opentelemetry import trace as otel_trace
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from fastapi import FastAPI


LOGGER = logging.getLogger("agent_relay.otel")


def setup_otel(app: FastAPI) -> None:
    """Configure OpenTelemetry for the given FastAPI application.

    Installs trace, metric, and log providers backed by OTLP gRPC exporters,
    instruments the FastAPI app for automatic HTTP span/metric generation, and
    instruments the standard ``logging`` module for log correlation.
    """
    otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    service_name = os.getenv("OTEL_SERVICE_NAME", "agent-relay")

    resource = Resource.create({SERVICE_NAME: service_name})

    # --- Traces ---
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=otel_endpoint))
    )
    otel_trace.set_tracer_provider(tracer_provider)

    # --- Metrics ---
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=otel_endpoint)
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    otel_metrics.set_meter_provider(meter_provider)

    # --- Logs ---
    log_provider = LoggerProvider(resource=resource)
    log_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=otel_endpoint))
    )
    otel_logs.set_logger_provider(log_provider)

    # --- Instrumentation ---
    FastAPIInstrumentor.instrument_app(app)
    LoggingInstrumentor().instrument(set_logging_format=True)

    LOGGER.info(
        "OpenTelemetry initialised — exporting to %s (service=%s)",
        otel_endpoint,
        service_name,
    )
