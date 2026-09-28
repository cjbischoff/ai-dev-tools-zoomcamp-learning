"""OpenTelemetry instrumentation for Order Tracker.

Configures traces, metrics, and logs.  Controlled by environment variable:

- ``OTEL_EXPORTER_OTLP_ENDPOINT`` — when set, exports to that OTLP endpoint.
  When unset, exports to console (stdout) via ConsoleSpanExporter and
  ConsoleMetricExporter so you can inspect signals with
  ``docker compose logs app``.

Call :func:`setup_otel` once during application startup, passing the FastAPI
app instance after all routes are registered.
"""

from __future__ import annotations

import os

from opentelemetry import _logs as otel_logs
from opentelemetry import metrics as otel_metrics
from opentelemetry import trace as otel_trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, SimpleLogRecordProcessor
from opentelemetry.sdk._logs.export import ConsoleLogExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor
from fastapi import FastAPI


def setup_otel(app: FastAPI) -> None:
    """Initialise OpenTelemetry for Order Tracker.

    Uses ``OTEL_EXPORTER_OTLP_ENDPOINT`` to decide between console and OTLP
    export.  Falls back to console when the variable is unset.
    """
    otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    service_name = os.getenv("OTEL_SERVICE_NAME", "order-tracker")
    resource = Resource.create({SERVICE_NAME: service_name})

    # --- Traces ---
    tracer_provider = TracerProvider(resource=resource)
    if otel_endpoint:
        tracer_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=otel_endpoint))
        )
    else:
        tracer_provider.add_span_processor(
            SimpleSpanProcessor(ConsoleSpanExporter())
        )
    otel_trace.set_tracer_provider(tracer_provider)

    # --- Metrics ---
    if otel_endpoint:
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=otel_endpoint)
        )
    else:
        metric_reader = PeriodicExportingMetricReader(
            ConsoleMetricExporter()
        )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    otel_metrics.set_meter_provider(meter_provider)

    # --- Logs ---
    log_provider = LoggerProvider(resource=resource)
    if otel_endpoint:
        from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter  # noqa: PLC0415
        log_provider.add_log_record_processor(
            BatchLogRecordProcessor(OTLPLogExporter(endpoint=otel_endpoint))
        )
    else:
        log_provider.add_log_record_processor(
            SimpleLogRecordProcessor(ConsoleLogExporter())
        )
    otel_logs.set_logger_provider(log_provider)

    # --- Instrumentation ---
    FastAPIInstrumentor.instrument_app(app)
    LoggingInstrumentor().instrument(set_logging_format=True)
