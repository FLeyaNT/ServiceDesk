from pydantic import BaseModel


class IssueTypeResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
