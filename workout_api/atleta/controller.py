from datetime import datetime
from typing import Optional, Union
from uuid import uuid4
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi_pagination import LimitOffsetPage, Page, LimitOffsetParams
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from workout_api.atleta.models import AtletaModel
from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate, AtletaFiltrado
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter()

@router.post(
    "/",
    summary="Cria um novo atleta",
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut
)
async def post(
    db_session: DatabaseDependency,
    atleta_in: AtletaIn = Body(...)
):
    categoria = (await db_session.execute(select(CategoriaModel).filter_by(nome=atleta_in.categoria.nome))).scalars().first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A categoria {atleta_in.categoria.nome} não encontrada"
        )
     
    centro_treinamento = (await db_session.execute(select(CentroTreinamentoModel).filter_by(nome=atleta_in.centro_treinamento.nome))).scalars().first()
    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O centro de treinamento {atleta_in.categoria.nome} não foi encontrado"
        )
        
    atleta_out = AtletaOut(id=uuid4(), created_at=datetime.now() , **atleta_in.model_dump())
    
    # O exclude= serve para não incluir os objetos diretamente no atleta sem relacionar, apenas clonando
    # Assim então o relacionamento deve ser feito utilizando as Keys de "categoria" e "centro de treinamento"
    atleta_model = AtletaModel(**atleta_out.model_dump(exclude={"categoria", "centro_treinamento"}))
    atleta_model.categoria_id = categoria.pk_id
    atleta_model.centro_treinamento_id = centro_treinamento.pk_id
    try:
        db_session.add(atleta_model)
        await db_session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe um atleta cadastrado com o CPF {atleta_model.cpf}"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao inserir os dados no banco de dados: {Exception}"
        )
    
    return atleta_out

@router.get(
    "/get_all",
    summary="Consultar todos os atletas",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage,
)
async def get_all_atletas(
    db_session: DatabaseDependency,
    nome: Optional[bool] = False,
    categoria: Optional[bool] = False,
    centro_treinamento: Optional[bool] = False,
    params: LimitOffsetParams = Depends()
) -> LimitOffsetPage:
    if not nome and not categoria and not centro_treinamento:
        pesquisa = (
            select(AtletaModel)
            .options(selectinload(AtletaModel.categoria), selectinload(AtletaModel.centro_treinamento))
        )
        
        resultado = await paginate(db_session, pesquisa, params)
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"A lista de atletas está vazia"
            )
        atletas = [AtletaOut.model_validate(a, from_attributes=True) for a in resultado.items]
        return LimitOffsetPage.create(items=atletas, total=resultado.total, params=params)
    
    else:
        colunas = [AtletaModel.cpf]
        colunas.append(AtletaModel.nome) if nome else None
        colunas.append(CategoriaModel.nome.label("categoria")) if categoria else None
        colunas.append(CentroTreinamentoModel.nome.label("centro_treinamento")) if centro_treinamento else None
        
        cmd = select(*colunas)
        cmd = cmd.join(AtletaModel.categoria) if categoria else cmd
        cmd = cmd.join(AtletaModel.centro_treinamento) if centro_treinamento else cmd
        
        resultado = await paginate(db_session, cmd, params=params)
        atletas = []
        for row in resultado.items:
            d = dict(row._mapping)
            d.pop("cpf")
            atletas.append(d)
            
        return LimitOffsetPage.create(items=atletas, total=resultado.total, params=params)
    

@router.get(
    "/",
    summary="Consultar atletas pelo ID, nome ou CPF",
    status_code=status.HTTP_200_OK,
    response_model=list[AtletaOut],
)
async def query(
    db_session: DatabaseDependency,
    id: Optional[UUID4] = Query(None),
    nome: Optional[str] = Query(None),
    cpf: Optional[str] = Query(None)
) -> list[AtletaOut]:
    if id == None and nome == None and cpf == None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi informado nenhum ID, nome ou CPF para a consulta"
        )
    
    params = {}
    if id is not None: params["id"] = id
    if nome is not None: params["nome"] = nome
    if cpf is not None: params["cpf"] = cpf
    
    atletas = (await db_session.execute(select(AtletaModel).filter_by(**params))).scalars().all()
    return atletas


@router.patch(
    "/{id}",
    summary="Editar um atleta pelo ID",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def update(id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:
    atleta = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nenhum atleta encontrado com o ID: {id}"
        )
        
    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)
    
    await db_session.commit()
    await db_session.refresh(atleta)
    return atleta


@router.delete(
    "/{id}",
    summary="Editar um atleta pelo ID",
    status_code=status.HTTP_204_NO_CONTENT
)
async def update(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nenhum atleta encontrado com o ID: {id}"
        )

    await db_session.delete(atleta)
    await db_session.commit()