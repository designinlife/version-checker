from enum import StrEnum

from pydantic import BaseModel


class InspectStatus(StrEnum):
    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"


class InspectItemResult(BaseModel):
    name: str
    status: InspectStatus
    error_type: str | None = None
    message: str | None = None

    @classmethod
    def success(cls, name: str):
        return cls(name=name, status=InspectStatus.SUCCESS)

    @classmethod
    def skipped(cls, name: str, message: str):
        return cls(name=name, status=InspectStatus.SKIPPED, message=message)

    @classmethod
    def failed(cls, name: str, error_type: str, message: str):
        return cls(name=name, status=InspectStatus.FAILED, error_type=error_type, message=message)


class InspectResult(BaseModel):
    items: list[InspectItemResult]

    @property
    def success(self):
        return [item for item in self.items if item.status == InspectStatus.SUCCESS]

    @property
    def skipped(self):
        return [item for item in self.items if item.status == InspectStatus.SKIPPED]

    @property
    def failed(self):
        return [item for item in self.items if item.status == InspectStatus.FAILED]

    @property
    def has_failed(self):
        return bool(self.failed)
