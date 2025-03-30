from .repository import CourseRepository






class CoursesService:
    def __init__(self, repository: CourseRepository):
        self.repository = repository