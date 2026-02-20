"""Build history data models for Story 3.3

This module defines data models for build history tracking, including
build records, stage execution records, and output file records.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import json


class BuildState(str, Enum):
    """Build state enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StageStatus(str, Enum):
    """Stage status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass
class OutputFileRecord:
    """Output file record

    Attributes:
        file_id: Unique identifier
        build_id: Associated build ID
        file_type: File type (hex, a2l, elf, etc.)
        file_path: File path (absolute)
        file_size: File size in bytes
        file_hash: File hash (MD5 or SHA256)
        created_at: File creation timestamp
    """
    file_id: str
    build_id: str
    file_type: str
    file_path: str
    file_size: int
    file_hash: str
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OutputFileRecord':
        """Create from dictionary"""
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class StageExecutionRecord:
    """Stage execution record

    Attributes:
        stage_id: Unique identifier
        build_id: Associated build ID
        stage_name: Stage name
        status: Stage status
        start_time: Stage start timestamp
        end_time: Stage end timestamp
        duration: Stage duration in seconds
        error_message: Error message if failed
        output_files: List of output file IDs
        logs: Stage logs (optional)
    """
    stage_id: str
    build_id: str
    stage_name: str
    status: StageStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    error_message: Optional[str] = None
    output_files: List[str] = field(default_factory=list)
    logs: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            'stage_id': self.stage_id,
            'build_id': self.build_id,
            'stage_name': self.stage_name,
            'status': self.status.value,
            'start_time': self.start_time.isoformat(),
            'duration': self.duration,
            'error_message': self.error_message,
            'output_files': self.output_files,
            'logs': self.logs
        }

        if self.end_time:
            data['end_time'] = self.end_time.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StageExecutionRecord':
        """Create from dictionary"""
        if isinstance(data.get('status'), str):
            data['status'] = StageStatus(data['status'])
        if isinstance(data.get('start_time'), str):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if isinstance(data.get('end_time'), str):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        return cls(**data)


@dataclass
class BuildRecord:
    """Build record

    Attributes:
        build_id: Unique identifier (UUID)
        project_name: Project name
        workflow_name: Workflow name
        workflow_id: Workflow ID
        start_time: Build start timestamp
        end_time: Build end timestamp (optional)
        duration: Build duration in seconds (optional)
        state: Build state
        progress_percent: Completion percentage (0-100)
        current_stage: Currently executing stage
        error_message: Error message if failed
        output_files: List of output file IDs
        stage_results: List of stage execution records
        config_snapshot: Build configuration snapshot
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    """
    build_id: str
    project_name: str
    workflow_name: str
    workflow_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    state: BuildState = BuildState.IDLE
    progress_percent: int = 0
    current_stage: Optional[str] = None
    error_message: Optional[str] = None
    output_files: List[str] = field(default_factory=list)
    stage_results: List[StageExecutionRecord] = field(default_factory=list)
    config_snapshot: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        # Convert stage_results to dictionaries
        stage_results_dicts = []
        for stage in self.stage_results:
            if isinstance(stage, StageExecutionRecord):
                stage_results_dicts.append(stage.to_dict())
            elif isinstance(stage, dict):
                # Already a dictionary, use as is
                stage_results_dicts.append(stage)
            else:
                # Unknown type, convert to string representation
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Unexpected stage type: {type(stage)}")
                stage_results_dicts.append(str(stage))

        # Build dictionary manually to avoid asdict() issues with enums
        data = {
            'build_id': self.build_id,
            'project_name': self.project_name,
            'workflow_name': self.workflow_name,
            'workflow_id': self.workflow_id,
            'state': self.state.value,
            'start_time': self.start_time.isoformat(),
            'duration': self.duration,
            'progress_percent': self.progress_percent,
            'current_stage': self.current_stage,
            'error_message': self.error_message,
            'output_files': self.output_files,
            'stage_results': stage_results_dicts,
            'config_snapshot': self.config_snapshot,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if self.end_time:
            data['end_time'] = self.end_time.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BuildRecord':
        """Create from dictionary"""
        if isinstance(data.get('state'), str):
            data['state'] = BuildState(data['state'])
        if isinstance(data.get('start_time'), str):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if isinstance(data.get('end_time'), str):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])

        # Convert stage results
        if 'stage_results' in data:
            data['stage_results'] = [
                StageExecutionRecord.from_dict(stage)
                if isinstance(stage, dict) else stage
                for stage in data['stage_results']
            ]

        return cls(**data)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> 'BuildRecord':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class BuildFilters:
    """Build query filters

    Attributes:
        project_name: Filter by project name (optional)
        workflow_name: Filter by workflow name (optional)
        state: Filter by build state (optional)
        start_time: Filter by start time range (optional)
        end_time: Filter by end time range (optional)
        keyword: Search keyword (optional)
    """
    project_name: Optional[str] = None
    workflow_name: Optional[str] = None
    state: Optional[BuildState] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    keyword: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {}
        if self.project_name:
            data['project_name'] = self.project_name
        if self.workflow_name:
            data['workflow_name'] = self.workflow_name
        if self.state:
            data['state'] = self.state.value
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        if self.keyword:
            data['keyword'] = self.keyword
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BuildFilters':
        """Create from dictionary"""
        if isinstance(data.get('state'), str):
            data['state'] = BuildState(data['state'])
        if isinstance(data.get('start_time'), str):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if isinstance(data.get('end_time'), str):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        return cls(**data)


@dataclass
class BuildStatistics:
    """Build statistics

    Attributes:
        total_builds: Total number of builds
        successful_builds: Number of successful builds
        failed_builds: Number of failed builds
        cancelled_builds: Number of cancelled builds
        success_rate: Success rate (percentage)
        average_duration: Average build duration in seconds
        min_duration: Minimum build duration in seconds
        max_duration: Maximum build duration in seconds
        builds_per_state: Number of builds per state
        builds_per_workflow: Number of builds per workflow
    """
    total_builds: int = 0
    successful_builds: int = 0
    failed_builds: int = 0
    cancelled_builds: int = 0
    success_rate: float = 0.0
    average_duration: Optional[float] = None
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None
    builds_per_state: Dict[str, int] = field(default_factory=dict)
    builds_per_workflow: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
