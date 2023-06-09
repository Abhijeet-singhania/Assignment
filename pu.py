from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        """
        Convert the Task object to a dictionary.
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': str(self.due_date),
            'status': self.status
        }

@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        due_date = data.get('due_date')
        status = data.get('status')

        # Input validation
        if not title:
            return jsonify({'error': 'Title is required.'}), 400

        if status not in ['Incomplete', 'In Progress', 'Completed']:
            return jsonify({'error': 'Invalid status value.'}), 400

        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            status=status
        )
        db.session.add(task)
        db.session.commit()

        return jsonify({'message': 'Task created successfully.'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while creating the task.'}), 500

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get(task_id)
    if task:
        return jsonify(task.to_dict())
    else:
        return jsonify({'error': 'Task not found.'}), 404

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found.'}), 404

        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        due_date = data.get('due_date')
        status = data.get('status')

        # Input validation
        if not title:
            return jsonify({'error': 'Title is required.'}), 400

        if status and status not in ['Incomplete', 'In Progress', 'Completed']:
            return jsonify({'error': 'Invalid status value.'}), 400

        task.title = title
        task.description = description
        task.due_date = due_date
        task.status = status
        db.session.commit()

        return jsonify({'message': 'Task updated successfully.'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while updating the task.'}), 500

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task = Task.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
            return jsonify({'message': 'Task deleted successfully.'})
        else:
            return jsonify({'error': 'Task not found.'}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while deleting the task.'}), 500

@app.route('/tasks', methods=['GET'])
def list_tasks():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        tasks = Task.query.paginate(page=page, per_page=per_page)
        task_list = [task.to_dict() for task in tasks.items]
        return jsonify(task_list)
    except SQLAlchemyError as e:
        return jsonify({'error': 'An error occurred while retrieving the tasks.'}), 500

if __name__ == '__main__':
    db.create_all()
    app.run()
