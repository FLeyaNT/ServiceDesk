from fastapi import (
    APIRouter,
    status,
    Path
)

from typing import Annotated

from core.dependencies import (
    IssueTypesServiceDep
)
from schemas.issue_types import IssueTypeResponse


router = APIRouter(
    prefix='/inventory-types',
    tags=['Inventory Types']
)


@router.get(
    '/{type_id}/issues',
    response_model=list[IssueTypeResponse],
    status_code=status.HTTP_200_OK
)
async def get_inventory_type_issues(
    type_id: Annotated[int, Path()],
    issue_types_service: IssueTypesServiceDep
):
    return await (
        issue_types_service
        .get_by_inventory_type_id(type_id)
    )
