# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configurare bază de date
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///links.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model pentru Link-uri
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'created_at': self.created_at.isoformat()
        }

# Rute API
@app.route('/api/links', methods=['GET'])
def get_links():
    category = request.args.get('category')
    if category:
        links = Link.query.filter_by(category=category).all()
    else:
        links = Link.query.all()
    return jsonify([link.to_dict() for link in links])

@app.route('/api/links', methods=['POST'])
def create_link():
    data = request.json
    new_link = Link(
        url=data['url'],
        title=data.get('title'),
        description=data.get('description'),
        category=data.get('category')
    )
    db.session.add(new_link)
    db.session.commit()
    return jsonify(new_link.to_dict()), 201

@app.route('/api/links/<int:link_id>', methods=['PUT'])
def update_link(link_id):
    link = Link.query.get_or_404(link_id)
    data = request.json
    link.url = data.get('url', link.url)
    link.title = data.get('title', link.title)
    link.description = data.get('description', link.description)
    link.category = data.get('category', link.category)
    db.session.commit()
    return jsonify(link.to_dict())

@app.route('/api/links/<int:link_id>', methods=['DELETE'])
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5040, debug=True)
