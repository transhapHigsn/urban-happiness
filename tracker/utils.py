from tracker.common import create_hash, encode_auth_token
from sqlalchemy.sql.expression import case, or_
from tracker.models import ExpenseParties, Expenses, Merchant, User, UserTransaction


def track_balance(session, user_id):
    rows = (
        session.query(
            case(
                (
                    UserTransaction.creditor_user_id == user_id,
                    UserTransaction.txn_amount,
                ),
                (
                    UserTransaction.debitor_user_id == user_id,
                    UserTransaction.txn_amount * -1,
                ),
                else_=0,
            ).label("amount")
        )
        .filter(
            or_(
                UserTransaction.creditor_user_id == user_id,
                UserTransaction.debitor_user_id == user_id,
            ),
            UserTransaction.is_active,
        )
        .all()
    )

    balance = sum(row["amount"] for row in rows)
    return {
        "success": True,
        "data": {
            "balance": float(balance),
        },
        "message": "Balance fetched successfully",
    }


def organise_expenses(session, user_id):
    rows = (
        session.query(
            UserTransaction.id,
            UserTransaction.creditor_user_id,
            UserTransaction.debitor_user_id,
            UserTransaction.type,
            UserTransaction.created_at,
            UserTransaction.updated_at,
            UserTransaction.description,
            case(
                (
                    UserTransaction.creditor_user_id == user_id,
                    UserTransaction.txn_amount,
                ),
                (
                    UserTransaction.debitor_user_id == user_id,
                    UserTransaction.txn_amount * -1,
                ),
                else_=0,
            ).label("amount"),
            UserTransaction.expense_id,
            Expenses.txn_amount,
        )
        .outerjoin(Expenses, Expenses.id == UserTransaction.expense_id)
        .filter(
            or_(
                UserTransaction.creditor_user_id == user_id,
                UserTransaction.debitor_user_id == user_id,
            ),
            UserTransaction.is_active,
        )
        .order_by(UserTransaction.created_at.desc())
        .all()
    )

    txns = []
    for (
        txn_id,
        creditor_user_id,
        debitor_user_id,
        type,
        created_at,
        updated_at,
        description,
        amount,
        expense_id,
        expense_amount,
    ) in rows:
        txns.append(
            {
                "creditor_user_id": creditor_user_id,
                "debitor_user_id": debitor_user_id,
                "amount": float(amount),
                "created_at": created_at.isoformat(),
                "updated_at": updated_at.isoformat(),
                "description": description,
                "txn_id": txn_id,
                "type": type,
                "expense_id": expense_id,
                "expense_amount": float(expense_amount),
            }
        )

    return {
        "success": True,
        "data": {"transactions": txns},
        "message": "Transaction info fetched successfully.",
    }


def add_expenses(session, expense_info):
    """
    expense_amount
    parties_involved
    {
        a: 100,
        b: 200
    }
    merchant_info

    """

    merchant_name = expense_info["merchant"]["name"].strip().lower()
    merchant = (
        session.query(Merchant).filter(Merchant.name == merchant_name).one_or_none()
    )

    if not merchant:
        merchant = Merchant(name=merchant_name)
        session.add(merchant)
        session.flush()

    expense = Expenses(
        user_id=expense_info["paid_by"],
        txn_amount=expense_info["amount"],
        merchant_id=merchant.id,
        description=expense_info.get("description"),
    )
    session.add(expense)
    session.flush()

    parties = expense_info["parties"]
    for party in parties:
        expense_party = ExpenseParties(
            amount=party["amount"], expense_id=expense.id, user_id=party["user_id"]
        )
        session.add(expense_party)
        txn = UserTransaction(
            creditor_user_id=expense_info["paid_by"],
            debitor_user_id=party["user_id"],
            type="expense",
            txn_amount=party["amount"],
            description="expense into description",
            expense_id=expense.id,
        )
        session.add(txn)

    settlements = expense_info.get("settlements", [])
    for settlement in settlements:
        txn = UserTransaction(
            creditor_user_id=settlement["user_id"],
            debitor_user_id=expense_info["paid_by"],
            type="settlement",
            txn_amount=settlement["amount"],
            description="settlement of expense",
            expense_id=expense.id,
        )
        session.add(txn)

    return {
        "success": True,
        "data": {"expense_id": expense.id},
        "message": "Expense added successfully.",
    }


def add_transactions(session, transactions):
    for txn in transactions:
        txn_entry = UserTransaction(
            creditor_user_id=txn["creditor_id"],
            debitor_user_id=txn["debitor_id"],
            type=txn["type"],
            txn_amount=txn["amount"],
            description=txn.get("description", "adding transaction"),
        )
        session.add(txn_entry)

    return {"success": True, "data": {}, "message": "Transactions added successfully."}


def create_new_user(session, user_info, secret):
    email = user_info["email"].strip().lower()
    existing_user = session.query(User).filter(User.email == email).one_or_none()
    if existing_user:
        return {"success": False, "message": "User already exists."}

    name = user_info["name"].strip().lower()
    digest = create_hash(name=name, email=email, secret=secret)

    user = User(email=email, name=name, phone=user_info.get("phone"), hash=digest)
    session.add(user)
    session.flush()

    access_token = encode_auth_token(user_id=user.id)

    return {
        "success": True,
        "message": "User added successfully.",
        "data": {
            "user_id": user.id,
            "access_token": access_token["data"]["access_token"],
        },
    }
