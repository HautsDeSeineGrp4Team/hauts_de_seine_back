import os
from typing import List
import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import Product, ProductCreate, ProductResponse, ProductUpdate, ProductUpdateStatus, ProductUpdatesAssociation
from crud.crud_user import get_user_by_id
from crud.crud_product import get_product_by_id
from models.status import Status
import json

router = APIRouter()

@router.post("/", status_code=201)
async def create_new_product(
    product: ProductCreate, 
    db: Session = Depends(get_db)
):
    """Crée un nouveau produit avec des images associées."""

    current_date = datetime.datetime.now().strftime("%Y%m%d")
    random_part = str(uuid.uuid4()).split("-")[0]
    reference = f"PRD-{current_date}-{random_part}"

    user = get_user_by_id(db, product.user_id) if product.user_id else None
    mairie_user = get_user_by_id(db, product.mairie_user_id)
    if mairie_user is None:
        raise HTTPException(status_code=404, detail="Mairie utilisateur non trouvé.")

    product_data = product.dict(exclude={'user_id', 'mairie_user_id'})
    product_data["photos"] = json.dumps(product_data["photos"])
    product_db = Product(**product_data, reference=reference, user_id=user.id if user else None, mairie_user_id=mairie_user.id)
    try:
        db.add(product_db)
        db.commit();
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du produit : {str(e)}")

    return {"product": product_db}

@router.get("/")
def get_all_products(db: Session = Depends(get_db), skip: int = 0, limit: int = 10) -> list[ProductResponse]:
    """Retourne tous les produits avec leurs images associées."""
    
    products = db.query(Product).offset(skip).limit(limit).all()
    
    product_responses = []
    for product in products:
        product_response = ProductResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            reference=product.reference,
            photos=json.loads(product.photos)
        )
        product_responses.append(product_response)
    
    return product_responses

@router.get("/{product_id}")
def get_product(product_id: uuid.UUID, db: Session = Depends(get_db)) -> ProductResponse:
    """Retourne un produit avec ses images associées."""
    
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")
    
    product_response = ProductResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            reference=product.reference,
            photos=json.loads(product.photos)
        )
    
    return product_response
  
@router.get("/user/{user_id}")
def get_product_by_user_id(user_id: uuid.UUID, db: Session = Depends(get_db)) -> list[ProductResponse]:
    """Retourne les produits du user avec leurs images associées."""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    
    products = db.query(Product).filter(Product.user_id == user.id).all()
    
    product_responses = []
    for product in products:
        product_response = ProductResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            reference=product.reference,
            photos=json.loads(product.photos)
        )
        product_responses.append(product_response)
    
    return product_responses

@router.put("/{product_id}/status")
async def update_product_status(product: ProductUpdateStatus, db: Session = Depends(get_db)) -> ProductResponse:
    """Met à jour uniquement le status d'un produit."""
    
    product_db = get_product_by_id(db, product.id)
    if product_db is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")
    
    product_db.status = product.status
    product_db.updated_at = datetime.datetime.now(datetime.timezone.utc)
    
    db.commit()
    db.refresh(product_db)
    
    return product_db

@router.put("/{product_id}/association")
async def update_product_association(product: ProductUpdatesAssociation, db: Session = Depends(get_db)) -> ProductResponse :
    """Met à jour l'association d'un produit."""
    
    product_db = get_product_by_id(db, product.id)
    if product_db is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")

    asso = get_user_by_id(db, product.association_user_id)
    if asso is None:
      raise HTTPException(status_code=404, detail="Association non trouvée.")
    
    product_db.association_user_id = asso.id
    product_db.updated_at = datetime.datetime.now(datetime.timezone.utc)
    
    db.commit()
    db.refresh(product_db)
    
    return product_db
  
@router.delete("/{product_id}")
def delete_product(product_id: uuid.UUID, db: Session = Depends(get_db)):
    """Supprime un produit avec ses images associées."""
    
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")
    
    db.delete(product)
    db.commit()
    
    return {"message": "Produit supprimé avec succès."}
  
@router.put("/{product_id}/deposed")
def update_product_deposed_at(product_id: uuid.UUID, db: Session = Depends(get_db)) -> ProductResponse :
    """Met à jour la date de déposition d'un produit."""
    
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")
    
    product.deposed_at = datetime.datetime.now(datetime.timezone.utc)
    product.updated_at = datetime.datetime.now(datetime.timezone.utc)
    
    db.commit()
    db.refresh(product)
    
    return product

@router.get("/mairie/{mairie_id}")
def get_product_by_mairie_id(mairie_id: uuid.UUID, db: Session = Depends(get_db)) -> list[ProductResponse] :
    """Retourne les produits de la mairie"""
    mairie = get_user_by_id(db, mairie_id)
    if mairie is None:
        raise HTTPException(status_code=404, detail="Mairie non trouvée.")
    
    products = db.query(Product).filter(Product.mairie_user_id == mairie.id).all()
    
    product_responses = []
    for product in products:
        product_response = ProductResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            reference=product.reference,
            photos=json.loads(product.photos)
        )
        product_responses.append(product_response)
    
    return product_responses

@router.get("/association/{association_id}")
def get_product_by_association_id(association_id: uuid.UUID, db: Session = Depends(get_db)) -> list[ProductResponse]:
    """Retourne les produits de l'association avec leurs images associées."""
    association = get_user_by_id(db, association_id)
    if association is None:
        raise HTTPException(status_code=404, detail="Association non trouvée.")
    
    products = db.query(Product).filter(Product.association_user_id == association.id).all()
    
    product_responses = []
    for product in products:
        product_response = ProductResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            reference=product.reference,
            photos=json.loads(product.photos)
        )
        product_responses.append(product_response)
    
    return product_responses
