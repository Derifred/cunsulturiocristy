from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Paciente, Cita, Consulta, PiezaDental, TratamientoPieza, Usuario
from config import Config
from dotenv import load_dotenv
from datetime import datetime, date
import json

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Datos de las piezas dentales
PIEZAS_DENTALES_DATA = [
    # Superior Derecho (18 al 11)
    (1, '18', 'Tercer Molar Superior Derecho', 'superior_derecho', 1),
    (2, '17', 'Segundo Molar Superior Derecho', 'superior_derecho', 2),
    (3, '16', 'Primer Molar Superior Derecho', 'superior_derecho', 3),
    (4, '15', 'Segundo Premolar Superior Derecho', 'superior_derecho', 4),
    (5, '14', 'Primer Premolar Superior Derecho', 'superior_derecho', 5),
    (6, '13', 'Canino Superior Derecho', 'superior_derecho', 6),
    (7, '12', 'Incisivo Lateral Superior Derecho', 'superior_derecho', 7),
    (8, '11', 'Incisivo Central Superior Derecho', 'superior_derecho', 8),
    # Superior Izquierdo (21 al 28)
    (9, '21', 'Incisivo Central Superior Izquierdo', 'superior_izquierdo', 1),
    (10, '22', 'Incisivo Lateral Superior Izquierdo', 'superior_izquierdo', 2),
    (11, '23', 'Canino Superior Izquierdo', 'superior_izquierdo', 3),
    (12, '24', 'Primer Premolar Superior Izquierdo', 'superior_izquierdo', 4),
    (13, '25', 'Segundo Premolar Superior Izquierdo', 'superior_izquierdo', 5),
    (14, '26', 'Primer Molar Superior Izquierdo', 'superior_izquierdo', 6),
    (15, '27', 'Segundo Molar Superior Izquierdo', 'superior_izquierdo', 7),
    (16, '28', 'Tercer Molar Superior Izquierdo', 'superior_izquierdo', 8),
    # Inferior Izquierdo (31 al 38)
    (17, '31', 'Incisivo Central Inferior Izquierdo', 'inferior_izquierdo', 1),
    (18, '32', 'Incisivo Lateral Inferior Izquierdo', 'inferior_izquierdo', 2),
    (19, '33', 'Canino Inferior Izquierdo', 'inferior_izquierdo', 3),
    (20, '34', 'Primer Premolar Inferior Izquierdo', 'inferior_izquierdo', 4),
    (21, '35', 'Segundo Premolar Inferior Izquierdo', 'inferior_izquierdo', 5),
    (22, '36', 'Primer Molar Inferior Izquierdo', 'inferior_izquierdo', 6),
    (23, '37', 'Segundo Molar Inferior Izquierdo', 'inferior_izquierdo', 7),
    (24, '38', 'Tercer Molar Inferior Izquierdo', 'inferior_izquierdo', 8),
    # Inferior Derecho (41 al 48)
    (25, '41', 'Incisivo Central Inferior Derecho', 'inferior_derecho', 1),
    (26, '42', 'Incisivo Lateral Inferior Derecho', 'inferior_derecho', 2),
    (27, '43', 'Canino Inferior Derecho', 'inferior_derecho', 3),
    (28, '44', 'Primer Premolar Inferior Derecho', 'inferior_derecho', 4),
    (29, '45', 'Segundo Premolar Inferior Derecho', 'inferior_derecho', 5),
    (30, '46', 'Primer Molar Inferior Derecho', 'inferior_derecho', 6),
    (31, '47', 'Segundo Molar Inferior Derecho', 'inferior_derecho', 7),
    (32, '48', 'Tercer Molar Inferior Derecho', 'inferior_derecho', 8),
]


def insertar_piezas_dentales():
    """Inserta las piezas dentales si la tabla está vacía"""
    try:
        if PiezaDental.query.count() == 0:
            print("Insertando piezas dentales...")
            for pieza in PIEZAS_DENTALES_DATA:
                nueva_pieza = PiezaDental(
                    id_pieza=pieza[0],
                    codigo_pieza=pieza[1],
                    nombre_pieza=pieza[2],
                    cuadrante=pieza[3],
                    posicion=pieza[4]
                )
                db.session.add(nueva_pieza)
            db.session.commit()
            print(f"Se insertaron {len(PIEZAS_DENTALES_DATA)} piezas dentales correctamente")
        else:
            print(f"Las piezas dentales ya existen ({PiezaDental.query.count()} registros)")
    except Exception as e:
        print(f"Error al insertar piezas dentales: {e}")
        db.session.rollback()


