"""Focused unit tests for MainController using stubbed signals."""

from contextlib import ExitStack
from typing import Any, Callable, Dict, List
from unittest.mock import Mock, patch

import pytest

from src.controllers.main_controller import MainController


class FakeSignal:
    def __init__(self) -> None:
        self.slots: List[Callable[..., None]] = []

    def connect(self, slot: Callable[..., None]) -> None:
        self.slots.append(slot)

    def emit(self, *args: Any, **kwargs: Any) -> None:
        for slot in list(self.slots):
            slot(*args, **kwargs)


class FakeFuture:
    def __init__(self, fn: Callable[[], Any]) -> None:
        self._exception: Exception | None = None
        self._result: Any = None

        try:
            self._result = fn()
        except Exception as exc:  # pragma: no cover - surfaced via result()
            self._exception = exc

    def result(self) -> Any:
        if self._exception is not None:
            raise self._exception
        return self._result

    def add_done_callback(self, callback: Callable[["FakeFuture"], None]):
        callback(self)
        return self


class PlotStub:
    def __init__(self) -> None:
        self.plot_updated = FakeSignal()
        self.sensors_updated = FakeSignal()
        self.axis_limits_changed = FakeSignal()
        self.current_tob_data: Any = None
        self.handle_sensor_calls: List[tuple[str, bool, Any]] = []

    def update_plot_data(self, data: Any) -> None:
        self.current_tob_data = data

    def update_selected_sensors(self, sensors: List[str], window: Any) -> None:
        return

    def update_sensor_checkboxes(self, window: Any) -> None:
        return

    def handle_sensor_selection_changed(
        self, sensor: str, selected: bool, window: Any
    ) -> None:
        self.handle_sensor_calls.append((sensor, selected, window))


class TOBStub:
    def __init__(self) -> None:
        self.file_loaded = FakeSignal()
        self.data_processed = FakeSignal()
        self.metrics_calculated = FakeSignal()
        self.error_occurred = FakeSignal()
        self.process_calls: List[Any] = []
        self.metric_calls: List[Any] = []
        self.load_calls: List[str] = []
        self.raise_on_load: Exception | None = None

    def load_tob_file(self, file_path: str) -> None:
        if self.raise_on_load is not None:
            raise self.raise_on_load
        self.load_calls.append(file_path)

    def process_tob_data(self, model: Any) -> None:
        self.process_calls.append(model)

    def calculate_metrics(self, model: Any) -> None:
        self.metric_calls.append(model)


class WindowStub:
    def __init__(self) -> None:
        self.file_opened = FakeSignal()
        self.project_created = FakeSignal()
        self.project_opened = FakeSignal()
        self.send_data_requested = FakeSignal()
        self.quality_control_requested = FakeSignal()
        self.status_request_requested = FakeSignal()

        self.update_plot_data = Mock()
        self.update_plot_sensors = Mock()
        self._handle_plot_axis_limits_update = Mock()
        self._show_plot_area = Mock()
        self.display_status_message = Mock()
        self.update_tob_file_status_bar = Mock()
        self.show_error_dialog = Mock()
        self.show_data_loaded = Mock()

        self.set_services = Mock()
        self.set_controller = Mock()
        self.get_metrics_widgets = Mock(return_value={})

        self.ui_state_manager = Mock(set_containers=Mock())
        self.welcome_container = object()
        self.plot_container = object()
        self.ntc_checkboxes: Dict[str, Any] = {}

        self.plot_widget = Mock()
        self.plot_widget.active_ntc_sensors = []
        self.plot_widget.set_active_ntc_sensors = Mock()
        self.plot_widget._refresh_plot = Mock()
        self.plot_widget._update_axis_labels = Mock()


