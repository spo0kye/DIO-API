from datetime import datetime
from typing import Annotated, Optional
from pydantic import UUID4, Field, PositiveFloat, PositiveInt

from workout_api.categorias.schemas import CategoriaIn
from workout_api.centro_treinamento.schemas import CentroTreinamentoAtleta
from workout_api.contrib.schemas import BaseSchema, OutMixin


class Atleta(BaseSchema):
    nome: Annotated[str, Field(description="Nome do atleta", example="João", max_length=50)]
    cpf: Annotated[str, Field(description="CPF do atleta", example="12345678900", max_length=11)]
    idade: Annotated[PositiveInt, Field(description="Idade do atleta", example=25)]
    peso: Annotated[PositiveFloat, Field(description="Peso do atleta", example=85.5)]
    altura: Annotated[PositiveFloat, Field(description="Altura do atleta", example=1.83)]
    sexo: Annotated[str, Field(description="Sexo do atleta", example="H", max_length=1)]
    categoria: Annotated[CategoriaIn, Field(description="Categoria do atleta")]
    centro_treinamento: Annotated[CentroTreinamentoAtleta, Field(description="Centro de treinamento do atleta")]

    
class AtletaIn(Atleta):
    pass

    
class AtletaOut(AtletaIn, OutMixin):
    pass


class AtletaUpdate(BaseSchema):
    nome: Annotated[Optional[str], Field(None, description="Nome do atleta", example="João", max_length=50)]
    idade: Annotated[Optional[PositiveInt], Field(None, description="Idade do atleta", example=25)]
    

#class AtletaQuery(BaseSchema):
    #id: Annotated[Optional[str], Field(None, description="ID do atleta", max_length=11)]
    #cpf: Annotated[Optional[str], Field(None, description="CPF do atleta", example="12345678900", max_length=11)]
    #nome: Annotated[Optional[str], Field(None, description="Nome do atleta", example="João", max_length=50)]
    

# Todos os campos são opcionais pois podem ser ignorados no retorno dependendo do filtro escolhido
class AtletaFiltrado(BaseSchema):
    id: Annotated[Optional[UUID4], Field(description="Idendificador")]
    created_at: Annotated[Optional[datetime], Field(description="Data de criação")]
    nome: Annotated[Optional[str], Field(description="Nome do atleta", example="João", max_length=50)]
    cpf: Annotated[Optional[str], Field(description="CPF do atleta", example="12345678900", max_length=11)]
    idade: Annotated[Optional[PositiveInt], Field(description="Idade do atleta", example=25)]
    peso: Annotated[Optional[PositiveFloat], Field(description="Peso do atleta", example=85.5)]
    altura: Annotated[Optional[PositiveFloat], Field(description="Altura do atleta", example=1.83)]
    sexo: Annotated[Optional[str], Field(description="Sexo do atleta", example="H", max_length=1)]
    categoria: Annotated[Optional[CategoriaIn], Field(description="Categoria do atleta")]
    centro_treinamento: Annotated[Optional[CentroTreinamentoAtleta], Field(description="Centro de treinamento do atleta")]