import os
from app import create_app, db
from app.models import User, PurchasePlan, PurchaseItem, ApprovalFlow, ApprovalStep, ApprovalLog

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    """为 flask shell 添加上下文"""
    return {
        'db': db,
        'User': User,
        'PurchasePlan': PurchasePlan,
        'PurchaseItem': PurchaseItem,
        'ApprovalFlow': ApprovalFlow,
        'ApprovalStep': ApprovalStep,
        'ApprovalLog': ApprovalLog
    }


if __name__ == '__main__':
    app.run(
        host=os.environ.get('FLASK_RUN_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_RUN_PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
