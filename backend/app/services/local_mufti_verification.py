import base64
import os
import smtplib
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_MUFTI_EMAIL = "local.mufti@example.com"


@dataclass(frozen=True)
class EmailConfig:
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    sender_email: str
    use_tls: bool = True

    @classmethod
    def from_env(cls) -> Optional["EmailConfig"]:
        host = os.getenv("SMTP_HOST", "").strip()
        username = os.getenv("SMTP_USERNAME", "").strip()
        password = os.getenv("SMTP_PASSWORD", "").strip().replace(" ", "")
        sender = os.getenv("SMTP_SENDER_EMAIL", username).strip()

        if not all([host, username, password, sender]):
            return None

        return cls(
            smtp_host=host,
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_username=username,
            smtp_password=password,
            sender_email=sender,
            use_tls=os.getenv("SMTP_USE_TLS", "true").lower() != "false",
        )


class MuftiVerificationError(RuntimeError):
    pass


def build_verification_payload(
    results: Dict[str, Any],
    case_details: Optional[Dict[str, Any]] = None,
    source: str = "system",
) -> Dict[str, Any]:
    """
    Convert Streamlit/API calculation output into a stable verification payload.
    This function does not mutate the existing backend result contract.
    """
    if not isinstance(results, dict) or not results.get("shares"):
        raise ValueError("results must contain a non-empty 'shares' dictionary")

    case_details = case_details or {}
    shares = results.get("shares", {})
    tax_results = results.get("tax_results", {})
    disputes = results.get("disputes", {})

    return {
        "verification_id": f"WN-MUFTI-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": source,
        "case_details": case_details,
        "calculation": {
            "sect": results.get("sect", "hanafi"),
            "total_estate": _to_number(results.get("total_estate")),
            "distributable": _to_number(results.get("distributable") or results.get("distributable_estate")),
            "debts": _to_number(results.get("debts")),
            "funeral": _to_number(results.get("funeral")),
            "wasiyyat": _to_number(results.get("wasiyyat")),
            "minor_heir_present": bool(results.get("minor", False)),
            "shares": shares,
            "tax_results": tax_results,
            "disputes": disputes,
        },
        "references": _collect_references(shares, disputes, results.get("sect", "hanafi")),
    }


def build_mufti_email(
    payload: Dict[str, Any],
    recipient_email: str = DEFAULT_MUFTI_EMAIL,
    certificate_pdf: Optional[bytes] = None,
    certificate_filename: str = "share_certificate.pdf",
) -> EmailMessage:
    recipient_email = (recipient_email or DEFAULT_MUFTI_EMAIL).strip()
    if "@" not in recipient_email:
        raise ValueError("recipient_email must be a valid email address")

    subject = f"WarisNama AI Mufti Verification Request - {payload['verification_id']}"
    body = _render_email_body(payload)

    msg = EmailMessage()
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg["From"] = os.getenv("SMTP_SENDER_EMAIL", "warisnama-ai@example.com")
    msg.set_content(body)

    if certificate_pdf:
        msg.add_attachment(
            certificate_pdf,
            maintype="application",
            subtype="pdf",
            filename=certificate_filename or "share_certificate.pdf",
        )

    return msg