with app.app_context():
    db.create_all()
    print("Tablas creadas correctamente")
    insertar_piezas_dentales()


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/main-form')
def main_form():
    return render_template('mainForm.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    usuario = Usuario.query.filter_by(username=username, activo=True).first()

    if usuario and usuario.password == password:
        return jsonify({
            "success": True,
            "message": "Login exitoso",
            "user": usuario.nombre_completo,
            "rol": usuario.rol
        })
    else:
        return jsonify({
            "success": False,
            "message": "Usuario o contrasena incorrectos"
        }), 401


# ==================== API PACIENTES ====================
@app.route('/api/pacientes', methods=['GET', 'POST'])
def api_pacientes():
    if request.method == 'POST':
        data = request.get_json()
        try:
            fecha_nac = None
            if data.get('fecha_nacimiento'):
                fecha_nac = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()

            nuevo_paciente = Paciente(
                cedula=data.get('cedula'),
                nombre_completo=data.get('nombre_completo'),
                telefono=data.get('telefono'),
                correo=data.get('correo'),
                direccion=data.get('direccion'),
                fecha_nacimiento=fecha_nac,
                observaciones_generales=data.get('observaciones_generales'),
                activo=True
            )
            db.session.add(nuevo_paciente)
            db.session.commit()
            return jsonify({"success": True, "mensaje": "Paciente guardado", "id": nuevo_paciente.id_paciente}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "mensaje": str(e)}), 500

    return jsonify({"success": False, "mensaje": "Metodo no permitido"}), 405


@app.route('/api/pacientes/buscar')
def api_buscar_pacientes():
    q = request.args.get('q', '')
    pacientes = Paciente.query.filter(
        (Paciente.cedula.like(f'%{q}%')) |
        (Paciente.nombre_completo.like(f'%{q}%'))
    ).limit(20).all()

    resultado = []
    fecha_actual = date.today()

    for p in pacientes:
        todas_las_citas = Cita.query.filter(
            Cita.id_paciente == p.id_paciente
        ).order_by(Cita.fecha_cita.desc(), Cita.hora_cita.desc()).all()

        citas_agendadas = []
        historial_citas = []

        for cita in todas_las_citas:
            cita_info = {
                "id": cita.id_cita,
                "fecha": cita.fecha_cita.strftime('%Y-%m-%d'),
                "hora": str(cita.hora_cita),
                "motivo": cita.motivo,
                "estado": cita.estado,
                "observaciones": cita.observaciones
            }

            if cita.estado in ['agendada', 'confirmada'] and cita.fecha_cita >= fecha_actual:
                citas_agendadas.append(cita_info)
            else:
                historial_citas.append(cita_info)

        resultado.append({
            "id": p.id_paciente,
            "cedula": p.cedula,
            "nombre_completo": p.nombre_completo,
            "telefono": p.telefono,
            "correo": p.correo,
            "direccion": p.direccion,
            "citas_agendadas": citas_agendadas,
            "historial_citas": historial_citas[:10],
            "total_citas_agendadas": len(citas_agendadas),
            "total_citas_historial": len(historial_citas)
        })

    return jsonify({
        "success": True,
        "data": resultado
    })


