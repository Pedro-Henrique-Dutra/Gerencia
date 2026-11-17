from datetime import datetime, timezone

from . import db

#criação de uma tabela chamada  activities
class Activity(db.Model):

    __tablename__ = "activities"

    # cada variavel vai ser uma linha  e o conteúdo dentro de db.Column será as   colunas
    
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    subject = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Pendente"
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    responsable = db.Column(
        db.String(15),
        default = None
    )

    status_interno = db.Column( 
        db.String(30), 
        nullable=False, 
        default="Pendente"
    )

    prioridade = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    origem = db.Column(
        db.String(30),
        nullable= False,
        default="Site"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "status": self.status,
            "status_interno": self.status_interno,
            "responsavel": self.responsable,
            "prioridade": self.prioridade,
            "origem": self.origem,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at else None
            )
        }
    def __repr__(self):

        return f"<Activity {self.subject}>"
