from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from ..dependencies import get_db, admin_required
from ..models.configuration import Configuration
from ..schemas.configuration import ConfigUpdate, ConfigResponse

router = APIRouter(prefix="/api/config", tags=["Configuration"])

PUBLIC_KEYS = ["voting_window_hours", "mess_name", "contact_info"]

@router.get("")
def get_public_config(db: Session = Depends(get_db)):
    configs = db.query(Configuration).filter(Configuration.key.in_(PUBLIC_KEYS)).all()
    result = {}
    for c in configs:
        try:
            result[c.key] = json.loads(c.value)
        except (json.JSONDecodeError, TypeError):
            result[c.key] = c.value
    return result

@router.get("/all", response_model=list[ConfigResponse])
def get_all_config(db: Session = Depends(get_db), admin=Depends(admin_required)):
    configs = db.query(Configuration).all()
    result = []
    for c in configs:
        try:
            val = json.loads(c.value)
        except (json.JSONDecodeError, TypeError):
            val = c.value
        result.append({"id": c.id, "key": c.key, "value": val})
    return result

@router.put("", response_model=ConfigResponse)
def update_config(req: ConfigUpdate, db: Session = Depends(get_db),
                  admin=Depends(admin_required)):
    config = db.query(Configuration).filter(Configuration.key == req.key).first()
    value_str = json.dumps(req.value) if not isinstance(req.value, str) else req.value
    if config:
        config.value = value_str
        config.updated_by = admin.id
    else:
        config = Configuration(key=req.key, value=value_str, updated_by=admin.id)
        db.add(config)
    db.commit(); db.refresh(config)
    try:
        val = json.loads(config.value)
    except (json.JSONDecodeError, TypeError):
        val = config.value
    return ConfigResponse(id=config.id, key=config.key, value=val)
