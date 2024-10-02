# ./information-generation/app/api/routes/organization.py

from fastapi import APIRouter, HTTPException, Depends
from app.services.organization import OrganizationService
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.core.logging_config import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/organizations", status_code=201)
async def create_organization(org_data: OrganizationCreate, service: OrganizationService = Depends()):
    try:
        organization = await service.create_organization(org_data.name, org_data.description)
        logger.info(f"Organization created: {org_data.name}")
        return organization
    except ValueError as e:
        logger.warning(f"Organization creation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/organizations/{org_name}")
async def update_organization(org_name: str, org_data: OrganizationUpdate, service: OrganizationService = Depends()):
    try:
        updated_org = await service.update_organization(org_name, org_data.description)
        logger.info(f"Organization updated: {org_name}")
        return updated_org
    except ValueError as e:
        logger.warning(f"Organization update failed: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/organizations/{org_name}")
async def get_organization(org_name: str, service: OrganizationService = Depends()):
    try:
        organization = await service.get_organization(org_name)
        logger.info(f"Organization retrieved: {org_name}")
        return organization
    
    except:
        logger.warning(f"Organization retrieval failed: {org_name}")
        raise HTTPException(status_code=404, detail="Organization not found")
    
@router.delete("/organizations/{org_name}")
async def delete_organization(org_name: str, service: OrganizationService = Depends()):
    try:
        result = await service.delete_organization(org_name)
        logger.info(f"Organization deleted: {org_name}")
        return result
    except ValueError as e:
        logger.warning(f"Organization deletion failed: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
