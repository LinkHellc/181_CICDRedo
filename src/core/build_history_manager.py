"""Build history manager for Story 3.4

This module implements the BuildHistoryManager class which is responsible for:
- Saving build history to JSON file
- Loading build history from JSON file
- Querying and filtering build records
- Maintaining maximum 100 records limit
"""

import json
import logging
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.build_history_models import (
    BuildRecord,
    BuildFilters,
    BuildStatistics,
    BuildState
)

logger = logging.getLogger(__name__)


class BuildHistoryManager:
    """构建历史管理器 (Story 3.4)

    负责构建历史的持久化存储、查询和管理。

    数据存储位置:
        - Windows: %APPDATA%/MBD_CICDKits/build_history.json
        - 最多保存 100 条记录
    """

    def __init__(self, max_records: int = 100):
        """初始化构建历史管理器

        Args:
            max_records: 最大保存记录数（默认 100）
        """
        self._max_records = max_records
        self._records: List[BuildRecord] = []
        self._history_file: Optional[Path] = None

        # 初始化时加载历史记录
        self._initialize_storage()

    def _initialize_storage(self):
        """初始化存储路径并加载历史记录"""
        try:
            # 获取应用数据目录
            import os
            appdata_dir = Path(os.getenv('APPDATA', Path.home() / '.local'))
            self._history_dir = appdata_dir / 'MBD_CICDKits'

            # 确保目录存在
            self._history_dir.mkdir(parents=True, exist_ok=True)

            # 设置历史文件路径
            self._history_file = self._history_dir / 'build_history.json'

            logger.info(f"构建历史存储路径: {self._history_file}")

            # 加载历史记录
            self.load_history()

        except Exception as e:
            logger.error(f"初始化存储失败: {e}")
            self._history_file = None
            self._records = []

    def create_build_record(
        self,
        project_name: str,
        workflow_name: str,
        workflow_id: str,
        config_snapshot: Dict[str, Any]
    ) -> BuildRecord:
        """创建新的构建记录 (Story 3.4 Task 1)

        Args:
            project_name: 项目名称
            workflow_name: 工作流名称
            workflow_id: 工作流 ID
            config_snapshot: 构建配置快照

        Returns:
            BuildRecord: 新创建的构建记录
        """
        build_id = str(uuid.uuid4())

        record = BuildRecord(
            build_id=build_id,
            project_name=project_name,
            workflow_name=workflow_name,
            workflow_id=workflow_id,
            start_time=datetime.now(),
            state=BuildState.RUNNING,
            progress_percent=0,
            config_snapshot=config_snapshot
        )

        # 添加到内存中的记录列表
        self._records.insert(0, record)  # 新记录在前面

        logger.info(f"创建构建记录: build_id={build_id}, project={project_name}")

        return record

    def update_build_record(
        self,
        build_id: str,
        end_time: Optional[datetime] = None,
        state: Optional[BuildState] = None,
        duration: Optional[float] = None,
        progress_percent: Optional[int] = None,
        current_stage: Optional[str] = None,
        error_message: Optional[str] = None,
        stage_results: Optional[List] = None,
        output_files: Optional[List[str]] = None
    ) -> bool:
        """更新构建记录 (Story 3.4 Task 2)

        Args:
            build_id: 构建 ID
            end_time: 结束时间
            state: 构建状态
            duration: 总耗时
            progress_percent: 进度百分比
            current_stage: 当前阶段
            error_message: 错误消息
            stage_results: 阶段执行结果
            output_files: 输出文件列表

        Returns:
            bool: 是否更新成功
        """
        record = self.get_record_by_id(build_id)
        if not record:
            logger.warning(f"未找到构建记录: {build_id}")
            return False

        try:
            if end_time is not None:
                record.end_time = end_time
            if state is not None:
                record.state = state
            if duration is not None:
                record.duration = duration
            if progress_percent is not None:
                record.progress_percent = progress_percent
            if current_stage is not None:
                record.current_stage = current_stage
            if error_message is not None:
                record.error_message = error_message
            if stage_results is not None:
                record.stage_results = stage_results
            if output_files is not None:
                record.output_files = output_files

            record.updated_at = datetime.now()

            logger.debug(f"更新构建记录: {build_id}")
            return True

        except Exception as e:
            logger.error(f"更新构建记录失败: {e}")
            return False

    def save_build_record(self, build_id: str) -> bool:
        """保存构建记录到文件 (Story 3.4 Task 3)

        将构建记录保存到 JSON 文件，如果超过最大记录数，删除最旧的记录。

        Args:
            build_id: 构建 ID

        Returns:
            bool: 是否保存成功
        """
        record = self.get_record_by_id(build_id)
        if not record:
            logger.warning(f"未找到构建记录: {build_id}")
            return False

        try:
            # 限制记录数量
            if len(self._records) > self._max_records:
                removed = self._records[self._max_records:]
                self._records = self._records[:self._max_records]
                logger.info(f"删除过期的 {len(removed)} 条历史记录")

            # 保存到文件
            if self._history_file:
                data = [record.to_dict() for record in self._records]
                with open(self._history_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                logger.info(f"保存构建历史记录: {len(self._records)} 条记录")

            return True

        except Exception as e:
            logger.error(f"保存构建历史记录失败: {e}")
            return False

    def save_history(self) -> bool:
        """保存所有历史记录到文件 (Story 3.4 Task 4)

        Returns:
            bool: 是否保存成功
        """
        try:
            # 限制记录数量
            if len(self._records) > self._max_records:
                removed = self._records[self._max_records:]
                self._records = self._records[:self._max_records]
                logger.info(f"删除过期的 {len(removed)} 条历史记录")

            # 保存到文件
            if self._history_file:
                data = [record.to_dict() for record in self._records]
                with open(self._history_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                logger.info(f"保存构建历史记录: {len(self._records)} 条记录")
                return True

            return False

        except Exception as e:
            logger.error(f"保存构建历史记录失败: {e}")
            return False

    def load_history(self) -> int:
        """加载历史记录 (Story 3.4 Task 5)

        Returns:
            int: 加载的记录数
        """
        if not self._history_file or not self._history_file.exists():
            logger.info("构建历史文件不存在，从空开始")
            self._records = []
            return 0

        try:
            with open(self._history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._records = [BuildRecord.from_dict(item) for item in data]
            logger.info(f"加载构建历史记录: {len(self._records)} 条记录")
            return len(self._records)

        except Exception as e:
            logger.error(f"加载构建历史记录失败: {e}")
            self._records = []
            return 0

    def get_record_by_id(self, build_id: str) -> Optional[BuildRecord]:
        """根据 ID 获取构建记录 (Story 3.4 Task 6)

        Args:
            build_id: 构建 ID

        Returns:
            BuildRecord: 构建记录，如果未找到则返回 None
        """
        for record in self._records:
            if record.build_id == build_id:
                return record
        return None

    def query_records(self, filters: Optional[BuildFilters] = None) -> List[BuildRecord]:
        """查询构建记录 (Story 3.4 Task 7)

        Args:
            filters: 查询过滤器

        Returns:
            List[BuildRecord]: 符合条件的构建记录列表
        """
        if not filters:
            return self._records.copy()

        results = []

        for record in self._records:
            # 项目名称过滤
            if filters.project_name and record.project_name != filters.project_name:
                continue

            # 工作流名称过滤
            if filters.workflow_name and record.workflow_name != filters.workflow_name:
                continue

            # 状态过滤
            if filters.state and record.state != filters.state:
                continue

            # 时间范围过滤
            if filters.start_time and record.start_time < filters.start_time:
                continue
            if filters.end_time and record.start_time > filters.end_time:
                continue

            # 关键字搜索
            if filters.keyword:
                keyword_lower = filters.keyword.lower()
                text = (
                    f"{record.project_name} {record.workflow_name} "
                    f"{record.build_id} {record.error_message or ''}"
                ).lower()
                if keyword_lower not in text:
                    continue

            results.append(record)

        logger.info(f"查询构建记录: {len(results)} 条结果")
        return results

    def get_recent_records(self, limit: int = 10) -> List[BuildRecord]:
        """获取最近的构建记录 (Story 3.4 Task 8)

        Args:
            limit: 返回记录数限制

        Returns:
            List[BuildRecord]: 最近的构建记录列表
        """
        return self._records[:limit]

    def get_statistics(self, filters: Optional[BuildFilters] = None) -> BuildStatistics:
        """获取构建统计信息 (Story 3.4 Task 9)

        Args:
            filters: 查询过滤器（可选）

        Returns:
            BuildStatistics: 统计信息
        """
        records = self.query_records(filters)

        if not records:
            return BuildStatistics()

        stats = BuildStatistics(total_builds=len(records))

        # 统计各状态构建数
        for record in records:
            if record.state == BuildState.COMPLETED:
                stats.successful_builds += 1
            elif record.state == BuildState.FAILED:
                stats.failed_builds += 1
            elif record.state == BuildState.CANCELLED:
                stats.cancelled_builds += 1

            # 统计每个工作流的构建数
            workflow_name = record.workflow_name
            stats.builds_per_workflow[workflow_name] = (
                stats.builds_per_workflow.get(workflow_name, 0) + 1
            )

        # 计算成功率
        finished_builds = (
            stats.successful_builds + stats.failed_builds + stats.cancelled_builds
        )
        if finished_builds > 0:
            stats.success_rate = (stats.successful_builds / finished_builds) * 100

        # 计算耗时统计（仅统计已完成的构建）
        completed_records = [
            r for r in records
            if r.duration is not None and r.state == BuildState.COMPLETED
        ]

        if completed_records:
            durations = [r.duration for r in completed_records]
            stats.average_duration = sum(durations) / len(durations)
            stats.min_duration = min(durations)
            stats.max_duration = max(durations)

        return stats

    def delete_record(self, build_id: str) -> bool:
        """删除构建记录 (Story 3.4 Task 10)

        Args:
            build_id: 构建 ID

        Returns:
            bool: 是否删除成功
        """
        for i, record in enumerate(self._records):
            if record.build_id == build_id:
                self._records.pop(i)
                self.save_history()
                logger.info(f"删除构建记录: {build_id}")
                return True

        logger.warning(f"未找到构建记录: {build_id}")
        return False

    def clear_all_records(self) -> int:
        """清空所有历史记录 (Story 3.4 Task 11)

        Returns:
            int: 删除的记录数
        """
        count = len(self._records)
        self._records = []
        self.save_history()
        logger.info(f"清空所有构建历史记录: {count} 条记录")
        return count

    def compare_records(self, build_id_1: str, build_id_2: str) -> Dict[str, Any]:
        """对比两个构建记录 (Story 3.4 Task 12)

        Args:
            build_id_1: 第一个构建 ID
            build_id_2: 第二个构建 ID

        Returns:
            Dict[str, Any]: 对比结果
        """
        record_1 = self.get_record_by_id(build_id_1)
        record_2 = self.get_record_by_id(build_id_2)

        if not record_1 or not record_2:
            raise ValueError("未找到构建记录")

        comparison = {
            'build_1': {
                'build_id': record_1.build_id,
                'project_name': record_1.project_name,
                'workflow_name': record_1.workflow_name,
                'start_time': record_1.start_time.isoformat(),
                'state': record_1.state.value,
                'duration': record_1.duration
            },
            'build_2': {
                'build_id': record_2.build_id,
                'project_name': record_2.project_name,
                'workflow_name': record_2.workflow_name,
                'start_time': record_2.start_time.isoformat(),
                'state': record_2.state.value,
                'duration': record_2.duration
            },
            'performance_diff': {},
            'stage_diff': {},
            'config_diff': {}
        }

        # 性能对比
        if record_1.duration is not None and record_2.duration is not None:
            diff = record_2.duration - record_1.duration
            comparison['performance_diff']['duration_diff'] = diff
            comparison['performance_diff']['duration_diff_percent'] = (
                (diff / record_1.duration * 100) if record_1.duration > 0 else 0
            )

        # 阶段对比
        stage_map_1 = {stage.stage_name: stage for stage in record_1.stage_results}
        stage_map_2 = {stage.stage_name: stage for stage in record_2.stage_results}

        all_stage_names = set(stage_map_1.keys()) | set(stage_map_2.keys())

        for stage_name in all_stage_names:
            stage_1 = stage_map_1.get(stage_name)
            stage_2 = stage_map_2.get(stage_name)

            stage_diff = {
                'stage_name': stage_name,
                'status_1': stage_1.status.value if stage_1 else None,
                'status_2': stage_2.status.value if stage_2 else None,
                'duration_1': stage_1.duration if stage_1 else None,
                'duration_2': stage_2.duration if stage_2 else None,
                'duration_diff': None
            }

            if stage_1 and stage_2 and stage_1.duration and stage_2.duration:
                stage_diff['duration_diff'] = stage_2.duration - stage_1.duration

            comparison['stage_diff'][stage_name] = stage_diff

        # 配置差异（简化版本，仅对比关键字段）
        config_diff = []
        key_fields = ['project_name', 'workflow_name']

        for field in key_fields:
            val_1 = getattr(record_1, field, None)
            val_2 = getattr(record_2, field, None)

            if val_1 != val_2:
                config_diff.append({
                    'field': field,
                    'value_1': val_1,
                    'value_2': val_2
                })

        comparison['config_diff'] = config_diff

        logger.info(f"对比构建记录: {build_id_1} vs {build_id_2}")
        return comparison

    def get_all_records(self) -> List[BuildRecord]:
        """获取所有构建记录

        Returns:
            List[BuildRecord]: 所有构建记录列表
        """
        return self._records.copy()

    def export_records(self, output_path: Path, filters: Optional[BuildFilters] = None) -> bool:
        """导出构建记录到文件 (Story 3.4 Task 13)

        Args:
            output_path: 输出文件路径
            filters: 查询过滤器（可选）

        Returns:
            bool: 是否导出成功
        """
        try:
            records = self.query_records(filters)
            data = [record.to_dict() for record in records]

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"导出构建记录到: {output_path}")
            return True

        except Exception as e:
            logger.error(f"导出构建记录失败: {e}")
            return False


# 全局单例实例
_history_manager_instance: Optional[BuildHistoryManager] = None


def get_history_manager() -> BuildHistoryManager:
    """获取构建历史管理器单例实例 (Story 3.4 Task 14)

    Returns:
        BuildHistoryManager: 构建历史管理器实例
    """
    global _history_manager_instance
    if _history_manager_instance is None:
        _history_manager_instance = BuildHistoryManager()
    return _history_manager_instance


def reset_history_manager():
    """重置构建历史管理器单例（主要用于测试）"""
    global _history_manager_instance
    _history_manager_instance = None
