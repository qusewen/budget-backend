from pydantic import BaseModel


class RoleTypeResponse(BaseModel):
    id: int
    role: str
    description: str
    name: str

    class Config:
        from_attributes = True