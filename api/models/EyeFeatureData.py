from api.utils.database import db, ma

class EyeTrackingFeature(db.Model):
    __tablename__ = 'EyeTrackingFeatureData'
    uid = db.Column(db.BIGINT, primary_key=True, nullable=False)
    gameid = db.Column(db.String(100), nullable=False)
    sessionid = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    tracking_dist = db.Column(db.Float, nullable=False)
    game_time = db.Column(db.Float, nullable=False)
    tracking_speed = db.Column(db.Float, nullable=False)
    wink_left = db.Column(db.Float, nullable=False)
    wink_right = db.Column(db.Float, nullable=False)

    def __init__(self, gameid, sessionid, username, tracking_dist, game_time, tracking_speed, wink_left, wink_right):
        self.gameid = gameid
        self.sessionid = sessionid
        self.username = username
        self.tracking_dist = tracking_dist
        self.game_time = game_time
        self.tracking_speed = tracking_speed
        self.wink_left = wink_left
        self.wink_right = wink_right

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __repr__(self):
        return '<Post %r data>' % self.username


class EyeTrackingFeatureSchema(ma.SQLAlchemyAutoSchema):
    """
    SQLAlchemySchema automatically generates fields
    """
    class Meta:
        model = EyeTrackingFeature
        sqla_session = db.session
        load_instance = True

