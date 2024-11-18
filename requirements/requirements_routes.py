from flask import Blueprint, jsonify
from .create_requirements_for_entire_doc import create_requirements_for_entire_doc

requirements_bp = Blueprint('requirements', __name__)

@requirements_bp.route('/create_requirements_for_document/<int:document_id>', methods=['POST'])
def create_requirements_for_document(document_id):
    try:
        result = create_requirements_for_entire_doc(document_id)
        return jsonify({"success": True, "message": result}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400