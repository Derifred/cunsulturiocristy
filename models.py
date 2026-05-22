from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(50), default='usuario')
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Usuario {self.username}>'


class Paciente(db.Model):
    __tablename__ = 'pacientes'

    id_paciente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cedula = db.Column(db.String(20), nullable=False, unique=True, index=True)
    nombre_completo = db.Column(db.String(100), nullable=False, index=True)
    telefono = db.Column(db.String(15))
    correo = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    fecha_nacimiento = db.Column(db.Date)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_primera_consulta = db.Column(db.Date)
    activo = db.Column(db.Boolean, default=True, index=True)
    observaciones_generales = db.Column(db.Text)

    fecha_actualiza = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Paciente {self.nombre_completo}>'


class Cita(db.Model):
    __tablename__ = 'citas'

    id_cita = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('pacientes.id_paciente', ondelete='CASCADE'), nullable=False)
    fecha_cita = db.Column(db.Date, nullable=False, index=True)
    hora_cita = db.Column(db.Time, nullable=False)
    motivo = db.Column(db.String(200))
    estado = db.Column(db.Enum('agendada', 'cancelada', 'atendida', 'completada', name='estado_cita'), default='agendada', index=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    observaciones = db.Column(db.String(500))

    paciente = db.relationship('Paciente', backref='citas')

    fecha_actualiza = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('fecha_cita', 'hora_cita', name='unique_cita_horario'),
        db.Index('idx_paciente', 'id_paciente'),
    )

class Consulta(db.Model):
    __tablename__ = 'consultas'

    id_consulta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('pacientes.id_paciente', ondelete='CASCADE'), nullable=False)
    id_cita = db.Column(db.Integer, db.ForeignKey('citas.id_cita', ondelete='SET NULL'))
    fecha_consulta = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    motivo_consulta = db.Column(db.String(200))
    diagnostico = db.Column(db.Text)
    tratamiento = db.Column(db.Text)
    observaciones = db.Column(db.Text)

    paciente = db.relationship('Paciente', backref='consultas')
    cita = db.relationship('Cita', backref='consulta', uselist=False)

    fecha_actualiza = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Consulta {self.id_consulta} - Paciente {self.id_paciente} - {self.fecha_consulta}>'


class PiezaDental(db.Model):
    __tablename__ = 'piezas_dentales'

    id_pieza = db.Column(db.Integer, primary_key=True, autoincrement=False)
    codigo_pieza = db.Column(db.String(5), nullable=False, index=True)
    nombre_pieza = db.Column(db.String(50), nullable=False)
    cuadrante = db.Column(db.Enum('superior_derecho', 'superior_izquierdo', 'inferior_derecho', 'inferior_izquierdo',
                                  name='cuadrante_tipo'))
    posicion = db.Column(db.Integer)

    fecha_actualiza = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<PiezaDental {self.codigo_pieza} - {self.nombre_pieza}>'


class TratamientoPieza(db.Model):
    __tablename__ = 'tratamientos_piezas'

    id_tratamiento_pieza = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_consulta = db.Column(db.Integer, db.ForeignKey('consultas.id_consulta', ondelete='CASCADE'), nullable=False)
    id_pieza = db.Column(db.Integer, db.ForeignKey('piezas_dentales.id_pieza'), nullable=False)
    estado_tratamiento = db.Column(
        db.Enum('diagnosticado', 'tratado', 'pendiente', 'derivado', name='estado_tratamiento_tipo'),
        default='diagnosticado')
    descripcion_tratamiento = db.Column(db.Text)
    fecha_tratamiento = db.Column(db.DateTime, default=datetime.utcnow)

    consulta = db.relationship('Consulta', backref='tratamientos_piezas')
    pieza_dental = db.relationship('PiezaDental', backref='tratamientos')

    fecha_actualiza = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TratamientoPieza {self.id_tratamiento_pieza} - Consulta {self.id_consulta} - Pieza {self.id_pieza}>'