@app.route('/api/pacientes/<int:id_paciente>', methods=['GET'])
def api_obtener_paciente(id_paciente):
    try:
        paciente = Paciente.query.get(id_paciente)
        if not paciente:
            return jsonify({
                "success": False,
                "error": "Paciente no encontrado"
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "id": paciente.id_paciente,
                "cedula": paciente.cedula,
                "nombre_completo": paciente.nombre_completo,
                "telefono": paciente.telefono,
                "correo": paciente.correo,
                "direccion": paciente.direccion,
                "fecha_nacimiento": paciente.fecha_nacimiento.strftime(
                    '%Y-%m-%d') if paciente.fecha_nacimiento else None,
                "observaciones_generales": paciente.observaciones_generales
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/pacientes/<int:id_paciente>', methods=['PUT'])
def api_actualizar_paciente(id_paciente):
    try:
        data = request.get_json()
        paciente = Paciente.query.get(id_paciente)

        if not paciente:
            return jsonify({"success": False, "error": "Paciente no encontrado"}), 404

        if 'nombre_completo' in data:
            paciente.nombre_completo = data['nombre_completo']
        if 'telefono' in data:
            paciente.telefono = data['telefono']
        if 'correo' in data:
            paciente.correo = data['correo']
        if 'direccion' in data:
            paciente.direccion = data['direccion']
        if 'fecha_nacimiento' in data and data['fecha_nacimiento']:
            paciente.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
        if 'observaciones_generales' in data:
            paciente.observaciones_generales = data['observaciones_generales']

        db.session.commit()
        return jsonify({"success": True, "message": "Paciente actualizado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/pacientes/<int:id_paciente>', methods=['DELETE'])
def api_eliminar_paciente(id_paciente):
    try:
        paciente = Paciente.query.get(id_paciente)
        if not paciente:
            return jsonify({"success": False, "error": "Paciente no encontrado"}), 404

        nombre_paciente = paciente.nombre_completo
        cedula_paciente = paciente.cedula

        total_citas = Cita.query.filter_by(id_paciente=id_paciente).count()
        total_consultas = Consulta.query.filter_by(id_paciente=id_paciente).count()

        Consulta.query.filter_by(id_paciente=id_paciente).delete()
        Cita.query.filter_by(id_paciente=id_paciente).delete()
        db.session.delete(paciente)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Paciente {nombre_paciente} eliminado correctamente",
            "detalles": {
                "citas_eliminadas": total_citas,
                "consultas_eliminadas": total_consultas
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== API CITAS ====================
# ==================== API CITAS ====================
@app.route('/api/citas', methods=['GET', 'POST', 'PUT'])
def api_citas():
    if request.method == 'POST':
        data = request.get_json()
        try:
            paciente = Paciente.query.filter_by(cedula=data.get('cedula_paciente')).first()
            if not paciente:
                return jsonify({"success": False, "mensaje": "Paciente no encontrado"}), 404

            fecha_cita = datetime.strptime(data.get('fecha_cita'), '%Y-%m-%d').date()
            hora_cita = datetime.strptime(data.get('hora_cita'), '%H:%M').time()

            cita_existente = Cita.query.filter(
                Cita.id_paciente == paciente.id_paciente,
                Cita.fecha_cita == fecha_cita,
                Cita.estado.in_(['agendada', 'confirmada'])
            ).first()

            if cita_existente and not data.get('force', False):
                return jsonify({
                    "success": False,
                    "existe": True,
                    "mensaje": f"El paciente ya tiene una cita agendada para el dia {fecha_cita.strftime('%d/%m/%Y')} a las {cita_existente.hora_cita}",
                    "cita_existente": {
                        "id": cita_existente.id_cita,
                        "hora": str(cita_existente.hora_cita),
                        "motivo": cita_existente.motivo
                    }
                }), 409

            nueva_cita = Cita(
                id_paciente=paciente.id_paciente,
                fecha_cita=fecha_cita,
                hora_cita=hora_cita,
                motivo=data.get('motivo'),
                observaciones=data.get('observaciones'),
                estado=data.get('estado', 'agendada')
            )
            db.session.add(nueva_cita)
            db.session.commit()
            return jsonify({"success": True, "mensaje": "Cita agendada", "id": nueva_cita.id_cita}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "mensaje": str(e)}), 500

    elif request.method == 'GET':
        fecha = request.args.get('fecha')
        if fecha:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            citas = db.session.query(Cita, Paciente).join(Paciente, Cita.id_paciente == Paciente.id_paciente).filter(
                Cita.fecha_cita == fecha_obj,
                Cita.estado.in_(['agendada', 'confirmada'])
            ).all()

            return jsonify({
                "success": True,
                "data": [{
                    "id": c.Cita.id_cita,
                    "hora_cita": str(c.Cita.hora_cita),
                    "paciente_nombre": c.Paciente.nombre_completo,
                    "paciente_cedula": c.Paciente.cedula,
                    "motivo": c.Cita.motivo,
                    "estado": c.Cita.estado,
                    "observaciones": c.Cita.observaciones,
                    "fecha": c.Cita.fecha_cita.strftime('%Y-%m-%d')
                } for c in citas]
            })
        return jsonify({"success": True, "data": []})

    elif request.method == 'PUT':
        data = request.get_json()
        try:
            cita_id = data.get('id_cita')
            cita = Cita.query.get(cita_id)

            if not cita:
                return jsonify({"success": False, "mensaje": "Cita no encontrada"}), 404

            if 'fecha_cita' in data:
                cita.fecha_cita = datetime.strptime(data['fecha_cita'], '%Y-%m-%d').date()
            if 'hora_cita' in data:
                cita.hora_cita = datetime.strptime(data['hora_cita'], '%H:%M').time()
            if 'motivo' in data:
                cita.motivo = data['motivo']
            if 'observaciones' in data:
                cita.observaciones = data['observaciones']
            if 'estado' in data:
                cita.estado = data['estado']

            db.session.commit()
            return jsonify({"success": True, "mensaje": "Cita actualizada correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "mensaje": str(e)}), 500
@app.route('/api/citas/<int:id_cita>', methods=['DELETE'])
def api_eliminar_cita(id_cita):
    try:
        cita = Cita.query.get(id_cita)
        if not cita:
            return jsonify({"success": False, "mensaje": "Cita no encontrada"}), 404

        db.session.delete(cita)
        db.session.commit()
        return jsonify({"success": True, "mensaje": "Cita eliminada correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "mensaje": str(e)}), 500


# ==================== API CONSULTAS ====================
@app.route('/api/consultas', methods=['POST'])
def api_crear_consulta():
    data = request.get_json()
    try:
        paciente = Paciente.query.filter_by(cedula=data.get('cedula_paciente')).first()
        if not paciente:
            return jsonify({"success": False, "mensaje": "Paciente no encontrado"}), 404

        nueva_consulta = Consulta(
            id_paciente=paciente.id_paciente,
            motivo_consulta=data.get('motivo_consulta'),
            diagnostico=data.get('diagnostico'),
            tratamiento=data.get('tratamiento'),
            observaciones=data.get('observaciones')
        )
        db.session.add(nueva_consulta)
        db.session.commit()
        return jsonify({"success": True, "mensaje": "Consulta registrada", "id": nueva_consulta.id_consulta}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "mensaje": str(e)}), 500


@app.route('/api/consultas/historial')
def api_historial_consultas():
    cedula = request.args.get('cedula')
    paciente = Paciente.query.filter_by(cedula=cedula).first()
    if not paciente:
        return jsonify({"success": False, "mensaje": "Paciente no encontrado"}), 404

    consultas = Consulta.query.filter_by(id_paciente=paciente.id_paciente).order_by(
        Consulta.fecha_consulta.desc()).all()

    return jsonify({
        "success": True,
        "data": [{
            "id": c.id_consulta,
            "fecha_consulta": c.fecha_consulta.strftime('%Y-%m-%d %H:%M'),
            "motivo_consulta": c.motivo_consulta,
            "diagnostico": c.diagnostico,
            "tratamiento": c.tratamiento,
            "observaciones": c.observaciones
        } for c in consultas]
    })


# ==================== API TRATAMIENTOS PIEZAS ====================
@app.route('/api/tratamientos-piezas', methods=['POST'])
def api_crear_tratamiento_pieza():
    data = request.get_json()
    try:
        nuevo_tratamiento = TratamientoPieza(
            id_consulta=data.get('id_consulta'),
            id_pieza=data.get('id_pieza'),
            estado_tratamiento=data.get('estado_tratamiento', 'diagnosticado'),
            descripcion_tratamiento=data.get('descripcion_tratamiento')
        )
        db.session.add(nuevo_tratamiento)
        db.session.commit()
        return jsonify(
            {"success": True, "mensaje": "Tratamiento registrado", "id": nuevo_tratamiento.id_tratamiento_pieza}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "mensaje": str(e)}), 500


@app.route('/api/piezas-dentales', methods=['GET'])
def api_listar_piezas():
    piezas = PiezaDental.query.order_by(PiezaDental.id_pieza).all()
    return jsonify({
        "success": True,
        "data": [{
            "id": p.id_pieza,
            "codigo": p.codigo_pieza,
            "nombre": p.nombre_pieza,
            "cuadrante": p.cuadrante
        } for p in piezas]
    })


# ==================== API USUARIOS ====================
@app.route('/api/usuarios', methods=['GET', 'POST'])
def api_usuarios():
    if request.method == 'GET':
        usuarios = Usuario.query.filter_by(activo=True).all()
        return jsonify({
            "success": True,
            "data": [{
                "id": u.id_usuario,
                "username": u.username,
                "nombre_completo": u.nombre_completo,
                "rol": u.rol
            } for u in usuarios]
        })

    elif request.method == 'POST':
        data = request.get_json()
        try:
            existe = Usuario.query.filter_by(username=data.get('username')).first()
            if existe:
                return jsonify({"success": False, "mensaje": "Usuario ya existe"}), 400

            nuevo_usuario = Usuario(
                username=data.get('username'),
                password=data.get('password'),
                nombre_completo=data.get('nombre_completo'),
                rol=data.get('rol', 'usuario'),
                activo=True
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            return jsonify({"success": True, "mensaje": "Usuario creado", "id": nuevo_usuario.id_usuario}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "mensaje": str(e)}), 500

    return jsonify({"success": False, "mensaje": "Metodo no permitido"}), 405


# ==================== API BITACORA ====================
@app.route('/api/bitacora', methods=['GET'])
def api_bitacora():
    try:
        return jsonify({
            "success": True,
            "data": [
                {"fecha_hora": "2026-05-12 10:00:00", "accion": "Login", "descripcion": "Usuario inicio sesion"},
                {"fecha_hora": "2026-05-12 09:30:00", "accion": "Registro", "descripcion": "Nuevo paciente registrado"}
            ]
        })
    except Exception as e:
        return jsonify({"success": False, "mensaje": str(e)}), 500


# ==================== RUTAS ADICIONALES ====================
@app.route('/insertar-paciente', methods=['POST'])
def insertar_paciente():
    return api_pacientes()


@app.route('/pacientes')
def listar_pacientes():
    pacientes = Paciente.query.all()
    return {"pacientes": [{"id": p.id_paciente, "nombre": p.nombre_completo, "cedula": p.cedula} for p in pacientes]}


if __name__ == '__main__':
    app.run(debug=True)