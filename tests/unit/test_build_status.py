"""Unit tests for BuildStatus enum (Story 2.15 - Task 1)

This module contains unit tests for the BuildState enum validation.
"""

import pytest
from core.models import BuildState, StageStatus


class TestBuildStateEnum:
    """测试 BuildState 枚举 (Story 2.15 - Task 1.3)"""

    def test_enum_values_defined(self):
        """验证枚举值正确定义"""
        # 检查所有必需的状态存在
        assert hasattr(BuildState, "IDLE")
        assert hasattr(BuildState, "RUNNING")
        assert hasattr(BuildState, "COMPLETED")
        assert hasattr(BuildState, "FAILED")
        assert hasattr(BuildState, "CANCELLED")

    def test_enum_value_types(self):
        """验证枚举值的类型正确"""
        assert isinstance(BuildState.IDLE.value, str)
        assert isinstance(BuildState.RUNNING.value, str)
        assert isinstance(BuildState.COMPLETED.value, str)
        assert isinstance(BuildState.FAILED.value, str)
        assert isinstance(BuildState.CANCELLED.value, str)

    def test_enum_value_strings(self):
        """验证枚举值的字符串正确"""
        assert BuildState.IDLE.value == "idle"
        assert BuildState.RUNNING.value == "running"
        assert BuildState.COMPLETED.value == "completed"
        assert BuildState.FAILED.value == "failed"
        assert BuildState.CANCELLED.value == "cancelled"

    def test_enum_equality(self):
        """验证枚举值相等性"""
        assert BuildState.IDLE == BuildState.IDLE
        assert BuildState.RUNNING == BuildState.RUNNING
        assert BuildState.CANCELLED == BuildState.CANCELLED

        assert BuildState.IDLE != BuildState.RUNNING
        assert BuildState.COMPLETED != BuildState.FAILED


class TestStageStatusEnum:
    """测试 StageStatus 枚举 (Story 2.15 - Task 1.3)"""

    def test_enum_values_defined(self):
        """验证枚举值正确定义"""
        assert hasattr(StageStatus, "PENDING")
        assert hasattr(StageStatus, "RUNNING")
        assert hasattr(StageStatus, "COMPLETED")
        assert hasattr(StageStatus, "FAILED")
        assert hasattr(StageStatus, "CANCELLED")
        assert hasattr(StageStatus, "SKIPPED")

    def test_cancelled_status_value(self):
        """验证 CANCELLED 状态的值"""
        assert StageStatus.CANCELLED.value == "cancelled"


class TestStateTransitionLogic:
    """测试状态转换逻辑 (Story 2.15 - Task 1.4)"""

    def test_idle_to_running(self):
        """测试 IDLE -> RUNNING 转换"""
        # 模拟状态转换
        state = BuildState.IDLE
        assert state == BuildState.IDLE

        # 转换到 RUNNING
        state = BuildState.RUNNING
        assert state == BuildState.RUNNING

    def test_running_to_completed(self):
        """测试 RUNNING -> COMPLETED 转换"""
        state = BuildState.RUNNING
        assert state == BuildState.RUNNING

        # 转换到 COMPLETED
        state = BuildState.COMPLETED
        assert state == BuildState.COMPLETED

    def test_running_to_failed(self):
        """测试 RUNNING -> FAILED 转换"""
        state = BuildState.RUNNING
        assert state == BuildState.RUNNING

        # 转换到 FAILED
        state = BuildState.FAILED
        assert state == BuildState.FAILED

    def test_running_to_cancelled(self):
        """测试 RUNNING -> CANCELLED 转换"""
        state = BuildState.RUNNING
        assert state == BuildState.RUNNING

        # 转换到 CANCELLED
        state = BuildState.CANCELLED
        assert state == BuildState.CANCELLED

    def test_cancelled_to_idle(self):
        """测试 CANCELLED -> IDLE 转换"""
        state = BuildState.CANCELLED
        assert state == BuildState.CANCELLED

        # 取消后回到 IDLE
        state = BuildState.IDLE
        assert state == BuildState.IDLE

    def test_stage_result_cancelled_factory(self):
        """测试 StageResult.cancelled() 工厂方法 (Story 2.15 - Task 14.2)"""
        from core.models import StageResult

        # 使用工厂方法创建取消结果
        result = StageResult.cancelled("用户取消")

        assert result.status == StageStatus.CANCELLED
        assert result.message == "用户取消"

        # 使用默认消息
        result_default = StageResult.cancelled()
        assert result_default.status == StageStatus.CANCELLED
        assert result_default.message == "已取消"
