from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pulp

# 1. Initialize the Flask Application
app = Flask(__name__)

# --- Database Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Models ---
class InvestmentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    budget = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<User {self.user_name}>'

# --- In-Memory Data for Cybersecurity Controls ---
# In a real application, this would come from your database.
CYBER_CONTROLS = [
    {"id": "c1", "name": "Advanced Endpoint Protection (EDR)", "cost": 40000, "risk_reduction": 25},
    {"id": "c2", "name": "Security Awareness Training", "cost": 15000, "risk_reduction": 18},
    {"id": "c3", "name": "Network Firewall Upgrade", "cost": 45000, "risk_reduction": 22},
    {"id": "c4", "name": "Multi-Factor Authentication (MFA)", "cost": 25000, "risk_reduction": 30},
    {"id": "c5", "name": "Data Encryption", "cost": 30000, "risk_reduction": 20},
    {"id": "c6", "name": "Vulnerability Management Program", "cost": 50000, "risk_reduction": 28},
    {"id": "c7", "name": "Incident Response Retainer", "cost": 20000, "risk_reduction": 15},
    {"id": "c8", "name": "Cloud Access Security Broker (CASB)", "cost": 35000, "risk_reduction": 19}
]


# --- Web Page Routes ---

@app.route('/')
def home():
    return render_template('index.html')


# --- RESTful API Routes ---

@app.route('/api/v1/optimize', methods=['POST'])
def optimize_portfolio():
    """
    API endpoint to handle investment optimization with PuLP.
    """
    # 1. Get budget from the user's request
    data = request.json
    budget = data.get('budget', 100000)

    # 2. Set up the Optimization Problem
    problem = pulp.LpProblem("Cybersecurity_Portfolio_Optimization", pulp.LpMaximize)

    # 3. Define Decision Variables
    # Create a dictionary of binary variables, one for each control.
    # The variable will be 1 if the control is chosen, 0 otherwise.
    control_vars = pulp.LpVariable.dicts("Control", [c['id'] for c in CYBER_CONTROLS], cat='Binary')

    # 4. Define the Objective Function
    # We want to maximize the total risk reduction score.
    problem += pulp.lpSum([c['risk_reduction'] * control_vars[c['id']] for c in CYBER_CONTROLS]), "Total_Risk_Reduction"

    # 5. Define the Constraint
    # The total cost of selected controls must not exceed the budget.
    problem += pulp.lpSum([c['cost'] * control_vars[c['id']] for c in CYBER_CONTROLS]) <= budget, "Budget_Constraint"

    # 6. Solve the Problem
    problem.solve()

    # 7. Process the Results
    recommended_investments = []
    total_cost = 0
    total_risk_reduction = 0

    for control in CYBER_CONTROLS:
        # Check if the control was selected by the solver
        if control_vars[control['id']].varValue == 1:
            recommended_investments.append({
                'control': control['name'],
                'cost': control['cost'],
                'risk_reduction': control['risk_reduction'] / 100 # Convert back to percentage for display
            })
            total_cost += control['cost']
            total_risk_reduction += control['risk_reduction']

    response_data = {
        'status': 'success',
        'investments': recommended_investments,
        'total_cost': total_cost,
        'projected_risk_reduction': total_risk_reduction / 100, # Convert back to percentage for display
        'message': f'Optimization complete. Found {len(recommended_investments)} optimal investments within the budget.'
    }

    return jsonify(response_data)


# --- Main execution ---

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)