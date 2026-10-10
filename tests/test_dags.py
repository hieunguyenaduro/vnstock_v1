"""Test lịch chạy DAGs — không cần scheduler, chỉ đọc timetable object."""

from dags import round1_dag, round2_dag


def test_round1_runs_daily_at_4pm_vietnam():
    timetable = round1_dag.dag.timetable
    assert timetable.summary == "0 16 * * *"
    assert str(timetable._timezone) == "Asia/Ho_Chi_Minh"
    assert round1_dag.dag.catchup is False


def test_round1_tasks_run_sequentially():
    order = ["HH_HL", "LL_LH", "WAVE_UP", "WAVE_DOWN", "RSI_OVERSOLD", "SMA"]
    dag = round1_dag.dag
    assert [t.task_id for t in dag.topological_sort()] == order
    for prev, cur in zip(order, order[1:]):
        assert dag.get_task(cur).upstream_task_ids == {prev}


def test_round1_has_no_trigger_task():
    # round2 chạy hourly độc lập nên round1 không trigger kèm nữa
    task_ids = [t.task_id for t in round1_dag.dag.tasks]
    assert "TRIGGER_DAG_FILTER_STRATEGIES" not in task_ids
    assert len(task_ids) == 6


def test_round2_runs_hourly():
    timetable = round2_dag.dag.timetable
    assert timetable.summary == "0 * * * *"
    assert round2_dag.dag.catchup is False


def test_round2_tasks_unchanged():
    task_ids = [t.task_id for t in round2_dag.dag.tasks]
    assert task_ids == ["BINANCE_RSI_1H", "US_STOCK_RSI_1H"]


def test_round2_tasks_run_parallel():
    for task in round2_dag.dag.tasks:
        assert task.upstream_task_ids == set()
        assert task.downstream_task_ids == set()
