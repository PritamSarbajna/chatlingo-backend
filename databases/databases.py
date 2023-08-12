from pydantic import BaseModel, Field

class TodoItem(BaseModel):
    title: str = Field(..., title="Title of the Todo item")
    description: str = Field(None, title="Description of the Todo item", max_length=100)
    completed: bool = Field(False, title="Status of completion")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sample Todo",
                "description": "This is a sample todo item.",
                "completed": False
            }
        }