def send_mufti_verification_email(
    payload: Dict[str, Any],
    recipient_email: str = DEFAULT_MUFTI_EMAIL,
    certificate_pdf: Optional[bytes] = None,
    dry_run: bool = True,
    email_config: Optional[EmailConfig] = None,
) -> Dict[str, Any]:
    """
    Build and optionally send the mufti verification email.
    dry_run=True returns the composed email without connecting to SMTP.
    """
    msg = build_mufti_email(payload, recipient_email, certificate_pdf)

    if dry_run:
        return {
            "status": "preview",
            "verification_id": payload["verification_id"],
            "recipient": recipient_email,
            "subject": msg["Subject"],
            "body": _plain_text_body(msg),
            "attachments": _attachment_names(msg),
        }

    config = email_config or EmailConfig.from_env()
    if config is None:
        raise MuftiVerificationError(
            "SMTP is not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USERNAME, "
            "SMTP_PASSWORD, and SMTP_SENDER_EMAIL or use dry_run=True."
        )

    msg.replace_header("From", config.sender_email)
    try:
        with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=30) as smtp:
            if config.use_tls:
                smtp.starttls()
            smtp.login(config.smtp_username, config.smtp_password)
            smtp.send_message(msg)
    except Exception as exc:
        raise MuftiVerificationError(f"Unable to send verification email: {exc}") from exc

    return {
        "status": "sent",
        "verification_id": payload["verification_id"],
        "recipient": recipient_email,
        "subject": msg["Subject"],
        "attachments": _attachment_names(msg),
    }


def decode_certificate_base64(value: Optional[str]) -> Optional[bytes]:
    if not value:
        return None
    try:
        return base64.b64decode(value, validate=True)
    except Exception as exc:
        raise ValueError("certificate_base64 must be valid base64 PDF bytes") from exc


def _render_email_body(payload: Dict[str, Any]) -> str:
    case = payload.get("case_details", {})
    calc = payload.get("calculation", {})
    shares = calc.get("shares", {})
    disputes = calc.get("disputes", {})
    tax_results = calc.get("tax_results", {})
    references = payload.get("references", [])

    lines = [
        "Assalamu Alaikum wa Rahmatullah,",
        "",
        "A WarisNama AI user has requested independent local mufti verification of an inheritance calculation.",
        "Please review the faraid distribution, deductions, dispute indicators, and attached/share-certificate evidence where provided.",
        "",
        "CASE META",
        f"- Verification ID: {payload.get('verification_id')}",
        f"- Created at UTC: {payload.get('created_at_utc')}",
        f"- Input source: {payload.get('source')}",
        "",
        "PARTIES AND USER PROVIDED DETAILS",
        f"- Deceased name: {case.get('deceased_name', 'Not provided')}",
        f"- Deceased father/husband: {case.get('deceased_father', 'Not provided')}",
        f"- Date of death: {case.get('death_date', 'Not provided')}",
        f"- Applicant/requesting heir: {case.get('applicant_name', 'Not provided')}",
        f"- Applicant CNIC/contact: {case.get('applicant_cnic', 'Not provided')} / {case.get('applicant_contact', 'Not provided')}",
        f"- Property/assets description: {case.get('property_description', 'Inherited Property / not separately provided')}",
        "",
        "INHERITANCE CALCULATION SUMMARY",
        f"- Maslak/religious law selected: {str(calc.get('sect', 'hanafi')).title()}",
        f"- Gross estate: PKR {_fmt_money(calc.get('total_estate'))}",
        f"- Debts payable before distribution: PKR {_fmt_money(calc.get('debts'))}",
        f"- Funeral expenses: PKR {_fmt_money(calc.get('funeral'))}",
        f"- Wasiyyat/bequest considered: PKR {_fmt_money(calc.get('wasiyyat'))}",
        f"- Distributable estate after deductions: PKR {_fmt_money(calc.get('distributable'))}",
        f"- Minor heir present: {'Yes' if calc.get('minor_heir_present') else 'No'}",
        "",
        "PROPOSED WARSA SHARES",
    ]

    for heir_id, data in shares.items():
        tax = tax_results.get(heir_id, {})
        lines.append(
            f"- {heir_id.replace('_', ' ').title()}: "
            f"{data.get('fraction', 'N/A')} = PKR {_fmt_money(data.get('amount'))}; "
            f"reference: {data.get('reference', 'system calculation reference not provided')}; "
            f"net after sale tax estimate: PKR {_fmt_money(tax.get('net_after_all_taxes', data.get('amount')))}"
        )

    lines.extend(["", "DISPUTE / FRAUD INDICATORS"])
    if disputes and disputes.get("total_patterns_detected", 0):
        lines.append(f"- Total detected patterns: {disputes.get('total_patterns_detected')}")
        for item in disputes.get("disputes", []):
            lines.append(
                f"- {item.get('pattern', 'dispute').replace('_', ' ').title()}: "
                f"fraud score {item.get('fraud_score', 'N/A')}; "
                f"court/remedy: {item.get('court', 'N/A')} / {item.get('remedy', 'N/A')}; "
                f"law sections: {item.get('law_sections', {})}"
            )
    else:
        lines.append("- No dispute/fraud pattern was detected by the system.")

    if case.get("legal_notice_issued") or case.get("fir_issued"):
        lines.extend([
            "",
            "LEGAL NOTICE / FIR STATUS",
            f"- Legal notice issued: {'Yes' if case.get('legal_notice_issued') else 'No'}",
            f"- FIR issued: {'Yes' if case.get('fir_issued') else 'No'}",
            f"- Notes: {case.get('legal_action_notes', 'Not provided')}",
        ])

    lines.extend([
        "",
        "CALCULATION APPROACH FOR REVIEW",
        "- Debts and funeral expenses are deducted before mirath distribution.",
        "- Wasiyyat is treated as payable before heirs only within the recognized one-third limit unless heirs consent.",
        "- For Hanafi/Shia cases, spouse/parents/children shares are calculated by fixed shares and residue/asaba logic as implemented by WarisNama AI.",
        "- Tax entries are only sale/transfer estimates and are not treated as inheritance shares.",
        "",
        "REFERENCES RECORDED BY SYSTEM",
    ])
    lines.extend([f"- {ref}" for ref in references] or ["- No explicit references were emitted by the calculation engine."])

    lines.extend([
        "",
        "REQUEST",
        "Kindly verify whether the proposed faraid shares and treatment of deductions/disputes are Shariah-compliant for the facts above.",
        "Please identify any missing heirs, blocked heirs (mahjub), invalid hiba/wasiyyat assumptions, debt priority issues, or documentation concerns.",
        "",
        "JazakAllah Khair,",
        "WarisNama AI Verification Automation",
        "",
        "Disclaimer: This is an automated request for scholarly verification, not a legal fatwa by the software.",
    ])
    return "\n".join(lines)


