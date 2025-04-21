from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(1000), nullable=False)
    response = db.Column(db.String(1000), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'response': self.response,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

class Node(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Float, default=1.0)
    color = db.Column(db.String(20), default="#B290D6")  # Default to purple
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'label': self.label,
            'size': self.size,
            'color': self.color
        }

class Edge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('node.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('node.id'), nullable=False)
    weight = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    source = db.relationship('Node', foreign_keys=[source_id], backref='outgoing_edges')
    target = db.relationship('Node', foreign_keys=[target_id], backref='incoming_edges')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'source': str(self.source_id),
            'target': str(self.target_id),
            'weight': self.weight
        } 