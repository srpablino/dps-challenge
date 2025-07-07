from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class ResultDetailsOut(BaseModel):
    total_words: Optional[int] = 0
    total_lines: Optional[int] = 0
    total_chars: Optional[int] = 0
    most_frequent_words: Optional[dict] = {}
    files_processed: Optional[List[str]] = []
    files_summary: Optional[List[str]] = []


class ProgressOut(BaseModel):
    total_files: Optional[int] = 0
    processed_files: Optional[int] = 0
    percentage: Optional[float] = 0.0


class ResultOut(BaseModel):
    process_id: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[ProgressOut] = ProgressOut()
    started_at: Optional[datetime] = None
    results: Optional[ResultDetailsOut] = ResultDetailsOut()
    estimated_completion: Optional[datetime] = None


class Result(BaseModel):
    id: Optional[str] = None
    process_id: Optional[str] = None
    file_name: Optional[str] = None
    total_words: Optional[int] = None
    total_lines: Optional[int] = None
    total_chars: Optional[int] = None
    most_frequent_words: Optional[int] = None
    summary: Optional[str] = None


class Process(BaseModel):
    id: str
    status: str
    created_at: Optional[datetime] = None
    number_of_files: Optional[int] = 0
    completed_at: Optional[datetime] = None


class EnumStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"
