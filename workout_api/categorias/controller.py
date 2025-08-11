from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Body, Depends, status, HTTPException
from pydantic import UUID4

from fastapi_pagination import LimitOffsetPage, Page, LimitOffsetParams
from fastapi_pagination.ext.sqlalchemy import paginate
from workout_api.categorias.schemas import CategoriaIn, CategoriaOut
from workout_api.contrib.dependencies import DatabaseDependency
from workout_api.categorias.models import CategoriaModel
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError


router = APIRouter()

@router.post(
    "/",
    summary="Cria uma nova categoria",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoriaIn
)
async def post(
    db_session: DatabaseDependency,
    categoria_in: CategoriaIn = Body(...)
):
    categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())
    categoria_model = CategoriaModel(**categoria_out.model_dump())
    
    try:
        db_session.add(categoria_model)
        await db_session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Categoria já existente no banco de dados"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Erro ao inserir os dados no banco de dados: {Exception}"
        )
        
    return categoria_out


@router.get(
    "/",
    summary="Consulta todas as categorias",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[CategoriaOut],
)
async def query(db_session: DatabaseDependency, params: LimitOffsetParams = Depends()) -> list[CategoriaOut]:
    resultado = (await paginate(db_session, select(CategoriaModel), params=params))
    categorias = [CategoriaOut.model_validate(r, from_attributes=True) for r in resultado.items]
    return LimitOffsetPage.create(items=categorias, total=resultado.total, params=params)


@router.get(
    "/{id}",
    summary="Consulta uma categoria pelo ID",
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut
)
async def query(id: UUID4, db_session: DatabaseDependency) -> CategoriaOut:
    categoria: CategoriaOut = (await db_session.execute(select(CategoriaModel).filter_by(id=id))).scalars().first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detalis=f"Categoria não encontrada no ID: {id}"
        )
    
    return categoria