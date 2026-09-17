"""Modelo entidad-relación en SQLAlchemy. Ver docs/modelo-datos.md.

Responsable: David — frente front y plataforma (T-02)
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Productor(Base):
    __tablename__ = "productor"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200))
    municipio: Mapped[str] = mapped_column(String(200))

    parcelas: Mapped[list["Parcela"]] = relationship(back_populates="productor")


class Acopio(Base):
    __tablename__ = "acopio"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200))
    ubicacion: Mapped[str] = mapped_column(String(200))

    parcelas: Mapped[list["Parcela"]] = relationship(back_populates="acopio")
    ventanas_despacho: Mapped[list["VentanaDespacho"]] = relationship(back_populates="acopio")


class Parcela(Base):
    __tablename__ = "parcela"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # id acordado con equipos 1 y 3
    productor_id: Mapped[int] = mapped_column(ForeignKey("productor.id"))
    area_ha: Mapped[float] = mapped_column(Numeric(8, 2))
    ubicacion: Mapped[str] = mapped_column(String(200))
    acopio_id: Mapped[int] = mapped_column(ForeignKey("acopio.id"))
    tiempo_acarreo_min: Mapped[int]
    medio_acarreo: Mapped[str] = mapped_column(String(20))  # cable_via | traccion_animal | otro
    capacidad_medio_racimos: Mapped[int]

    productor: Mapped["Productor"] = relationship(back_populates="parcelas")
    acopio: Mapped["Acopio"] = relationship(back_populates="parcelas")
    aforamientos: Mapped[list["Aforamiento"]] = relationship(back_populates="parcela")
    proyecciones: Mapped[list["ProyeccionCosecha"]] = relationship(back_populates="parcela")


class Aforamiento(Base):
    __tablename__ = "aforamiento"

    id: Mapped[int] = mapped_column(primary_key=True)
    parcela_id: Mapped[str] = mapped_column(ForeignKey("parcela.id"))
    fecha: Mapped[datetime] = mapped_column(DateTime)
    num_plantas: Mapped[int]
    calidad_confianza: Mapped[float] = mapped_column(Numeric(3, 2))  # 0-1

    parcela: Mapped["Parcela"] = relationship(back_populates="aforamientos")


class ProyeccionCosecha(Base):
    __tablename__ = "proyeccion_cosecha"
    __table_args__ = (UniqueConstraint("parcela_id", "periodo", "metodo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    parcela_id: Mapped[str] = mapped_column(ForeignKey("parcela.id"))
    periodo: Mapped[str] = mapped_column(String(10))  # ISO week, "2026-W38"
    volumen_racimos: Mapped[float] = mapped_column(Numeric(10, 2))
    metodo: Mapped[str] = mapped_column(String(30))  # determinista-v1 | predictivo-v1

    parcela: Mapped["Parcela"] = relationship(back_populates="proyecciones")


class Vehiculo(Base):
    __tablename__ = "vehiculo"

    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str] = mapped_column(String(50))
    capacidad_racimos: Mapped[int]
    disponible_desde: Mapped[datetime] = mapped_column(DateTime)
    disponible_hasta: Mapped[datetime] = mapped_column(DateTime)


class VentanaDespacho(Base):
    __tablename__ = "ventana_despacho"

    id: Mapped[int] = mapped_column(primary_key=True)
    acopio_id: Mapped[int] = mapped_column(ForeignKey("acopio.id"))
    periodo: Mapped[str] = mapped_column(String(10))
    inicio: Mapped[datetime] = mapped_column(DateTime)
    fin: Mapped[datetime] = mapped_column(DateTime)

    acopio: Mapped["Acopio"] = relationship(back_populates="ventanas_despacho")


class PlanRecoleccion(Base):
    __tablename__ = "plan_recoleccion"

    id: Mapped[int] = mapped_column(primary_key=True)
    periodo: Mapped[str] = mapped_column(String(10))
    generado_en: Mapped[datetime] = mapped_column(DateTime)
    version_metodo: Mapped[str] = mapped_column(String(30))  # trazabilidad, D-005

    items: Mapped[list["ItemPlan"]] = relationship(back_populates="plan")
    requerimientos: Mapped[list["RequerimientoInsumo"]] = relationship(back_populates="plan")


class ItemPlan(Base):
    __tablename__ = "item_plan"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plan_recoleccion.id"))
    parcela_id: Mapped[str] = mapped_column(ForeignKey("parcela.id"))
    fecha_corte: Mapped[datetime] = mapped_column(DateTime)
    vehiculo_id: Mapped[int | None] = mapped_column(ForeignKey("vehiculo.id"), nullable=True)
    orden: Mapped[int]
    carga_estimada_racimos: Mapped[int]
    cumple_ventana: Mapped[bool] = mapped_column(Boolean)
    motivo: Mapped[str | None] = mapped_column(String(200), nullable=True)

    plan: Mapped["PlanRecoleccion"] = relationship(back_populates="items")


class Insumo(Base):
    __tablename__ = "insumo"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50))  # cajas | carton | bolsas
    unidad: Mapped[str] = mapped_column(String(20))


class CoeficienteConsumo(Base):
    __tablename__ = "coeficiente_consumo"
    __table_args__ = (UniqueConstraint("insumo_id", "productor_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    insumo_id: Mapped[int] = mapped_column(ForeignKey("insumo.id"))
    productor_id: Mapped[int] = mapped_column(ForeignKey("productor.id"))
    valor_por_racimo: Mapped[float] = mapped_column(Numeric(6, 4))


class Inventario(Base):
    __tablename__ = "inventario"
    __table_args__ = (UniqueConstraint("insumo_id", "parcela_id", "periodo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    insumo_id: Mapped[int] = mapped_column(ForeignKey("insumo.id"))
    parcela_id: Mapped[str] = mapped_column(ForeignKey("parcela.id"))
    periodo: Mapped[str] = mapped_column(String(10))
    cantidad_disponible: Mapped[float] = mapped_column(Numeric(10, 2))


class RequerimientoInsumo(Base):
    __tablename__ = "requerimiento_insumo"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plan_recoleccion.id"))
    insumo_id: Mapped[int] = mapped_column(ForeignKey("insumo.id"))
    fecha: Mapped[datetime] = mapped_column(DateTime)
    cantidad_requerida: Mapped[float] = mapped_column(Numeric(10, 2))
    deficit: Mapped[float] = mapped_column(Numeric(10, 2))

    plan: Mapped["PlanRecoleccion"] = relationship(back_populates="requerimientos")
