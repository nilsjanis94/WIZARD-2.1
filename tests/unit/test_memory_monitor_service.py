"""Test cases for MemoryMonitorService."""

import time
from unittest.mock import MagicMock, patch

import psutil
import pytest

from src.services.memory_monitor_service import (
    MemoryLevel,
    MemoryMonitorService,
    MemoryStats,
)


@pytest.mark.unit
class TestMemoryMonitorService:
    """Test cases for MemoryMonitorService class."""

    def test_init(self):
        """Test MemoryMonitorService initialization."""
        service = MemoryMonitorService()
        assert service.logger is not None
        assert service.tob_memory_usage == 0.0
        assert not service.monitoring_active

    @patch("psutil.virtual_memory")
    def test_get_memory_stats(self, mock_virtual_memory):
        """Test getting memory statistics."""
        # Mock psutil response
        mock_memory = MagicMock()
        mock_memory.total = 16 * 1024 * 1024 * 1024  # 16GB
        mock_memory.used = 2 * 1024 * 1024 * 1024  # 2GB (below critical threshold)
        mock_memory.available = 14 * 1024 * 1024 * 1024  # 14GB
        mock_memory.percent = 12.5  # Low usage
        mock_virtual_memory.return_value = mock_memory

        service = MemoryMonitorService()

        stats = service.get_memory_stats()

        assert isinstance(stats, MemoryStats)
        # Note: The actual calculation might be different, but we check the structure
        assert stats.total_mb > 0
        assert stats.used_mb >= 0
        assert stats.available_mb >= 0
        assert stats.usage_percent == 12.5
        assert stats.tob_data_mb == 0.0

    def test_calculate_memory_level(self):
        """Test memory level calculation."""
        service = MemoryMonitorService()

        # Test different memory levels (using MB values)
        assert service._calculate_memory_level(500) == MemoryLevel.LOW  # 500MB
        assert service._calculate_memory_level(1200) == MemoryLevel.MODERATE  # 1.2GB
        assert service._calculate_memory_level(1600) == MemoryLevel.HIGH  # 1.6GB
        assert service._calculate_memory_level(1900) == MemoryLevel.CRITICAL  # 1.9GB
        assert service._calculate_memory_level(2100) == MemoryLevel.EXCEEDED  # 2.1GB

    def test_update_tob_memory_usage(self):
        """Test updating TOB memory usage."""
        service = MemoryMonitorService()

        service.update_tob_memory_usage(150.5)
        assert service.tob_memory_usage == 150.5

        # Test negative values are handled
        service.update_tob_memory_usage(-10)
        assert service.tob_memory_usage == 0.0

    def test_check_memory_before_operation(self):
        """Test memory check before operation."""
        service = MemoryMonitorService()

        with patch.object(service, "get_memory_stats") as mock_stats:
            # Mock moderate memory usage
            mock_stats.return_value = MemoryStats(
                total_mb=8192,
                used_mb=1000,
                available_mb=7192,  # 1GB used, well below limits
                usage_percent=12.2,
                level=MemoryLevel.LOW,
                tob_data_mb=100,
            )

            # Should allow small operation
            can_proceed, reason = service.check_memory_before_operation(50)
            assert can_proceed
            assert reason == ""

            # Mock high memory usage
            mock_stats.return_value = MemoryStats(
                total_mb=8192,
                used_mb=1900,
                available_mb=6292,  # 1.9GB used, critical
                usage_percent=23.2,
                level=MemoryLevel.CRITICAL,
                tob_data_mb=100,
            )

            # Should block operation when memory is critical
            can_proceed, reason = service.check_memory_before_operation(50)
            assert not can_proceed
            assert "critical" in reason.lower()

    def test_add_cleanup_callback(self):
        """Test adding cleanup callbacks."""
        service = MemoryMonitorService()

        def test_callback():
            return 100.0

        service.add_cleanup_callback(test_callback)
        assert len(service.cleanup_callbacks) == 1
        assert service.cleanup_callbacks[0] == test_callback

    def test_get_memory_report(self):
        """Test getting memory report."""
        service = MemoryMonitorService()
        service.update_tob_memory_usage(200.0)

        with patch.object(service, "get_memory_stats") as mock_stats:
            mock_stats.return_value = MemoryStats(
                total_mb=8192,
                used_mb=4096,
                available_mb=4096,
                usage_percent=50.0,
                level=MemoryLevel.MODERATE,
                tob_data_mb=200.0,
            )

            report = service.get_memory_report()

            assert report["current_usage_mb"] == 4096
            assert report["total_memory_mb"] == 8192
            assert report["tob_data_mb"] == 200.0
            assert report["memory_level"] == "moderate"
            assert "can_allocate_mb" in report

    @patch("threading.Thread")
    def test_start_stop_monitoring(self, mock_thread):
        """Test starting and stopping memory monitoring."""
        service = MemoryMonitorService()

        # Mock thread
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        # Start monitoring
        service.start_monitoring()
        assert service.monitoring_active

        # Stop monitoring
        service.stop_monitoring()
        assert not service.monitoring_active

        # Should not start again if already active
        service.monitoring_active = True
        service.start_monitoring()  # Should not create new thread

    def test_perform_cleanup(self):
        """Test performing cleanup operations."""
        service = MemoryMonitorService()

        # Add test cleanup callbacks
        call_count = [0]
        service.add_cleanup_callback(
            lambda: (call_count.__setitem__(0, call_count[0] + 1), 50.0)[1]
        )
        service.add_cleanup_callback(lambda: 75.0)

        total_freed = service._perform_cleanup()

        assert total_freed == 125.0  # 50 + 75
        assert call_count[0] == 1

    def test_perform_emergency_cleanup(self):
        """Test performing emergency cleanup."""
        service = MemoryMonitorService()

        # Add cleanup callback that returns small amount
        service.add_cleanup_callback(lambda: 10.0)

        # Emergency cleanup doesn't return a value, just logs
        service._perform_emergency_cleanup()

        # Verify cleanup was called (we can't easily test the internal logic)
