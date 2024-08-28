from typing_extensions import Annotated

from pydantic import BaseModel, Field


class CronExpression(BaseModel):
    expression: Annotated[str, Field(..., examples=["*/15 14 1,15 * 2-5", "@weekly", "0 0 4 * SUN", "30 14 1,5 * mon"])]