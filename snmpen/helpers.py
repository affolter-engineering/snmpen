"""Helper functions for SNMPen."""

import argparse
import ipaddress
import re

COMMUNITY_MAX_LENGTH = 32
PORT_MAX = 65535
RETRIES_MAX = 10
IPV4_LABEL_COUNT = 4
IPV4_MIN_NUMERIC_LABELS = 3


def community_type(value):
    """Validate SNMP community string length."""
    if len(value) >= COMMUNITY_MAX_LENGTH:
        msg = "Community string must be shorter than 32 chars"
        raise argparse.ArgumentTypeError(msg)
    return value


def port_type(value):
    """Validate SNMP port range."""
    port = int(value)
    if not (0 <= port <= PORT_MAX):
        msg = "Port must be between 0 and 65535"
        raise argparse.ArgumentTypeError(msg)
    return port


def retries_type(value):
    """Validate request retries range."""
    retries = int(value)
    if not (0 <= retries <= RETRIES_MAX):
        msg = "Retries must be between 0 and 10"
        raise argparse.ArgumentTypeError(msg)
    return retries


def target_type(value):
    """Validate that IP literals are well-formed while allowing hostnames."""
    try:
        ipaddress.ip_address(value)
    except ValueError:
        pass
    else:
        return value

    if ":" in value:
        msg = f"Invalid IP address: {value}"
        raise argparse.ArgumentTypeError(msg)

    labels = value.split(".")
    numeric_labels = sum(label.isdigit() for label in labels)
    if len(labels) == IPV4_LABEL_COUNT and numeric_labels >= IPV4_MIN_NUMERIC_LABELS:
        msg = f"Invalid IP address: {value}"
        raise argparse.ArgumentTypeError(msg)

    return value


def target_to_output_filename(target):
    """Create a safe output filename from a target name."""
    safe_target = re.sub(r"[^A-Za-z0-9._-]", "_", target).strip("._")
    if not safe_target:
        safe_target = "snmp-target"
    return f"{safe_target}.txt"