def _collect_references(shares: Dict[str, Any], disputes: Dict[str, Any], sect: str) -> List[str]:
    refs = []
    for item in shares.values():
        reference = item.get("reference")
        if reference and reference not in refs:
            refs.append(reference)

    for dispute in (disputes or {}).get("disputes", []):
        law_sections = dispute.get("law_sections")
        if law_sections and str(law_sections) not in refs:
            refs.append(str(law_sections))

    if sect == "hanafi":
        refs.append("Hanafi faraid rules: fixed Quranic shares plus residue/asaba distribution.")
    elif sect == "shia":
        refs.append("Shia Jafari inheritance treatment as selected by the user/system.")
    elif sect == "christian":
        refs.append("Succession Act 1925 rules as selected by the user/system.")
    elif sect == "hindu":
        refs.append("Hindu Succession Act 1956 Class I handling as selected by the user/system.")

    return _dedupe(refs)


def _dedupe(values: Iterable[str]) -> List[str]:
    seen = set()
    output = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            output.append(text)
    return output


def _attachment_names(msg: EmailMessage) -> List[str]:
    names = []
    for part in msg.iter_attachments():
        filename = part.get_filename()
        if filename:
            names.append(filename)
    return names


def _plain_text_body(msg: EmailMessage) -> str:
    if not msg.is_multipart():
        return msg.get_content()

    body = msg.get_body(preferencelist=("plain",))
    if body is None:
        return ""
    return body.get_content()


def _to_number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _fmt_money(value: Any) -> str:
    return f"{_to_number(value):,.0f}"
