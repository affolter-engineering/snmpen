"""Unit tests for snmpen's core functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

from snmpen.snmpen import (
    detect_supported_snmp_versions,
    snmp_get,
    snmp_set,
    snmp_walk,
)


class TestSnmpGet:
    """Tests for snmp_get."""

    async def test_returns_value_on_success(self):
        """If the get command succeeds without error indication or status, snmp_get should return the value."""
        var_binds = [("1.3.6.1.2.1.1.1.0", "RouterOS")]
        with patch("snmpen.snmpen.get_cmd", new=AsyncMock(return_value=(None, None, None, var_binds))):
            result = await snmp_get(MagicMock(), MagicMock(), MagicMock(), "1.3.6.1.2.1.1.1.0")
        assert result == "RouterOS"

    async def test_returns_none_on_error_indication(self):
        """If there's an error indication, snmp_get should return None."""
        with patch("snmpen.snmpen.get_cmd", new=AsyncMock(return_value=("timeout", None, None, []))):
            result = await snmp_get(MagicMock(), MagicMock(), MagicMock(), "1.3.6.1.2.1.1.1.0")
        assert result is None

    async def test_returns_none_on_error_status(self):
        """If there's an error status, snmp_get should return None."""
        with patch("snmpen.snmpen.get_cmd", new=AsyncMock(return_value=(None, "error", None, []))):
            result = await snmp_get(MagicMock(), MagicMock(), MagicMock(), "1.3.6.1.2.1.1.1.0")
        assert result is None

    async def test_returns_none_on_empty_var_binds(self):
        """If there are no var binds, snmp_get should return None."""
        with patch("snmpen.snmpen.get_cmd", new=AsyncMock(return_value=(None, None, None, []))):
            result = await snmp_get(MagicMock(), MagicMock(), MagicMock(), "1.3.6.1.2.1.1.1.0")
        assert result is None

    async def test_returns_none_on_exception(self):
        """If there's an exception (e.g. connection error), snmp_get should return None."""
        with patch("snmpen.snmpen.get_cmd", side_effect=Exception("connection refused")):
            result = await snmp_get(MagicMock(), MagicMock(), MagicMock(), "1.3.6.1.2.1.1.1.0")
        assert result is None


class TestSnmpSet:
    """Tests for snmp_set."""

    async def test_returns_true_on_success(self):
        """If the set command succeeds without error indication or status, snmp_set should return True."""
        with patch("snmpen.snmpen.set_cmd", new=AsyncMock(return_value=(None, None, None, None))):
            result = await snmp_set(MagicMock(), MagicMock(), MagicMock(), "1.3.6.1.2.1.1.5.0", "host")
        assert result is True

    async def test_returns_false_on_error_indication(self):
        """If there's an error indication, snmp_set should return False."""
        with patch("snmpen.snmpen.set_cmd", new=AsyncMock(return_value=("timeout", None, None, None))):
            result = await snmp_set(MagicMock(), MagicMock(), MagicMock(), "1.3.6.1.2.1.1.5.0", "host")
        assert result is False

    async def test_returns_false_on_error_status(self):
        """If there's an error status, snmp_set should return False."""
        with patch("snmpen.snmpen.set_cmd", new=AsyncMock(return_value=(None, "noAccess", None, None))):
            result = await snmp_set(MagicMock(), MagicMock(), MagicMock(), "1.3.6.1.2.1.1.5.0", "host")
        assert result is False

    async def test_returns_false_on_exception(self):
        """If there's an exception, snmp_set should return False."""
        with patch("snmpen.snmpen.set_cmd", side_effect=Exception("network error")):
            result = await snmp_set(MagicMock(), MagicMock(), MagicMock(), "1.3.6.1.2.1.1.5.0", "host")
        assert result is False


class TestSnmpWalk:
    """Tests for snmp_walk."""

    async def test_yields_nothing_on_error_indication(self):
        """If there's an error indication, snmp_walk should yield nothing."""
        with patch("snmpen.snmpen.next_cmd", new=AsyncMock(return_value=("timeout", None, None, []))):
            rows = [row async for row in snmp_walk(MagicMock(), MagicMock(), MagicMock(), ["1.3.6.1"])]
        assert rows == []

    async def test_yields_nothing_on_empty_var_binds(self):
        """If there are no var binds, snmp_walk should yield nothing."""
        with patch("snmpen.snmpen.next_cmd", new=AsyncMock(return_value=(None, None, None, []))):
            rows = [row async for row in snmp_walk(MagicMock(), MagicMock(), MagicMock(), ["1.3.6.1"])]
        assert rows == []

    async def test_yields_nothing_on_exception(self):
        """If there's an exception, snmp_walk should yield nothing."""
        with patch("snmpen.snmpen.next_cmd", side_effect=Exception("network error")):
            rows = [row async for row in snmp_walk(MagicMock(), MagicMock(), MagicMock(), ["1.3.6.1"])]
        assert rows == []


class TestDetectSupportedSnmpVersions:
    """Tests for detect_supported_snmp_versions."""

    async def test_detects_both_versions(self):
        """Both v1 and v2c respond successfully."""
        with patch("snmpen.snmpen.snmp_get", new=AsyncMock(return_value="Linux")):
            result = await detect_supported_snmp_versions(MagicMock(), MagicMock(), "public")
        assert result == ["SNMPv1", "SNMPv2c"]

    async def test_detects_no_versions_when_no_response(self):
        """No SNMP versions respond."""
        with patch("snmpen.snmpen.snmp_get", new=AsyncMock(return_value=None)):
            result = await detect_supported_snmp_versions(MagicMock(), MagicMock(), "public")
        assert result == []

    async def test_detects_only_v1(self):
        """Only SNMPv1 responds."""
        with patch("snmpen.snmpen.snmp_get", new=AsyncMock(side_effect=["Linux", None])):
            result = await detect_supported_snmp_versions(MagicMock(), MagicMock(), "public")
        assert result == ["SNMPv1"]

    async def test_detects_only_v2c(self):
        """Only SNMPv2c responds."""
        with patch("snmpen.snmpen.snmp_get", new=AsyncMock(side_effect=[None, "Linux"])):
            result = await detect_supported_snmp_versions(MagicMock(), MagicMock(), "public")
        assert result == ["SNMPv2c"]
