
from flask import (
    Blueprint, render_template, request, jsonify, url_for, redirect
    )
from app.models import Activity
from app import db
from app.functions_proc import transformador_prioridade_num_texto, transformador_prioridade_texto_num, Prioridades

main = Blueprint("main", __name__)


@main.route("/reset-db", methods=["POST"])
def reset_database():

    try:
        db.session.execute(
            db.text("TRUNCATE TABLE activities RESTART IDENTITY CASCADE")
        )

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Banco de dados reiniciado!"
        }), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@main.route("/")
def dashboard():

    last_10 = Activity.query.order_by(
        Activity.created_at
        ).limit(10).all()

    metrics = {
        "recebidos": Activity.query.count(),
        
        "processados": Activity.query.filter_by(
            status="Concluido"
        ).count(),

        "pendentes": Activity.query.filter_by(
            status="Pendente"
        ).count(),

        "erros": Activity.query.filter_by(
            status="Erro"
        ).count()
    }
    
    return render_template(
        "dashboard.html",
        metrics=metrics,
        last_10= last_10,
        prioridades= Prioridades
    )

@main.route("/interno")
def filtro():
     # Captura o que foi digitado na barra de pesquisa
    tipo_solicitacao = request.args.get("tipo_solicitacao", "").strip()
    atividades = Activity.query.filter_by(status="Pendente")
    if tipo_solicitacao:
        if tipo_solicitacao in ["Pendente", "Concluido", "Erro"]:
            atividades = atividades.filter(
                Activity.subject.ilike(f"%{tipo_solicitacao}%")
            )
        atividades = Activity.query.filter_by(status=str(tipo_solicitacao))
        if tipo_solicitacao == "Pendente":
            metrics = {
                "recebido": Activity.query.count(),
                "não iniciado": Activity.query.filter_by(status_interno = "Pendente").count(),
                "esperando retorno": Activity.query.filter_by(status_interno = "Aguardando").count(),
                "em aguardo de materiais": Activity.query.filter_by(status_interno = "Materiais").count(),
                "em espera pelo prazo": Activity.query.filter_by(status_interno = "Prazo").count()
                
            }
        else:
            metrics ={
                 "recebido": Activity.query.count(),
                 "pendentes":  Activity.query.filter_by(status = "Pendente").count(),
                 "concluido":  Activity.query.filter_by(status = "Concluido").count(),
                 "erros":  Activity.query.filter_by(status = "Erro").count()
            }
        
    else:
        tipo_solicitacao = "Pendente"
        atividades = Activity.query.filter_by(status='Pendente')
        
        metrics = {
            "recebido": Activity.query.count(),
            "não iniciado": Activity.query.filter_by(status_interno = "Pendente").count(),
            "esperando retorno": Activity.query.filter_by(status_interno = "Aguardando").count(),
            "em aguardo de materiais": Activity.query.filter_by(status_interno = "Materiais").count(),
            "em espera pelo prazo": Activity.query.filter_by(status_interno = "Prazo").count()
            
        }
        
    return render_template(
        "pendentes.html",
        metrics=metrics,
        activities=atividades,
        tipo_solicitacao= tipo_solicitacao,
        prioridades= Prioridades
        
    )
   
@main.route("/api/deleta/<int:atividade_id>", methods=["DELETE"])
def deletar_atividade(atividade_id):

    try:
        # Procura a atividade pelo ID
        atividade = db.session.get(Activity, atividade_id)

        # Verifica se existe
        if not atividade:
            return jsonify({
                "success": False,
                "erro": "Atividade não encontrada"
            }), 404

        # Guarda os dados antes de excluir
        dados = atividade.to_dict()

        # Remove do banco
        db.session.delete(atividade)
        db.session.commit()

        return jsonify({
            "success": True,
            "mensagem": "Atividade excluída com sucesso",
            "dados_excluidos": dados
        }), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "success": False,
            "erro": "Erro ao excluir atividade",
            "detalhes": str(e)
        }), 500

@main.route("/Nova_solicitacao", methods=["GET", "POST"])
def Nova_solicitacao():
    tipo_solicitacao = "Nova"
    if request.method == "POST":

        try:
            # Captura os dados enviados pelo formulário
            subject = request.form.get("subject", "").strip()
            prioridade = request.form.get("prioridade", "").strip()
            

            # Validação
            if not subject:
                return render_template(
                    "nova_solicitacao.html",
                    erro="O tipo de solicitação é obrigatório."
                ), 400

            # Cria a atividade
            atividade = Activity(
                subject=subject,
                prioridade= prioridade,
                status="Pendente",
                status_interno="Pendente"
            )

            # Salva no banco
            db.session.add(atividade)
            db.session.commit()

            # Redireciona para a página de solicitações
            return redirect(url_for("main.filtro"))

        except Exception as e:

            db.session.rollback()

            return render_template(
                "nova_solicitacao.html",
                erro=f"Erro ao cadastrar solicitação: {str(e)}"
            ), 500

    return render_template("nova_solicitacao.html")

  
@main.route("/api/envio", methods=["POST"])
def envio():

    if request.is_json:
        # recebe o conteúdo em json
        dados = request.get_json()
        # modela a atividade pcom base nos dados recebidos, ele procura e atribui ao campo subject o subject que veio e adiciona o  status pendente
        if not dados:
            return jsonify({
                "erro": "Envie um JSON válido"
            }), 400

        subject = dados.get("subject")

        if not subject:
            return jsonify({
                "erro": "O campo subject é obrigatório"
            }), 400
        if dados.get("status"):
            status= dados.get("status")
        if dados.get("resposavel"):
            responsavel = dados.get("responsavel")
        atividade = Activity(
            subject=str(subject),
            status= str(status),
            responsavel= str(responsavel)
        )

        db.session.add(atividade)
        db.session.commit()

    else:
        dados = request.form.to_dict()

    return jsonify({
        "mensagem": "Dados recebidos",
        "dados": atividade.to_dict()
    }), 200


@main.route("/api/atualiza", methods=["PUT"])
def atualizar_status():

    if not request.is_json:
        return jsonify({
            "erro": "O conteúdo deve ser enviado em JSON"
        }), 400

    dados = request.get_json()

    if not dados:
        return jsonify({
            "erro": "Envie um JSON válido"
        }), 400

    # Identifica a atividade que será atualizada
    atividade_id = dados.get("id")

    if not atividade_id:
        return jsonify({
            "erro": "O campo id é obrigatório"
        }), 400

    alteracao = db.session.get(Activity, atividade_id)

    if not alteracao:
        return jsonify({
            "erro": "Atividade não encontrada"
        }), 404

    try:
        # Atualiza somente os campos enviados
        if "subject" in dados:
            alteracao.subject = str(dados["subject"])

        if "status" in dados:
            alteracao.status = dados["status"]

        if "interno" in dados:
            alteracao.status_interno = dados["interno"]

        db.session.commit()

        return jsonify({
            "mensagem": "Atividade atualizada com sucesso",
            "dados": alteracao.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "erro": "Erro ao atualizar atividade",
            "detalhes": str(e)
        }), 500
@main.route("/api/tudo")
def Consulta_total():
    atividades = Activity.query.order_by(
            Activity.id.asc()
        ).all()
    resultado = [
            atividade.to_dict()
            for atividade in atividades
        ]
    return jsonify({
            "success": True,
            "total_registros": len(resultado),
            "dados": resultado
        }), 200
