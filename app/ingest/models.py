from __future__ import annotations
from pydantic import BaseModel
from typing import List, Literal, Dict

CourseType = Literal["required", "elective"]

class Course(BaseModel):
    code: str
    name: str
    semester: int
    ects: float
    type: CourseType
    module: str
    prerequisites: List[str] = []
    notes: str = ""
    source_ref: str

class PlanRules(BaseModel):
    total_ects: int = 120
    min_electives_ects: int = 24
    per_semester_constraints: Dict[str, Dict[str, int]] = {}

class Plan(BaseModel):
    program: Literal["AI", "AI Product"]
    version: str
    source_url: str
    courses: List[Course]
    rules: PlanRules = PlanRules()