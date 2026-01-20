from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from database import get_conn
from rules import data_futura, horario_comercial

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}

@app.route("/agendar", methods=["POST"])
def agendar():
    dados = request.json

    nome = dados.get("nome")
    telefone = dados.get("telefone")
    data_consulta = dados.get("data")
    hora_inicio = dados.get("hora")

    if not all([nome, telefone, data_consulta, hora_inicio]):
        return jsonify({"erro": "Dados incompletos"}), 400

    if not data_futura(data_consulta):
        return jsonify({"erro": "Data inválida"}), 400

    if not horario_comercial(hora_inicio):
        return jsonify({"erro": "Horário fora do expediente"}), 400

    hora_fim = (
        datetime.strptime(hora_inicio, "%H:%M")
        + timedelta(minutes=30)
    ).strftime("%H:%M")

    conn = get_conn()
    cur = conn.cursor()

    # 1️⃣ verifica se já existe agendamento para o telefone na mesma data
    cur.execute("""
        SELECT id FROM agendamentos
        WHERE telefone = ?
        AND data = ?
        AND status = 'CONFIRMADO'
    """, (telefone, data_consulta))

    agendamento_existente = cur.fetchone()

    # 2️⃣ verifica conflito de horário
    if agendamento_existente:
        agendamento_id = agendamento_existente["id"]

        # ignora o próprio registro
        cur.execute("""
            SELECT 1 FROM agendamentos
            WHERE data = ?
            AND hora_inicio < ?
            AND hora_fim > ?
            AND status = 'CONFIRMADO'
            AND id != ?
        """, (data_consulta, hora_fim, hora_inicio, agendamento_id))
    else:
        cur.execute("""
            SELECT 1 FROM agendamentos
            WHERE data = ?
            AND hora_inicio < ?
            AND hora_fim > ?
            AND status = 'CONFIRMADO'
        """, (data_consulta, hora_fim, hora_inicio))

    if cur.fetchone():
        conn.close()
        return jsonify({"erro": "Horário indisponível"}), 409

    # 3️⃣ reagendamento
    if agendamento_existente:
        cur.execute("""
            UPDATE agendamentos
            SET hora_inicio = ?, hora_fim = ?
            WHERE id = ?
        """, (hora_inicio, hora_fim, agendamento_id))

        conn.commit()
        conn.close()

        return jsonify({
            "msg": "Consulta reagendada com sucesso",
            "data": data_consulta,
            "hora": hora_inicio
        })

    # 4️⃣ novo agendamento
    cur.execute("""
        INSERT INTO agendamentos
        (nome, telefone, data, hora_inicio, hora_fim)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, telefone, data_consulta, hora_inicio, hora_fim))

    conn.commit()
    conn.close()

    return jsonify({
        "msg": "Consulta agendada com sucesso",
        "data": data_consulta,
        "hora": hora_inicio
    })
