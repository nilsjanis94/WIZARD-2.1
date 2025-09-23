"""
Memory Monitor Service for WIZARD-2.1

Service for monitoring and managing memory usage to prevent memory exhaustion.
Provides automatic cleanup and warnings when memory limits are approached.
"""

import logging
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import psutil

from ..utils.error_handler import ErrorHandler


class MemoryLevel(Enum):
    """Memory usage levels."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    EXCEEDED = "exceeded"


@dataclass
class MemoryStats:
    """Memory statistics."""

    total_mb: float
    used_mb: float
    available_mb: float
    usage_percent: float
    level: MemoryLevel
    tob_data_mb: float = 0.0  # Memory used by TOB data


class MemoryMonitorService:
    """
    Service for monitoring and managing memory usage.

    Provides real-time memory monitoring, automatic cleanup, and user warnings
    to prevent memory exhaustion during TOB file operations.
    """

    # Memory limits in MB for TOB data
    WARNING_THRESHOLD_MB = 2048  # 2.0GB - start warning user
    CRITICAL_THRESHOLD_MB = 3072  # 3.0GB - force cleanup
    MAX_MEMORY_MB = 4096  # 4.0GB - absolute maximum for TOB data

    # Monitoring intervals in seconds
    MONITORING_INTERVAL = 30.0  # Check every 30 seconds (TOB data changes infrequently)
    FAST_MONITORING_INTERVAL = 10.0  # Check every 10 seconds when critical

    def __init__(self, error_handler: Optional[ErrorHandler] = None):
        """
        Initialize the memory monitor service.

        Args:
            error_handler: Error handler for user notifications
        """
        self.logger = logging.getLogger(__name__)
        self.error_handler = error_handler

        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        # Memory tracking
        self.tob_memory_usage = 0.0  # Memory used by TOB data in MB
        self.memory_callbacks: List[Callable[[MemoryStats], None]] = []

        # Cleanup callbacks (called when memory is critical)
        self.cleanup_callbacks: List[Callable[[], float]] = []  # Return freed MB

        # User notification flags (prevent spam)
        self.last_warning_time = 0
        self.warning_cooldown = 30  # Don't warn more than once per 30 seconds

        self.logger.info("MemoryMonitorService initialized")

    def start_monitoring(self) -> None:
        """Start background memory monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.stop_event.clear()

        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, name="MemoryMonitor", daemon=True
        )
        self.monitoring_thread.start()

        self.logger.info("Memory monitoring started")

    def stop_monitoring(self) -> None:
        """Stop background memory monitoring."""
        if not self.monitoring_active:
            return

        self.monitoring_active = False
        self.stop_event.set()

        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2.0)

        self.logger.info("Memory monitoring stopped")

    def get_memory_stats(self) -> MemoryStats:
        """
        Get current memory statistics.

        Returns:
            MemoryStats object with current memory information
        """
        try:
            # Get system memory info
            memory = psutil.virtual_memory()

            total_mb = memory.total / (1024 * 1024)
            used_mb = memory.used / (1024 * 1024)
            available_mb = memory.available / (1024 * 1024)
            usage_percent = memory.percent

            # Determine memory level
            level = self._calculate_memory_level(used_mb)

            return MemoryStats(
                total_mb=total_mb,
                used_mb=used_mb,
                available_mb=available_mb,
                usage_percent=usage_percent,
                level=level,
                tob_data_mb=self.tob_memory_usage,
            )

        except Exception as e:
            self.logger.error(f"Error getting memory stats: {e}")
            # Return safe defaults
            return MemoryStats(
                total_mb=0,
                used_mb=0,
                available_mb=0,
                usage_percent=0,
                level=MemoryLevel.LOW,
                tob_data_mb=self.tob_memory_usage,
            )

    def _calculate_memory_level(self, used_mb: float) -> MemoryLevel:
        """
        Calculate memory usage level based on thresholds.

        Args:
            used_mb: Memory used in MB

        Returns:
            MemoryLevel enum value
        """
        if used_mb >= self.MAX_MEMORY_MB:
            return MemoryLevel.EXCEEDED
        elif used_mb >= self.CRITICAL_THRESHOLD_MB:
            return MemoryLevel.CRITICAL
        elif used_mb >= self.WARNING_THRESHOLD_MB:
            return MemoryLevel.HIGH
        elif used_mb >= self.WARNING_THRESHOLD_MB * 0.7:  # 1.05GB
            return MemoryLevel.MODERATE
        else:
            return MemoryLevel.LOW

    def add_memory_callback(self, callback: Callable[[MemoryStats], None]) -> None:
        """
        Add a callback that gets called when memory stats change.

        Args:
            callback: Function that takes MemoryStats as parameter
        """
        self.memory_callbacks.append(callback)

    def add_cleanup_callback(self, callback: Callable[[], float]) -> None:
        """
        Add a cleanup callback that gets called when memory is critical.

        Args:
            callback: Function that performs cleanup and returns freed MB
        """
        self.cleanup_callbacks.append(callback)

    def update_tob_memory_usage(self, tob_memory_mb: float) -> None:
        """
        Update the memory usage tracking for TOB data.

        Args:
            tob_memory_mb: Memory used by TOB data in MB
        """
        self.tob_memory_usage = max(0, tob_memory_mb)
        self.logger.debug(f"TOB memory usage updated: {tob_memory_mb:.1f}MB")

    def check_memory_before_operation(self, estimated_mb: float) -> tuple[bool, str]:
        """
        Check if an operation can proceed based on memory requirements.

        Args:
            estimated_mb: Estimated memory required for the operation in MB

        Returns:
            Tuple of (can_proceed, reason)
        """
        stats = self.get_memory_stats()

        # Check if operation would exceed TOB data limits
        projected_tob_usage = self.tob_memory_usage + estimated_mb

        if projected_tob_usage >= self.MAX_MEMORY_MB:
            return (
                False,
                f"Operation would exceed TOB data memory limit ({projected_tob_usage:.1f}MB > {self.MAX_MEMORY_MB}MB)",
            )

        tob_memory_level = self._calculate_memory_level(self.tob_memory_usage)
        if tob_memory_level in [MemoryLevel.CRITICAL, MemoryLevel.EXCEEDED]:
            return (
                False,
                f"TOB data memory usage is critical ({self.tob_memory_usage:.1f}MB). Please remove some TOB files first.",
            )

        return True, ""

    def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        interval = self.MONITORING_INTERVAL

        while not self.stop_event.is_set():
            try:
                stats = self.get_memory_stats()

                # Call registered callbacks
                for callback in self.memory_callbacks:
                    try:
                        callback(stats)
                    except Exception as e:
                        self.logger.error(f"Error in memory callback: {e}")

                # Handle memory levels
                self._handle_memory_level(stats)

                # Adjust monitoring interval based on memory level
                if stats.level in [MemoryLevel.CRITICAL, MemoryLevel.EXCEEDED]:
                    interval = self.FAST_MONITORING_INTERVAL
                else:
                    interval = self.MONITORING_INTERVAL

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")

            # Wait for next check or stop event
            self.stop_event.wait(interval)

    def _handle_memory_level(self, stats: MemoryStats) -> None:
        """
        Handle memory level changes and take appropriate actions.

        Args:
            stats: Current memory statistics
        """
        current_time = time.time()

        # Check TOB data memory instead of system memory
        tob_memory_level = self._calculate_memory_level(self.tob_memory_usage)

        if tob_memory_level == MemoryLevel.EXCEEDED:
            self.logger.critical(
                f"TOB data memory limit exceeded: {self.tob_memory_usage:.1f}MB > {self.MAX_MEMORY_MB}MB"
            )
            self._perform_emergency_cleanup()

            if self.error_handler:
                self.error_handler.handle_error(
                    MemoryError(
                        f"TOB data memory limit exceeded ({self.tob_memory_usage:.1f}MB > {self.MAX_MEMORY_MB}MB)"
                    ),
                    "TOB Memory Limit Exceeded",
                    None,
                )

        elif tob_memory_level == MemoryLevel.CRITICAL:
            self.logger.warning(
                f"TOB data memory usage critical: {self.tob_memory_usage:.1f}MB"
            )
            freed_mb = self._perform_cleanup()

            if current_time - self.last_warning_time > self.warning_cooldown:
                self.last_warning_time = current_time
                if self.error_handler:
                    self.error_handler.handle_warning(
                        f"TOB data memory usage is critical ({self.tob_memory_usage:.1f}MB). "
                        "Consider removing some TOB files to free up memory.",
                        None,
                    )

        elif tob_memory_level == MemoryLevel.HIGH:
            self.logger.info(
                f"TOB data memory usage high: {self.tob_memory_usage:.1f}MB"
            )

            if current_time - self.last_warning_time > self.warning_cooldown:
                self.last_warning_time = current_time
                if self.error_handler:
                    self.error_handler.handle_warning(
                        f"TOB data memory usage is high ({self.tob_memory_usage:.1f}MB). "
                        "Consider removing unused TOB files.",
                        None,
                    )

    def _perform_cleanup(self) -> float:
        """
        Perform cleanup operations to free memory.

        Returns:
            Amount of memory freed in MB
        """
        total_freed = 0.0

        for cleanup_callback in self.cleanup_callbacks:
            try:
                freed_mb = cleanup_callback()
                total_freed += freed_mb
                self.logger.info(f"Cleanup callback freed {freed_mb:.1f}MB")
            except Exception as e:
                self.logger.error(f"Error in cleanup callback: {e}")

        self.logger.info(f"Total memory freed by cleanup: {total_freed:.1f}MB")
        return total_freed

    def _perform_emergency_cleanup(self) -> None:
        """
        Perform emergency cleanup when memory limit is exceeded.
        This is more aggressive and may remove user data.
        """
        self.logger.critical("Performing emergency memory cleanup")

        # Call all cleanup callbacks multiple times if needed
        total_freed = 0.0
        max_attempts = 3

        for attempt in range(max_attempts):
            freed = self._perform_cleanup()
            total_freed += freed

            if freed < 100:  # Less than 100MB freed, probably can't free more
                break

        self.logger.critical(f"Emergency cleanup freed {total_freed:.1f}MB")

        if total_freed < 500:  # Still couldn't free enough
            self.logger.critical(
                "Emergency cleanup insufficient. Application may become unstable."
            )

    def get_memory_report(self) -> Dict[str, Any]:
        """
        Get a detailed memory usage report.

        Returns:
            Dictionary with detailed memory information
        """
        stats = self.get_memory_stats()

        return {
            "current_usage_mb": stats.used_mb,
            "total_memory_mb": stats.total_mb,
            "available_mb": stats.available_mb,
            "usage_percent": stats.usage_percent,
            "memory_level": stats.level.value,
            "tob_data_mb": stats.tob_data_mb,
            "warning_threshold_mb": self.WARNING_THRESHOLD_MB,
            "critical_threshold_mb": self.CRITICAL_THRESHOLD_MB,
            "max_memory_mb": self.MAX_MEMORY_MB,
            "can_allocate_mb": max(0, self.MAX_MEMORY_MB - stats.used_mb),
        }