@pytest.fixture
def controller_setup():
    window = WindowStub()
    memory_monitor = Mock(start_monitoring=Mock())

    with ExitStack() as stack:
        stack.enter_context(patch("src.services.ui_service.UIService", return_value=Mock()))
        stack.enter_context(
            patch(
                "src.services.ui_state_manager.UIStateManager",
                return_value=Mock(set_containers=Mock()),
            )
        )
        stack.enter_context(
            patch("src.services.axis_ui_service.AxisUIService", return_value=Mock())
        )
        stack.enter_context(
            patch("src.services.plot_style_service.PlotStyleService", return_value=Mock())
        )
        stack.enter_context(
            patch("src.services.analytics_service.AnalyticsService", return_value=Mock())
        )
        stack.enter_context(patch("src.services.tob_service.TOBService", return_value=Mock()))
        stack.enter_context(patch("src.services.data_service.DataService", return_value=Mock()))
        stack.enter_context(patch("src.services.plot_service.PlotService", return_value=Mock()))
        stack.enter_context(
            patch("src.services.encryption_service.EncryptionService", return_value=Mock())
        )
        stack.enter_context(
            patch("src.services.project_service.ProjectService", return_value=Mock())
        )
        stack.enter_context(patch("src.services.error_service.ErrorService", return_value=Mock()))
        stack.enter_context(patch("src.utils.error_handler.ErrorHandler", return_value=Mock()))
        stack.enter_context(
            patch(
                "src.services.memory_monitor_service.MemoryMonitorService",
                return_value=memory_monitor,
            )
        )
        with patch("src.controllers.main_controller.subprocess.run"), patch(
            "src.controllers.main_controller.ThreadPoolExecutor"
        ) as fake_executor:
            executor_mock = fake_executor.return_value
            executor_mock.submit.side_effect = lambda fn: FakeFuture(fn)
            controller = MainController(window)

    plot_stub = PlotStub()
    tob_stub = TOBStub()

    controller._executor_mock = executor_mock

    controller.plot_controller = plot_stub
    controller.tob_controller = tob_stub
    controller._connect_plot_signals()
    controller._connect_tob_signals()

    return controller, window, plot_stub, tob_stub


def test_initialisation(controller_setup):
    controller, _, _, _ = controller_setup
    assert controller.project_model.name == "Untitled Project"
    assert controller.tob_data_model is None


def test_services_injected(controller_setup):
    _, window, _, _ = controller_setup
    window.set_services.assert_called_once()


def test_view_signal_connections(controller_setup):
    controller, window, _, _ = controller_setup
    assert controller._on_file_opened in window.file_opened.slots
    assert controller._on_project_created in window.project_created.slots
    assert controller._on_project_opened in window.project_opened.slots


def test_plot_signals_connected(controller_setup):
    controller, _, plot_stub, _ = controller_setup
    assert controller._on_plot_updated in plot_stub.plot_updated.slots
    assert controller._on_sensors_updated in plot_stub.sensors_updated.slots
    assert controller._on_axis_limits_changed in plot_stub.axis_limits_changed.slots


def test_tob_signals_connected(controller_setup):
    controller, _, _, tob_stub = controller_setup
    assert controller._on_tob_file_loaded in tob_stub.file_loaded.slots
    assert controller._on_tob_data_processed in tob_stub.data_processed.slots
    assert controller._on_tob_metrics_calculated in tob_stub.metrics_calculated.slots
    assert controller._on_tob_error_occurred in tob_stub.error_occurred.slots


def test_on_tob_file_loaded(controller_setup):
    controller, _, _, tob_stub = controller_setup
    model = Mock()

    controller._on_tob_file_loaded(model)

    assert controller.tob_data_model is model
    assert tob_stub.process_calls == [model]


def test_on_tob_data_processed(controller_setup):
    controller, _, _, tob_stub = controller_setup
    received: List[Any] = []
    controller.data_processed.connect(lambda payload: received.append(payload))
    controller.tob_data_model = Mock()

    payload = {"foo": "bar"}
    controller._on_tob_data_processed(payload)

    assert received == [payload]
    assert tob_stub.metric_calls == [controller.tob_data_model]


