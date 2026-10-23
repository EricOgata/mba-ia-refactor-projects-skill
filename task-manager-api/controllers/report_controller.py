"""Controllers de relatórios."""

from flask import jsonify

from services.report_service import ReportService


def summary_report():
    return jsonify(ReportService().summary()), 200


def user_report(user_id):
    return jsonify(ReportService().user_report(user_id)), 200
