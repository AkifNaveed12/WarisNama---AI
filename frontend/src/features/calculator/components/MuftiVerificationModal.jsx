// src/features/calculator/components/MuftiVerificationModal.jsx
import React, { useState } from 'react';
import toast from 'react-hot-toast';

const MuftiVerificationModal = ({
  isOpen,
  onClose,
  results,         // { shares, tax_results, disputes, sect, debts, funeral, wasiyyat, minor }
  totalEstate,
  distributable,
  generateCertificateBlob   // returns Promise<Blob>
}) => {
  const [muftiEmail, setMuftiEmail] = useState('local.mufti@example.com');
  const [dryRun, setDryRun] = useState(false);   // <-- Default to SEND real email (false)
  const [applicantName, setApplicantName] = useState('');
  const [propertyDescription, setPropertyDescription] = useState('Inherited Property');
  const [legalNoticeIssued, setLegalNoticeIssued] = useState(false);
  const [firIssued, setFirIssued] = useState(false);
  const [legalActionNotes, setLegalActionNotes] = useState('');
  const [sending, setSending] = useState(false);
  const [previewData, setPreviewData] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSending(true);
    setPreviewData(null);

    try {
      // Generate PDF certificate if shares exist
      let certificateBase64 = null;
      if (results?.shares && Object.keys(results.shares).length > 0) {
        const blob = await generateCertificateBlob();
        if (blob) {
          const reader = new FileReader();
          const base64Promise = new Promise((resolve, reject) => {
            reader.onloadend = () => resolve(reader.result.split(',')[1]);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
          });
          certificateBase64 = await base64Promise;
        }
      }

      const payload = {
        results: {
          shares: results.shares,
          tax_results: results.tax_results || {},
          disputes: results.disputes || {},
          sect: results.sect,
          total_estate: totalEstate,
          distributable: distributable,
          debts: results.debts || 0,
          funeral: results.funeral || 0,
          wasiyyat: results.wasiyyat || 0,
          minor: results.minor || false,
        },
        case_details: {
          deceased_name: 'Late Person',
          deceased_father: '[Father]',
          death_date: new Date().toISOString().split('T')[0],
          applicant_name: applicantName || 'Not provided',
          property_description: propertyDescription,
          legal_notice_issued: legalNoticeIssued,
          fir_issued: firIssued,
          legal_action_notes: legalActionNotes,
        },
        recipient_email: muftiEmail,
        dry_run: dryRun,
        certificate_base64: certificateBase64,
        source: 'react_frontend',
      };

      const response = await fetch('http://localhost:8000/api/v1/verify/mufti', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (data.status === 'success') {
        if (dryRun) {
          setPreviewData(data.data);
          toast.success('Verification preview generated. Scroll down to see email content.');
        } else {
          toast.success(`✅ Verification email sent to ${muftiEmail}`);
          onClose();
        }
      } else {
        toast.error(data.detail || 'Verification failed');
      }
    } catch (err) {
      toast.error(err.message);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-bold text-gray-800">🕌 Local Mufti Verification</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Mufti Email</label>
            <input
              type="email"
              value={muftiEmail}
              onChange={(e) => setMuftiEmail(e.target.value)}
              required
              className="w-full border border-gray-200 rounded-xl p-2.5 focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* DRY RUN TOGGLE – CLEAR AND OBVIOUS */}
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <input
              type="checkbox"
              id="dryRun"
              checked={dryRun}
              onChange={(e) => setDryRun(e.target.checked)}
              className="w-5 h-5 rounded text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="dryRun" className="text-sm font-medium text-gray-700">
              Preview only (dry run) – do not send real email
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Applicant Name (optional)</label>
            <input
              type="text"
              value={applicantName}
              onChange={(e) => setApplicantName(e.target.value)}
              className="w-full border border-gray-200 rounded-xl p-2.5"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Property / Assets Description</label>
            <input
              type="text"
              value={propertyDescription}
              onChange={(e) => setPropertyDescription(e.target.value)}
              className="w-full border border-gray-200 rounded-xl p-2.5"
            />
          </div>

          <div className="flex gap-4">
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={legalNoticeIssued} onChange={(e) => setLegalNoticeIssued(e.target.checked)} className="rounded" />
              <span className="text-sm">Legal notice already issued</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={firIssued} onChange={(e) => setFirIssued(e.target.checked)} className="rounded" />
              <span className="text-sm">FIR already issued</span>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
            <textarea
              rows={3}
              value={legalActionNotes}
              onChange={(e) => setLegalActionNotes(e.target.value)}
              className="w-full border border-gray-200 rounded-xl p-2.5"
            />
          </div>

          <button
            type="submit"
            disabled={sending}
            className="w-full bg-gradient-to-r from-purple-700 to-purple-600 text-white py-3 rounded-xl font-medium hover:from-purple-800 hover:to-purple-700 transition-all disabled:opacity-50"
          >
            {sending ? 'Sending...' : (dryRun ? '🔍 Generate Preview' : '📧 Send Verification Request')}
          </button>
        </form>

        {previewData && (
          <div className="border-t border-gray-100 p-6 bg-gray-50 rounded-b-2xl">
            <h3 className="font-bold text-gray-800 mb-2">📧 Email Preview (dry run)</h3>
            <p className="text-sm text-gray-600">To: {previewData.recipient}</p>
            <p className="text-sm text-gray-600 mb-2">Subject: {previewData.subject}</p>
            <pre className="bg-white p-3 rounded-lg text-xs whitespace-pre-wrap border border-gray-200 max-h-96 overflow-auto">
              {previewData.body}
            </pre>
            {previewData.attachments?.length > 0 && (
              <p className="text-sm text-gray-600 mt-2">Attachments: {previewData.attachments.join(', ')}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MuftiVerificationModal;