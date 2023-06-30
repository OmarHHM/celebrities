from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class BotModel(db.Model):
    __tablename__ = 'bots'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    telegram_token = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    voice_id = db.Column(db.String(255), nullable=False)
    voice_key = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update_status(self, new_status):
        self.status = new_status
        db.session.commit()

    @classmethod
    def from_dict(cls, data):
        return cls(
            telegram_token=data.get('telegram_token'),
            name=data.get('name'),
            voice_id=data.get('voice_id'),
            voice_key=data.get('voice_key'),
            status=data.get('status')
        )

    @classmethod
    def get_bot_by_name(cls, bot_name):
        return cls.query.filter_by(name=bot_name).first()

    @classmethod
    def get_bot_by_id(cls, bot_id):
        return cls.query.get(bot_id)

    @classmethod
    def get_bot_by_token(cls, telegram_token):
        return cls.query.filter_by(telegram_token=telegram_token).first()
