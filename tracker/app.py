from tracker.common import create_hash, decode_auth_token, encode_auth_token

from tracker.models import User
from tracker.utils import (
    add_expenses,
    add_transactions,
    create_new_user,
    organise_expenses,
    track_balance,
)
from flask import Flask, jsonify, request

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://postgres:passwd@localhost:5432/tracker", echo=True)
Session = sessionmaker(bind=engine)

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/create_user", methods=["POST"])
def create_user():

    args = request.json
    if not args.get("email") or not args.get("name") or not args.get("password"):
        return jsonify({"suucess": False, "message": "Missing required params"}), 400

    # perform email and phone verification here.
    # probably run some checks like length, special characters check, etc.,
    # skipping for now.

    with Session() as session:
        result = create_new_user(
            session=session, user_info=args, secret=args["password"]
        )
        if result["success"]:
            session.commit()

    return jsonify(result), 200


@app.route("/token", methods=["GET"])
def token():

    args = request.args
    if not args.get("email") or not args.get("password"):
        return (
            jsonify({"suucess": False, "message": "Please provide user credentials."}),
            400,
        )

    with Session() as session:
        email = args["email"].strip().lower()
        user = session.query(User).filter(User.email == email).one_or_none()

        if not user:
            return (
                jsonify(
                    {
                        "suucess": False,
                        "message": "User not present in system. Please signup first",
                    }
                ),
                400,
            )

        digest = create_hash(name=user.name, email=user.email, secret=args["password"])
        if user.hash != digest:
            return (
                jsonify(
                    {"success": False, "message": "Invalid user email or password."}
                ),
                400,
            )

        result = encode_auth_token(user_id=user.id)
        return jsonify(result), 200


@app.route("/create_expense", methods=["POST"])
def create_expense():

    access_token = request.headers.get("jwt")
    if not access_token:
        return (
            jsonify(
                {"success": False, "message": "Permission Denied. Token not provided."}
            ),
            400,
        )

    access_response = decode_auth_token(auth_token=access_token)
    if not access_response["success"]:
        return jsonify(access_response), 400

    args = request.json

    merchant = args.get("merchant")
    if not merchant or not merchant.get("name"):
        return (
            jsonify(
                {"success": False, "message": "Merchant Info for expense not provided."}
            ),
            400,
        )

    if not args.get("paid_by") or not args.get("amount"):
        return (
            jsonify({"success": False, "message": "Expense Info not provided."}),
            400,
        )

    parties = args.get("parties")
    if not parties:
        return (
            jsonify({"success": False, "message": "Expense Party Info not provided."}),
            400,
        )

    for party in parties:
        if not party.get("user_id") or not party.get("amount"):
            return (
                jsonify(
                    {"success": False, "message": "Expense Party Info is not valid."}
                ),
                400,
            )

    settlements = args.get("settlements", [])
    for settlement in settlements:
        if not settlement.get("user_id") or not settlement.get("amount"):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Expense Settlement Info is not valid.",
                    }
                ),
                400,
            )

    with Session() as session:
        result = add_expenses(session=session, expense_info=args)
        if result["success"]:
            session.commit()

        return jsonify(result), 200


@app.route("/get_transactions", methods=["GET"])
def get_transactions():

    access_token = request.headers.get("jwt")
    if not access_token:
        return (
            jsonify(
                {"success": False, "message": "Permission Denied. Token not provided."}
            ),
            400,
        )

    access_response = decode_auth_token(auth_token=access_token)
    if not access_response["success"]:
        return jsonify(access_response), 400

    user_id = access_response["data"]["user_id"]
    if not user_id:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "User Info not provided for getting transactions",
                }
            ),
            400,
        )

    with Session() as session:
        result = organise_expenses(session=session, user_id=user_id)
        return jsonify(result), 200


@app.route("/get_expenses", methods=["GET"])
def get_expenses():

    access_token = request.headers.get("jwt")
    if not access_token:
        return (
            jsonify(
                {"success": False, "message": "Permission Denied. Token not provided."}
            ),
            400,
        )

    access_response = decode_auth_token(auth_token=access_token)
    if not access_response["success"]:
        return jsonify(access_response), 400

    user_id = access_response["data"]["user_id"]
    if not user_id:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "User Info not provided for getting transactions",
                }
            ),
            400,
        )

    with Session() as session:
        result = organise_expenses(session=session, user_id=user_id)
        return jsonify(result), 200


@app.route("/track_balance", methods=["GET"])
def get_balance():

    access_token = request.headers.get("jwt")
    if not access_token:
        return (
            jsonify(
                {"success": False, "message": "Permission Denied. Token not provided."}
            ),
            400,
        )

    access_response = decode_auth_token(auth_token=access_token)
    if not access_response["success"]:
        return jsonify(access_response), 400

    user_id = access_response["data"]["user_id"]
    if not user_id:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "User Info not provided for getting balance.",
                }
            ),
            400,
        )

    with Session() as session:
        result = track_balance(session=session, user_id=user_id)
        return jsonify(result), 200


@app.route("/register_payback", methods=["POST"])
def register_payback():

    access_token = request.headers.get("jwt")
    if not access_token:
        return (
            jsonify(
                {"success": False, "message": "Permission Denied. Token not provided."}
            ),
            400,
        )

    access_response = decode_auth_token(auth_token=access_token)
    if not access_response["success"]:
        return jsonify(access_response), 400

    args = request.json

    settlements = args.get("settlements")
    if not settlements:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Settlement Info not provided for registering payback.",
                }
            ),
            400,
        )

    for settlement in settlements:
        if (
            not settlement.get("creditor_id")
            or not settlement.get("amount")
            or not settlement.get("debitor_id")
        ):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Expense Settlement Info is not valid.",
                    }
                ),
                400,
            )

        settlement["type"] = "settlement"

    with Session() as session:
        result = add_transactions(session=session, transactions=settlements)
        session.commit()
        return jsonify(result), 200