def test_on_plot_updated_updates_view(controller_setup):
    controller, window, plot_stub, _ = controller_setup
    window.update_plot_data.reset_mock()
    plot_stub.current_tob_data = Mock()

    controller._on_plot_updated()

    window.update_plot_data.assert_called_once_with(plot_stub.current_tob_data)


def test_on_sensors_updated_updates_view(controller_setup):
    controller, window, _, _ = controller_setup
    window.update_plot_sensors.reset_mock()
    sensors = ["NTC01", "PT100"]

    controller._on_sensors_updated(sensors)

    window.update_plot_sensors.assert_called_once_with(sensors)


def test_on_axis_limits_changed_updates_view(controller_setup):
    controller, window, _, _ = controller_setup
    window._handle_plot_axis_limits_update.reset_mock()

    controller._on_axis_limits_changed("x", 0.0, 100.0)

    window._handle_plot_axis_limits_update.assert_called_once_with("x", 0.0, 100.0)


def test_handle_sensor_selection_changed_ntc_updates_widget(controller_setup):
    controller, window, _, _ = controller_setup
    window.ntc_checkboxes = {"NTC01": object(), "Temp": object()}
    window.plot_widget.active_ntc_sensors = None
    window.plot_widget.set_active_ntc_sensors.reset_mock()

    controller.handle_sensor_selection_changed("NTC01", True)

    window.plot_widget.set_active_ntc_sensors.assert_called_once()
    args, _ = window.plot_widget.set_active_ntc_sensors.call_args
    assert "NTC01" in args[0]


def test_handle_sensor_selection_changed_non_ntc_delegates(controller_setup):
    controller, _, plot_stub, _ = controller_setup

    controller.handle_sensor_selection_changed("RPM", True)

    assert plot_stub.handle_sensor_calls == [("RPM", True, controller.main_window)]


def test_plot_controller_axis_signal_flow_updates_view(controller_setup):
    controller, window, plot_stub, _ = controller_setup
    window._handle_plot_axis_limits_update.reset_mock()

    plot_stub.axis_limits_changed.emit("x", 0.0, 100.0)

    window._handle_plot_axis_limits_update.assert_called_once_with("x", 0.0, 100.0)


def test_on_tob_metrics_calculated_updates_services_and_view(controller_setup):
    controller, window, plot_stub, _ = controller_setup
    controller.data_service.update_data_metrics = Mock()
    window.update_tob_file_status_bar.reset_mock()
    window._show_plot_area.reset_mock()
    window.show_data_loaded.reset_mock()

    tob_model = Mock()
    tob_model.sensors = ["NTC01", "PT100"]
    tob_model.file_name = "demo.tob"
    tob_model.data_points = 42
    tob_model.get_pt100_sensor = Mock(return_value="PT100")
    controller.tob_data_model = tob_model

    metrics = {"mean_hp_power": 10.5}
    controller._on_tob_metrics_calculated(metrics)

    controller.data_service.update_data_metrics.assert_called_once()
    assert plot_stub.current_tob_data is tob_model
    window.update_tob_file_status_bar.assert_called_once()
    window._show_plot_area.assert_called_once()
    window.show_data_loaded.assert_called_once()


def test_on_tob_error_occurred_shows_dialog(controller_setup):
    controller, window, _, _ = controller_setup
    window.show_error_dialog.reset_mock()

    controller._on_tob_error_occurred("Error", "Something went wrong")

    window.show_error_dialog.assert_called_once_with("Error", "Something went wrong")


def test_on_file_opened_success_invokes_loader(controller_setup):
    controller, _, _, tob_stub = controller_setup

    controller._on_file_opened("sample.tob")

    assert tob_stub.load_calls == ["sample.tob"]


def test_on_file_opened_handles_error(controller_setup):
    controller, _, _, tob_stub = controller_setup
    tob_stub.raise_on_load = RuntimeError("boom")

    try:
        controller._on_file_opened("broken.tob")
    except RuntimeError:  # pragma: no cover
        pytest.fail("_on_file_opened should handle loader exceptions internally")
