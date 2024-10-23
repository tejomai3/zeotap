from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from models import Base, Rule, engine
from utils import Node, parse_rule_string, validate_rule_string
import json
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create a new session
Session = sessionmaker(bind=engine)
session = Session()

# Define a catalog of valid attributes for validation
VALID_ATTRIBUTES = ['age', 'income', 'experience']

@app.route('/create_rule', methods=['POST'])
def create_rule():
    try:
        rule_string = request.json['rule_string']
        # Validate the rule before parsing
        if not validate_rule_string(rule_string, VALID_ATTRIBUTES):
            return jsonify({'error': 'Invalid rule format or attributes'}), 400
        ast = parse_rule_string(rule_string)
        rule = Rule(rule_string=rule_string, ast=json.dumps(ast.to_dict()))
        session.add(rule)
        session.commit()
        return jsonify({'id': rule.id, 'ast': rule.ast})
    except Exception as e:
        logging.error(f"Error creating rule: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/combine_rules', methods=['POST'])
def combine_rules():
    try:
        rule_ids = request.json['rule_ids']
        rules = session.query(Rule).filter(Rule.id.in_(rule_ids)).all()
        if not rules:
            return jsonify({'error': 'Rules not found'}), 404
        combined_ast = Node('operator', 'AND', *[Node.from_dict(json.loads(rule.ast)) for rule in rules])
        combined_rule_string = " AND ".join([rule.rule_string for rule in rules])
        combined_rule = Rule(rule_string=combined_rule_string, ast=json.dumps(combined_ast.to_dict()))
        session.add(combined_rule)
        session.commit()
        return jsonify({'id': combined_rule.id, 'combined_ast': json.dumps(combined_ast.to_dict())})
    except Exception as e:
        logging.error(f"Error combining rules: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule():
    try:
        rule_id = request.json['rule_id']
        rule = session.query(Rule).filter_by(id=rule_id).first()
        if not rule:
            return jsonify({'error': 'Rule not found'}), 404
        ast = Node.from_dict(json.loads(rule.ast))
        data = request.json['data']
        result = evaluate_ast(ast, data)
        return jsonify({'result': result})
    except Exception as e:
        logging.error(f"Error evaluating rule: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/modify_rule', methods=['POST'])
def modify_rule():
    try:
        rule_id = request.json['rule_id']
        modifications = request.json.get('modifications', {})
        rule = session.query(Rule).filter_by(id=rule_id).first()
        if not rule:
            return jsonify({'error': 'Rule not found'}), 404

        ast = Node.from_dict(json.loads(rule.ast))

        # Modify the AST based on the input
        for field, value in modifications.items():
            if field == 'operator':
                ast.value = value
            elif field == 'left_value':
                ast.left.value = value
            elif field == 'right_value':
                ast.right.value = value
        
        # Update the rule in the database
        rule.ast = json.dumps(ast.to_dict())
        session.commit()
        return jsonify({'message': 'Rule modified successfully', 'modified_ast': rule.ast})
    except Exception as e:
        logging.error(f"Error modifying rule: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
