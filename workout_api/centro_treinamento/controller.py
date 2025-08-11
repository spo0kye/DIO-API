from uuid import uuid4
from fastapi import APIRouter, Body, Depends, status, HTTPException
from fastapi_pagination import LimitOffsetPage, LimitOffsetParams, paginate
from pydantic import UUID4

from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from workout_api.contrib.dependencies import DatabaseDependency
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError


router = APIRouter()

@router.post(
    "/",
    summary="Cria um novo centro de treinamento",
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut
)
async def post(
    db_session: DatabaseDependency,
    centro_treinamento_in: CentroTreinamentoIn = Body(...)
) -> CentroTreinamentoOut:
    centro_treinamento_out = CentroTreinamentoOut(id=uuid4(), **centro_treinamento_in.model_dump())
    centro_treinamento_model = CentroTreinamentoModel(**centro_treinamento_out.model_dump())
    
    try:
        db_session.add(centro_treinamento_model)
        await db_session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Centro de treinamento já existente no banco de dados"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Erro ao inserir os dados no banco de dados: {Exception}"
        )
        
    return centro_treinamento_out


@router.get(
    "/",
    summary="Consulta todos os centros de treinamento",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[CentroTreinamentoOut]
)
async def query(db_session: DatabaseDependency, params: LimitOffsetParams = Depends()) -> LimitOffsetPage[CentroTreinamentoOut]:
    resultado = await paginate(db_session, select(CentroTreinamentoModel), params=params)
    centros_treinamento = [CentroTreinamentoOut.model_validate(r, from_attributes=True) for r in resultado.items]
    return LimitOffsetPage.create(items=centros_treinamento, total=resultado.total, params=params)


@router.get(
    "/{id}",
    summary="Consulta todos os centros de treinamento",
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut
)
async def query(id: UUID4, db_session: DatabaseDependency) -> CentroTreinamentoOut:
    categoria: CentroTreinamentoOut = (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))).scalars().first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detalis=f"Categoria não encontrada no ID: {id}"
        )
    
    return categoria