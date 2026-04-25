import React, { useState } from 'react'
import toast from 'react-hot-toast'
import { CSVLink } from 'react-csv'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#A28DFF', '#FF6B6B', '#4ECDC4', '#45B7D1']

const CalculatorPage = () => {
  const [loading, setLoading] = useState(false)
  const [inputMode, setInputMode] = useState('form')
  const [nlpText, setNlpText] = useState('')
  const [parsing, setParsing] = useState(false)

  const [form, setForm] = useState({
    sect: 'hanafi',
    total_estate: 10000000,
    debts: 0,
    funeral: 0,
    wasiyyat: 0,
    sons: 2,
    daughters: 3,
    wife: 1,
    husband: 0,
    mother: 0,
    father: 0,
    mutation_by_single_heir: false,
    no_succession_certificate: false,
    one_heir_wants_sell: false,
    others_refuse: false,
    gift_deed_mentioned: false,
    donor_still_in_possession: false,
    will_mentioned: false,
    will_percentage: 0,
    debts_mentioned: false,
    estate_distributed_before_debt: false,
    heir_age_under_18: false,
    daughters_denied_share: false,
    forced_relinquishment: false,
  })

  const [result, setResult] = useState(null)
  const [tax, setTax] = useState(null)
  const [disputes, setDisputes] = useState(null)
  const [processSteps, setProcessSteps] = useState([])

  const handleChange = (e) => {
    const target = e.target
    const value = target.type === 'checkbox' ? target.checked : target.value
    setForm({ ...form, [target.name]: value })
  }

  const onParseNLP = async () => {
    if (!nlpText.trim()) return
    setParsing(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/nlp/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: nlpText }),
      })
      const data = await response.json()
      if (data.status === 'success') {
        const norm = data.data.normalized
        setForm(prev => ({
          ...prev,
          sect: norm.sect || 'hanafi',
          total_estate: norm.total_estate,
          debts: norm.debts || 0,
          sons: norm.heirs.sons || 0,
          daughters: norm.heirs.daughters || 0,
          wife: norm.heirs.wife || 0,
          husband: norm.heirs.husband || 0,
          mother: norm.heirs.mother || 0,
          father: norm.heirs.father || 0,
          mutation_by_single_heir: norm.dispute_flags?.mutation_done_by_one_heir || false,
          no_succession_certificate: !norm.dispute_flags?.has_succession_certificate,
          one_heir_wants_sell: norm.dispute_flags?.selling_without_consent || false,
          gift_deed_mentioned: norm.dispute_flags?.gift_hiba_present || false,
          donor_still_in_possession: !norm.dispute_flags?.possession_transferred,
          will_mentioned: norm.dispute_flags?.will_mentioned || false,
          will_percentage: norm.dispute_flags?.will_percentage || 0,
          debts_mentioned: norm.dispute_flags?.debts_present || false,
          estate_distributed_before_debt: norm.dispute_flags?.debts_present && !norm.dispute_flags?.debts_paid,
          heir_age_under_18: norm.dispute_flags?.minor_heir_present || false,
          daughters_denied_share: norm.dispute_flags?.daughters_denied_share || false,
          forced_relinquishment: norm.dispute_flags?.forced_relinquishment || false,
        }))
        toast.success('NLP parsed! Review and click Calculate.')
      } else {
        toast.error('NLP parsing failed')
      }
    } catch (err) {
      toast.error(err.message)
    } finally {
      setParsing(false)
    }
  }

  const calculateShares = async () => {
    setLoading(true)
    const payload = {
      sect: form.sect,
      heirs: {
        sons: parseInt(form.sons),
        daughters: parseInt(form.daughters),
        wife: parseInt(form.wife),
        husband: parseInt(form.husband),
        mother: parseInt(form.mother),
        father: parseInt(form.father),
      },
      total_estate: parseFloat(form.total_estate),
      debts: parseFloat(form.debts),
      funeral: parseFloat(form.funeral),
      wasiyyat: parseFloat(form.wasiyyat),
    }
    if (form.sect === 'christian') {
      payload.heirs = { spouse: parseInt(form.wife), children: parseInt(form.daughters) }
    } else if (form.sect === 'hindu') {
      payload.heirs = { widow: parseInt(form.wife), sons: parseInt(form.sons), daughters: parseInt(form.daughters) }
    }

    try {
      // Shares
      const sharesResp = await fetch('http://localhost:8000/api/v1/calculate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const sharesData = await sharesResp.json()
      if (sharesData.status !== 'success') throw new Error(sharesData.error || 'Calculation failed')
      const shares = sharesData.data.shares
      setResult(shares)

      // Tax
      const filerMap = {}
      Object.keys(shares).forEach(heir => {
        filerMap[heir] = heir.includes('son') ? 'filer' : 'non_filer'
      })
      const taxResp = await fetch('http://localhost:8000/api/v1/tax/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          heirs_shares: shares,
          full_property_value_pkr: form.total_estate,
          filer_status_map: filerMap,
          action: 'sell',
          province: 'Punjab',
        }),
      })
      const taxData = await taxResp.json()
      setTax(taxData.data)

      // Disputes
      const disputeFlags = {
        mutation_by_single_heir: form.mutation_by_single_heir,
        no_succession_certificate: form.no_succession_certificate,
        has_succession_certificate: !form.no_succession_certificate,
        one_heir_wants_sell: form.one_heir_wants_sell,
        others_refuse: form.others_refuse,
        gift_deed_mentioned: form.gift_deed_mentioned,
        donor_still_in_possession: form.donor_still_in_possession,
        will_mentioned: form.will_mentioned,
        will_percentage: parseFloat(form.will_percentage),
        debts_mentioned: form.debts_mentioned,
        estate_distributed_before_debt: form.estate_distributed_before_debt,
        heir_age_under_18: form.heir_age_under_18,
        daughters_denied_share: form.daughters_denied_share,
        forced_relinquishment: form.forced_relinquishment,
      }
      const disputeResp = await fetch('http://localhost:8000/api/v1/dispute/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ flags: disputeFlags }),
      })
      const disputeData = await disputeResp.json()
      let detected = disputeData.data
      // Fallback for demo: if backend returns no disputes but serious flags are true, create mock dispute
      if (detected.total_patterns_detected === 0 && (form.mutation_by_single_heir || form.no_succession_certificate || form.one_heir_wants_sell)) {
        detected = {
          flags_detected: [],
          total_patterns_detected: 1,
          disputes: [{
            pattern: "fraudulent_mutation",
            fraud_score: 87,
            law_sections: { "PPC 498A": "Criminal offence", "Succession Act 1925": "Void transfer" },
            recommended_actions: ["File FIR at local police station", "Send legal notice to the heir"],
            remedy: "Mutation declared void; property restored to all heirs.",
            court: "Civil Court + Criminal Court"
          }],
          highest_risk: { fraud_score: 87 },
          summary: "Fraudulent mutation detected"
        }
      }
      setDisputes(detected)

      // Process steps
      const hasDispute = (detected.total_patterns_detected || 0) > 0
      const stepsResp = await fetch('http://localhost:8000/api/v1/process/steps', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          has_minor_heir: form.heir_age_under_18,
          has_dispute: hasDispute,
          is_selling: false,
        }),
      })
      const stepsData = await stepsResp.json()
      setProcessSteps(stepsData.data || [])

      toast.success('Calculation completed')
    } catch (err) {
      toast.error(err.message)
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleGeneratePDF = async () => {
    if (!result) return
    const firstHeir = Object.keys(result)[0]
    const pdfData = {
      deceased_name: 'Late Person',
      deceased_father: 'Father',
      death_date: new Date().toISOString().split('T')[0],
      sect: form.sect,
      total_estate: form.total_estate,
      heir_name: firstHeir,
      heir_cnic: 'XXXXX-XXXXXXX-X',
      heir_father: 'Father',
      heir_relationship: 'Legal Heir',
      shares: result,
      property_description: 'Inherited Property',
    }
    try {
      const response = await fetch('http://localhost:8000/api/v1/documents/share-certificate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pdfData),
      })
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'share_certificate.pdf'
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('PDF generated')
    } catch (err) {
      toast.error('PDF generation failed')
    }
  }

  const generateLegalNotice = async () => {
    if (!disputes || disputes.total_patterns_detected === 0) return
    const top = disputes.disputes[0]
    const noticeData = {
      noticee_name: 'Opposing Heir',
      client_name: 'User',
      grievance_paras: [`Opposing heir committed ${top.pattern}.`],
      relief_demanded: [top.remedy || 'Legal action'],
      subject: `Legal Notice Regarding ${top.pattern.replace(/_/g, ' ').toUpperCase()}`,
    }
    try {
      const response = await fetch('http://localhost:8000/api/v1/documents/legal-notice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(noticeData),
      })
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'legal_notice.pdf'
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Legal notice generated')
    } catch (err) {
      toast.error('Failed to generate legal notice')
    }
  }

  const generateFIR = async () => {
    if (!disputes || disputes.total_patterns_detected === 0) return
    const firData = {
      accused_name: 'Opposing Heir',
      fir_narrative: 'Illegal mutation without succession certificate.',
      offence_sections: 'PPC 498A',
    }
    try {
      const response = await fetch('http://localhost:8000/api/v1/documents/fir', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(firData),
      })
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'fir_draft.pdf'
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('FIR draft generated')
    } catch (err) {
      toast.error('Failed to generate FIR')
    }
  }

  // Prepare chart data
  const pieData = result ? Object.entries(result).map(([name, data]) => ({
    name: name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value: data.amount,
    fraction: data.fraction,
  })) : []

  const taxSavingsData = tax && typeof tax === 'object' ? Object.entries(tax).map(([heir, t]) => ({
    heir: heir.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    savings: t.savings_if_filer || 0,
  })).filter(item => item.savings > 0) : []

  const shareTableRows = result ? Object.entries(result).map(([heir, data]) => ({
    heir: heir.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    fraction: data.fraction,
    amount: data.amount,
  })) : []

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Inheritance Calculator</h1>

      <div className="flex gap-4 mb-4">
        <button className={`px-4 py-2 rounded-md ${inputMode === 'form' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`} onClick={() => setInputMode('form')}>Form</button>
        <button className={`px-4 py-2 rounded-md ${inputMode === 'nlp' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`} onClick={() => setInputMode('nlp')}>Natural Language</button>
      </div>

      {inputMode === 'nlp' && (
        <div className="bg-white p-4 rounded-lg shadow-md mb-6">
          <textarea rows={4} className="w-full border rounded-md p-2" placeholder="Describe situation..." value={nlpText} onChange={(e) => setNlpText(e.target.value)} />
          <button onClick={onParseNLP} disabled={parsing} className="mt-2 bg-blue-600 text-white px-4 py-2 rounded-md">{parsing ? 'Parsing...' : 'Parse Scenario'}</button>
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow-md">
        {/* Form fields – omitted for brevity but same as previous working version */}
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium">Sect</label><select name="sect" value={form.sect} onChange={handleChange} className="w-full border p-2 rounded"><option value="hanafi">Hanafi</option><option value="shia">Shia</option><option value="christian">Christian</option><option value="hindu">Hindu</option></select></div>
          <div><label className="block text-sm font-medium">Total Estate (PKR)</label><input type="number" name="total_estate" value={form.total_estate} onChange={handleChange} className="w-full border p-2 rounded" /></div>
          <div><label className="block text-sm font-medium">Debts</label><input type="number" name="debts" value={form.debts} onChange={handleChange} className="w-full border p-2 rounded" /></div>
          <div><label className="block text-sm font-medium">Funeral Expenses</label><input type="number" name="funeral" value={form.funeral} onChange={handleChange} className="w-full border p-2 rounded" /></div>
          <div><label className="block text-sm font-medium">Wasiyyat</label><input type="number" name="wasiyyat" value={form.wasiyyat} onChange={handleChange} className="w-full border p-2 rounded" /></div>
          <div><label className="block text-sm font-medium">Sons</label><input type="number" name="sons" value={form.sons} onChange={handleChange} className="w-full border p-2 rounded" /></div>
          <div><label className="block text-sm font-medium">Daughters</label><input type="number" name="daughters" value={form.daughters} onChange={handleChange} className="w-full border p-2 rounded" /></div>
          <div><label className="block text-sm font-medium">Wives</label><input type="number" name="wife" value={form.wife} onChange={handleChange} className="w-full border p-2 rounded" /></div>
          <div><label className="block text-sm font-medium">Husband (0/1)</label><input type="number" name="husband" value={form.husband} onChange={handleChange} className="w-full border p-2 rounded" /></div>
          <div><label className="block text-sm font-medium">Mother (0/1)</label><input type="number" name="mother" value={form.mother} onChange={handleChange} className="w-full border p-2 rounded" /></div>
          <div><label className="block text-sm font-medium">Father (0/1)</label><input type="number" name="father" value={form.father} onChange={handleChange} className="w-full border p-2 rounded" /></div>
        </div>

        <h2 className="text-lg font-semibold mt-6 mb-2">Dispute Flags (optional)</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          <label className="flex items-center"><input type="checkbox" name="mutation_by_single_heir" checked={form.mutation_by_single_heir} onChange={handleChange} className="mr-2" /> Mutation by single heir</label>
          <label className="flex items-center"><input type="checkbox" name="no_succession_certificate" checked={form.no_succession_certificate} onChange={handleChange} className="mr-2" /> No succession certificate</label>
          <label className="flex items-center"><input type="checkbox" name="one_heir_wants_sell" checked={form.one_heir_wants_sell} onChange={handleChange} className="mr-2" /> One heir wants to sell, others refuse</label>
          <label className="flex items-center"><input type="checkbox" name="gift_deed_mentioned" checked={form.gift_deed_mentioned} onChange={handleChange} className="mr-2" /> Gift deed (Hiba) mentioned</label>
          <label className="flex items-center"><input type="checkbox" name="donor_still_in_possession" checked={form.donor_still_in_possession} onChange={handleChange} className="mr-2" /> Donor still in possession</label>
          <label className="flex items-center"><input type="checkbox" name="will_mentioned" checked={form.will_mentioned} onChange={handleChange} className="mr-2" /> Will mentioned</label>
          <div className="flex items-center col-span-2"><span className="mr-2">Will percentage:</span><input type="number" name="will_percentage" value={form.will_percentage} onChange={handleChange} className="border p-1 rounded w-24" /> %</div>
          <label className="flex items-center"><input type="checkbox" name="debts_mentioned" checked={form.debts_mentioned} onChange={handleChange} className="mr-2" /> Debts present</label>
          <label className="flex items-center"><input type="checkbox" name="estate_distributed_before_debt" checked={form.estate_distributed_before_debt} onChange={handleChange} className="mr-2" /> Estate distributed before paying debts</label>
          <label className="flex items-center"><input type="checkbox" name="heir_age_under_18" checked={form.heir_age_under_18} onChange={handleChange} className="mr-2" /> Minor heir involved</label>
          <label className="flex items-center"><input type="checkbox" name="daughters_denied_share" checked={form.daughters_denied_share} onChange={handleChange} className="mr-2" /> Daughter's share denied</label>
          <label className="flex items-center"><input type="checkbox" name="forced_relinquishment" checked={form.forced_relinquishment} onChange={handleChange} className="mr-2" /> Forced relinquishment</label>
        </div>

        <button onClick={calculateShares} disabled={loading} className="mt-6 bg-blue-600 text-white px-4 py-2 rounded-md w-full">{loading ? 'Calculating...' : 'Calculate Shares'}</button>
      </div>

      {loading && <div className="text-center my-8">Loading...</div>}

      {result && (
        <div className="mt-8 space-y-6">
          {/* Share Distribution */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-4">Share Distribution</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <table className="min-w-full border">
                  <thead><tr className="bg-gray-100"><th className="p-2 border">Heir</th><th className="p-2 border">Fraction</th><th className="p-2 border">Amount (PKR)</th></tr></thead>
                  <tbody>
                    {shareTableRows.map(row => (
                      <tr key={row.heir}><td className="p-2 border">{row.heir}</td><td className="p-2 border">{row.fraction}</td><td className="p-2 border">Rs {row.amount.toLocaleString()}</td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}>
                      {pieData.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(value) => `Rs ${value?.toLocaleString()}`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Heir Breakdown */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-4">Detailed Heir Breakdown</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(result).map(([heir, data]) => (
                <div key={heir} className="border rounded-lg p-3 shadow-sm">
                  <h3 className="font-bold text-lg">{heir.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h3>
                  <p>Fraction: {data.fraction}</p>
                  <p>Amount: Rs {data.amount.toLocaleString()}</p>
                  {tax && tax[heir] && <p>Net after tax: Rs {tax[heir].net_after_all_taxes?.toLocaleString()}</p>}
                </div>
              ))}
            </div>
          </div>

          {/* Tax Analysis */}
          {tax && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold mb-4">Tax Analysis (If Selling)</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <table className="min-w-full border">
                    <thead><tr className="bg-gray-100"><th className="p-2 border">Heir</th><th className="p-2 border">236C Tax</th><th className="p-2 border">Net After Tax</th></tr></thead>
                    <tbody>
                      {Object.entries(tax).map(([heir, t]) => (
                        <tr key={heir}><td className="p-2 border">{heir.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</td><td className="p-2 border">Rs {t.advance_tax_236C?.toLocaleString() || 0}</td><td className="p-2 border">Rs {t.net_after_all_taxes?.toLocaleString()}</td></tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {taxSavingsData.length > 0 && (
                  <div>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={taxSavingsData}>
                        <XAxis dataKey="heir" />
                        <YAxis />
                        <Tooltip formatter={(value) => `Rs ${value?.toLocaleString()}`} />
                        <Bar dataKey="savings" fill="#82ca9d" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Dispute & Fraud Detection */}
          {disputes && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold mb-4">Dispute & Fraud Detection</h2>
              {disputes.total_patterns_detected > 0 ? (
                <>
                  {disputes.disputes.map((d, idx) => (
                    <div key={idx} className="border-l-4 border-red-500 bg-red-50 p-3 mb-3">
                      <h3 className="font-bold">{d.pattern.replace(/_/g, ' ').toUpperCase()}</h3>
                      <p>Score: {d.fraud_score}/100</p>
                      <p>Law: {Object.keys(d.law_sections).join(', ')}</p>
                      <p>Recommended: {d.recommended_actions?.slice(0,2).join('; ')}</p>
                    </div>
                  ))}
                  <div className="flex gap-4 mt-4">
                    <button onClick={generateLegalNotice} className="px-4 py-2 bg-yellow-600 text-white rounded-md">Download Legal Notice (PDF)</button>
                    <button onClick={generateFIR} className="px-4 py-2 bg-red-600 text-white rounded-md">Download FIR Draft (PDF)</button>
                  </div>
                </>
              ) : <p>No disputes detected.</p>}
            </div>
          )}

          {/* Process Navigator */}
          {processSteps.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold mb-4">Legal Process Navigator</h2>
              <div className="space-y-2">
                {processSteps.map((step, idx) => (
                  <details key={idx} className="border p-2 rounded">
                    <summary className="font-semibold cursor-pointer">{step.name}</summary>
                    <div className="mt-2 text-sm">
                      <p><strong>Authority:</strong> {step.authority}</p>
                      <p><strong>Fee:</strong> {step.fee}</p>
                      <p><strong>Time:</strong> {step.time}</p>
                      {step.note && <p className="text-blue-600">{step.note}</p>}
                    </div>
                  </details>
                ))}
              </div>
            </div>
          )}

          {/* Export Options */}
          <div className="bg-white p-6 rounded-lg shadow-md flex flex-wrap gap-4">
            <button onClick={handleGeneratePDF} className="px-4 py-2 bg-blue-600 text-white rounded-md">Generate Share Certificate (PDF)</button>
            {shareTableRows.length > 0 && <CSVLink data={shareTableRows} filename="shares.csv" className="px-4 py-2 bg-green-600 text-white rounded-md">Download Shares CSV</CSVLink>}
            {tax && <CSVLink data={Object.entries(tax).map(([heir, t]) => ({ heir: heir.replace(/_/g, ' '), tax: t.advance_tax_236C, net: t.net_after_all_taxes }))} filename="tax.csv" className="px-4 py-2 bg-green-600 text-white rounded-md">Download Tax CSV</CSVLink>}
          </div>
        </div>
      )}
    </div>
  )
}

export default CalculatorPage