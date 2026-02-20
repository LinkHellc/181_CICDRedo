"""Test serialization of build history models."""

import json
from datetime import datetime, timedelta

from src.core.build_history_models import BuildRecord, StageExecutionRecord, BuildState, StageStatus


def test_stage_execution_record_serialization():
    """测试 StageExecutionRecord 序列化"""
    stage = StageExecutionRecord(
        stage_id='test-stage-id',
        build_id='test-build-id',
        stage_name='test_stage',
        status=StageStatus.COMPLETED,
        start_time=datetime.now() - timedelta(seconds=5),
        end_time=datetime.now(),
        duration=5.0
    )

    # 转换为字典
    data = stage.to_dict()

    # 尝试序列化
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    print('StageExecutionRecord serialization success')
    print('Stage data:', data)


def test_build_record_serialization():
    """测试 BuildRecord 序列化"""
    stage = StageExecutionRecord(
        stage_id='test-stage-id',
        build_id='test-build-id',
        stage_name='test_stage',
        status=StageStatus.COMPLETED,
        start_time=datetime.now() - timedelta(seconds=5),
        end_time=datetime.now(),
        duration=5.0
    )

    record = BuildRecord(
        build_id='test-build-id',
        project_name='test_project',
        workflow_name='test_workflow',
        workflow_id='test-id',
        start_time=datetime.now(),
        state=BuildState.COMPLETED,
        stage_results=[stage]
    )

    # 转换为字典
    data = record.to_dict()

    # 尝试序列化
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    print('BuildRecord serialization success')
    print('Stage results:', data['stage_results'])


if __name__ == '__main__':
    test_stage_execution_record_serialization()
    test_build_record_serialization()
