from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EvidenceMetadata(BaseModel):
    artifact_path: str
    sha256: str
    verified: bool
    analysis_timestamp: str

class ProcessEntry(BaseModel):
    pid: int
    ppid: int
    image_name: str
    offset: str
    threads: int
    handles: int
    session_id: Optional[str]
    wow64: bool
    create_time: Optional[str]
    exit_time: Optional[str]

class ProcessListResult(BaseModel):
    evidence: EvidenceMetadata
    processes: list[ProcessEntry]
    total_count: int
    suspicious_count: int
    suspicious_pids: list[int]

class NetworkConnection(BaseModel):
    offset: str
    proto: str
    local_addr: str
    local_port: int
    foreign_addr: str
    foreign_port: int
    state: str
    pid: int
    owner: Optional[str]
    created: Optional[str]

class NetworkConnectionList(BaseModel):
    evidence: EvidenceMetadata
    connections: list[NetworkConnection]
    total_count: int
    suspicious_connections: list[NetworkConnection]

class RegistryRunKey(BaseModel):
    hive: str
    key_path: str
    value_name: str
    value_data: str
    last_written: Optional[str]
    suspicious: bool
    reason: Optional[str]

class RegistryRunKeyList(BaseModel):
    evidence: EvidenceMetadata
    run_keys: list[RegistryRunKey]
    total_count: int
    suspicious_count: int

class MFTEntry(BaseModel):
    inode: str
    filename: str
    file_path: str
    created: Optional[str]
    modified: Optional[str]
    accessed: Optional[str]
    size: int
    flags: str

class MFTTimeline(BaseModel):
    evidence: EvidenceMetadata
    entries: list[MFTEntry]
    total_count: int
    time_range_start: str
    time_range_end: str

class DLLEntry(BaseModel):
    pid: int
    base: str
    size: int
    name: str
    path: str
    suspicious: bool
    reason: Optional[str]

class DLLList(BaseModel):
    evidence: EvidenceMetadata
    pid: int
    dlls: list[DLLEntry]
    total_count: int
    suspicious_count: int

class MalfindEntry(BaseModel):
    pid: int
    process_name: str
    address: str
    vad_tag: str
    protection: str
    hexdump: str
    suspicious: bool
    reason: str

class MalfindResult(BaseModel):
    evidence: EvidenceMetadata
    entries: list[MalfindEntry]
    total_count: int
    suspicious_pids: list[int]

class EVTXEntry(BaseModel):
    event_id: int
    timestamp: Optional[str]
    source: str
    level: str
    description: str
    suspicious: bool
    reason: Optional[str]


class EmailArtifact(BaseModel):
    sender: str
    recipient: str
    subject: str
    reply_to: str
    attachments: list[str]
    timestamp: str

class BrowserArtifact(BaseModel):
    url: str
    timestamp: str
    artifact_type: str

class DocumentArtifact(BaseModel):
    file_name: str
    author: str
    created: str
    modified: str
    accessed: str
