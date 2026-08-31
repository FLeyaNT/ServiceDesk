from repositories.postgres import IssueTypesRepo
from schemas.issue_types import IssueTypeResponse


class IssueTypesService:
    issue_types_repo: IssueTypesRepo

    def __init__(
        self,
        issue_types_repo: IssueTypesRepo
    ) -> None:
        self.issue_types_repo = issue_types_repo

    async def get_by_inventory_type_id(
        self,
        invent_type_id: int
    ) -> list[IssueTypeResponse]:
        issue_types = await (
            self.issue_types_repo
            .get_by_inventory_type_id(invent_type_id)
        )

        pydantic_list = []
        for issue in issue_types:
            pydantic_list.append(
                IssueTypeResponse.model_validate(issue)
            )
        
        return pydantic_list
