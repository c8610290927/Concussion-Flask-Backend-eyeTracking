from api.utils.database import db, ma

class User(db.Model):
    __tablename__ = 'User'
    username = db.Column(db.String(100), primary_key=True, nullable=False)
    password = db.Column(db.String(100), primary_key=True, nullable=False)

    def __init__(self, gameid, username, password):
        self.username = username
        self.password = password

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<Post %r data>' % self.username


class UserSchema(ma.SQLAlchemyAutoSchema):
    """
    SQLAlchemySchema automatically generates fields
    """

    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True
