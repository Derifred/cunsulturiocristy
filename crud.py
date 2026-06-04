# crud.py
from sqlalchemy.orm import Session
from models import db, Paciente, Cita, Consulta, PiezaDental, TratamientoPieza, Usuario
from datetime import datetime, date
from typing import Optional, List, Dict, Any


# ==================== CRUD USUARIO ====================
def get_usuarios(db_session: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
    """Obtener todos los usuarios activos"""
    return db_session.query(Usuario).filter(Usuario.activo == True).offset(skip).limit(limit).all()


def get_usuario_by_id(db_session: Session, usuario_id: int) -> Optional[Usuario]:
    """Obtener usuario por ID"""
    return db_session.query(Usuario).filter(Usuario.id_usuario == usuario_id, Usuario.activo == True).first()


def get_usuario_by_username(db_session: Session, username: str) -> Optional[Usuario]:
    """Obtener usuario por nombre de usuario"""
    return db_session.query(Usuario).filter(Usuario.username == username, Usuario.activo == True).first()


def create_usuario(db_session: Session, username: str, password: str, nombre_completo: str,
                   rol: str = 'usuario') -> Usuario:
    """Crear un nuevo usuario"""
    db_usuario = Usuario(
        username=username,
        password=password,
        nombre_completo=nombre_completo,
        rol=rol,
        activo=True
    )
    db_session.add(db_usuario)
    db_session.commit()
    db_session.refresh(db_usuario)
    return db_usuario


def update_usuario(db_session: Session, usuario_id: int, **kwargs) -> Optional[Usuario]:
    """Actualizar un usuario"""
    usuario = get_usuario_by_id(db_session, usuario_id)
    if not usuario:
        return None
    for key, value in kwargs.items():
        if hasattr(usuario, key) and key not in ['id_usuario', 'username']:
            setattr(usuario, key, value)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario


def delete_usuario(db_session: Session, usuario_id: int) -> bool:
    """Eliminar usuario (soft delete)"""
    usuario = get_usuario_by_id(db_session, usuario_id)
    if not usuario:
        return False
    usuario.activo = False
    db_session.commit()
    return True


# ==================== CRUD PACIENTE ====================
def get_pacientes(db_session: Session, skip: int = 0, limit: int = 100, solo_activos: bool = True) -> List[Paciente]:
    """Obtener todos los pacientes"""
    query = db_session.query(Paciente)
    if solo_activos:
        query = query.filter(Paciente.activo == True)
    return query.offset(skip).limit(limit).all()


def get_paciente_by_id(db_session: Session, paciente_id: int) -> Optional[Paciente]:
    """Obtener paciente por ID"""
    return db_session.query(Paciente).filter(Paciente.id_paciente == paciente_id, Paciente.activo == True).first()


def get_paciente_by_cedula(db_session: Session, cedula: str) -> Optional[Paciente]:
    """Obtener paciente por cédula"""
    return db_session.query(Paciente).filter(Paciente.cedula == cedula, Paciente.activo == True).first()


def search_pacientes(db_session: Session, termino: str, limit: int = 20) -> List[Paciente]:
    """Buscar pacientes por cédula o nombre"""
    return db_session.query(Paciente).filter(
        Paciente.activo == True,
        (Paciente.cedula.like(f'%{termino}%')) |
        (Paciente.nombre_completo.like(f'%{termino}%'))
    ).limit(limit).all()


def create_paciente(db_session: Session, cedula: str, nombre_completo: str, **kwargs) -> Paciente:
    """Crear un nuevo paciente"""
    db_paciente = Paciente(
        cedula=cedula,
        nombre_completo=nombre_completo,
        telefono=kwargs.get('telefono'),
        correo=kwargs.get('correo'),
        direccion=kwargs.get('direccion'),
        fecha_nacimiento=kwargs.get('fecha_nacimiento'),
        observaciones_generales=kwargs.get('observaciones_generales'),
        activo=True
    )
    db_session.add(db_paciente)
    db_session.commit()
    db_session.refresh(db_paciente)
    return db_paciente


def update_paciente(db_session: Session, paciente_id: int, **kwargs) -> Optional[Paciente]:
    """Actualizar un paciente (la cédula no se modifica)"""
    paciente = get_paciente_by_id(db_session, paciente_id)
    if not paciente:
        return None
    for key, value in kwargs.items():
        if hasattr(paciente, key) and key != 'cedula':
            setattr(paciente, key, value)
    db_session.commit()
    db_session.refresh(paciente)
    return paciente


def delete_paciente(db_session: Session, paciente_id: int) -> Dict[str, int]:
    """Eliminar paciente y todos sus registros asociados"""
    paciente = get_paciente_by_id(db_session, paciente_id)
    if not paciente:
        return {"error": "Paciente no encontrado"}

    # Contar registros asociados
    total_citas = db_session.query(Cita).filter(Cita.id_paciente == paciente_id).count()
    total_consultas = db_session.query(Consulta).filter(Consulta.id_paciente == paciente_id).count()

    # Eliminar tratamientos de piezas (a través de consultas)
    subquery = db_session.query(Consulta.id_consulta).filter(Consulta.id_paciente == paciente_id).subquery()
    db_session.query(TratamientoPieza).filter(TratamientoPieza.id_consulta.in_(subquery)).delete(
        synchronize_session=False)

    # Eliminar consultas
    db_session.query(Consulta).filter(Consulta.id_paciente == paciente_id).delete()

    # Eliminar citas
    db_session.query(Cita).filter(Cita.id_paciente == paciente_id).delete()

    # Eliminar paciente
    db_session.delete(paciente)
    db_session.commit()

    return {
        "citas_eliminadas": total_citas,
        "consultas_eliminadas": total_consultas
    }


# ==================== CRUD CITA ====================
def get_citas(db_session: Session, skip: int = 0, limit: int = 100) -> List[Cita]:
    """Obtener todas las citas"""
    return db_session.query(Cita).order_by(Cita.fecha_cita.desc(), Cita.hora_cita.desc()).offset(skip).limit(
        limit).all()


def get_cita_by_id(db_session: Session, cita_id: int) -> Optional[Cita]:
    """Obtener cita por ID"""
    return db_session.query(Cita).filter(Cita.id_cita == cita_id).first()


def get_citas_by_fecha(db_session: Session, fecha: date) -> List:
    """Obtener citas por fecha con datos del paciente"""
    return db_session.query(Cita, Paciente).join(Paciente, Cita.id_paciente == Paciente.id_paciente).filter(
        Cita.fecha_cita == fecha,
        Cita.estado.in_(['agendada', 'confirmada'])
    ).all()


def get_citas_by_paciente(db_session: Session, paciente_id: int, solo_futuras: bool = True) -> List[Cita]:
    """Obtener citas de un paciente"""
    query = db_session.query(Cita).filter(Cita.id_paciente == paciente_id)
    if solo_futuras:
        query = query.filter(Cita.fecha_cita >= date.today())
    return query.order_by(Cita.fecha_cita, Cita.hora_cita).all()


def verificar_cita_duplicada(db_session: Session, paciente_id: int, fecha_cita: date) -> Optional[Cita]:
    """Verificar si el paciente ya tiene cita el mismo día"""
    return db_session.query(Cita).filter(
        Cita.id_paciente == paciente_id,
        Cita.fecha_cita == fecha_cita,
        Cita.estado.in_(['agendada', 'confirmada'])
    ).first()


def create_cita(db_session: Session, id_paciente: int, fecha_cita: date, hora_cita, **kwargs) -> Cita:
    """Crear una nueva cita"""
    db_cita = Cita(
        id_paciente=id_paciente,
        fecha_cita=fecha_cita,
        hora_cita=hora_cita,
        motivo=kwargs.get('motivo'),
        observaciones=kwargs.get('observaciones'),
        estado=kwargs.get('estado', 'agendada')
    )
    db_session.add(db_cita)
    db_session.commit()
    db_session.refresh(db_cita)
    return db_cita


def update_cita(db_session: Session, cita_id: int, **kwargs) -> Optional[Cita]:
    """Actualizar una cita"""
    cita = get_cita_by_id(db_session, cita_id)
    if not cita:
        return None
    for key, value in kwargs.items():
        if hasattr(cita, key):
            if key in ['fecha_cita', 'hora_cita'] and value:
                if key == 'fecha_cita':
                    setattr(cita, key, datetime.strptime(value, '%Y-%m-%d').date() if isinstance(value, str) else value)
                elif key == 'hora_cita':
                    setattr(cita, key, datetime.strptime(value, '%H:%M').time() if isinstance(value, str) else value)
            else:
                setattr(cita, key, value)
    db_session.commit()
    db_session.refresh(cita)
    return cita


def delete_cita(db_session: Session, cita_id: int) -> bool:
    """Eliminar una cita"""
    cita = get_cita_by_id(db_session, cita_id)
    if not cita:
        return False
    db_session.delete(cita)
    db_session.commit()
    return True


def completar_cita(db_session: Session, cita_id: int) -> Optional[Cita]:
    """Marcar cita como completada"""
    return update_cita(db_session, cita_id, estado='completada')


# ==================== CRUD CONSULTA ====================
def get_consultas(db_session: Session, skip: int = 0, limit: int = 100) -> List[Consulta]:
    """Obtener todas las consultas"""
    return db_session.query(Consulta).order_by(Consulta.fecha_consulta.desc()).offset(skip).limit(limit).all()


def get_consulta_by_id(db_session: Session, consulta_id: int) -> Optional[Consulta]:
    """Obtener consulta por ID"""
    return db_session.query(Consulta).filter(Consulta.id_consulta == consulta_id).first()


def get_consultas_by_paciente(db_session: Session, paciente_id: int) -> List[Consulta]:
    """Obtener consultas de un paciente"""
    return db_session.query(Consulta).filter(Consulta.id_paciente == paciente_id).order_by(
        Consulta.fecha_consulta.desc()).all()


def create_consulta(db_session: Session, id_paciente: int, **kwargs) -> Consulta:
    """Crear una nueva consulta"""
    db_consulta = Consulta(
        id_paciente=id_paciente,
        id_cita=kwargs.get('id_cita'),
        motivo_consulta=kwargs.get('motivo_consulta'),
        diagnostico=kwargs.get('diagnostico'),
        tratamiento=kwargs.get('tratamiento'),
        observaciones=kwargs.get('observaciones')
    )
    db_session.add(db_consulta)
    db_session.commit()
    db_session.refresh(db_consulta)
    return db_consulta


def update_consulta(db_session: Session, consulta_id: int, **kwargs) -> Optional[Consulta]:
    """Actualizar una consulta"""
    consulta = get_consulta_by_id(db_session, consulta_id)
    if not consulta:
        return None
    for key, value in kwargs.items():
        if hasattr(consulta, key):
            setattr(consulta, key, value)
    db_session.commit()
    db_session.refresh(consulta)
    return consulta


def delete_consulta(db_session: Session, consulta_id: int) -> bool:
    """Eliminar una consulta y sus tratamientos asociados"""
    consulta = get_consulta_by_id(db_session, consulta_id)
    if not consulta:
        return False
    # Eliminar tratamientos de piezas asociados
    db_session.query(TratamientoPieza).filter(TratamientoPieza.id_consulta == consulta_id).delete()
    db_session.delete(consulta)
    db_session.commit()
    return True


# ==================== CRUD PIEZAS DENTALES ====================
def get_piezas_dentales(db_session: Session) -> List[PiezaDental]:
    """Obtener todas las piezas dentales"""
    return db_session.query(PiezaDental).order_by(PiezaDental.id_pieza).all()


def get_pieza_by_id(db_session: Session, pieza_id: int) -> Optional[PiezaDental]:
    """Obtener pieza dental por ID"""
    return db_session.query(PiezaDental).filter(PiezaDental.id_pieza == pieza_id).first()


def get_piezas_by_cuadrante(db_session: Session, cuadrante: str) -> List[PiezaDental]:
    """Obtener piezas por cuadrante"""
    return db_session.query(PiezaDental).filter(PiezaDental.cuadrante == cuadrante).order_by(PiezaDental.posicion).all()


# ==================== CRUD TRATAMIENTO PIEZA ====================
def get_tratamientos_by_consulta(db_session: Session, consulta_id: int) -> List[TratamientoPieza]:
    """Obtener tratamientos de una consulta"""
    return db_session.query(TratamientoPieza).filter(TratamientoPieza.id_consulta == consulta_id).all()


def create_tratamiento_pieza(db_session: Session, id_consulta: int, id_pieza: int, **kwargs) -> TratamientoPieza:
    """Crear un tratamiento para una pieza dental"""
    db_tratamiento = TratamientoPieza(
        id_consulta=id_consulta,
        id_pieza=id_pieza,
        estado_tratamiento=kwargs.get('estado_tratamiento', 'diagnosticado'),
        descripcion_tratamiento=kwargs.get('descripcion_tratamiento')
    )
    db_session.add(db_tratamiento)
    db_session.commit()
    db_session.refresh(db_tratamiento)
    return db_tratamiento