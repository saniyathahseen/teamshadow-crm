import React, { useState, useEffect } from 'react';
import { login, logout, getDashboard, getCustomers, getInquiries, getQuotations, getBookings, getPayments, getStaff, getEditingProjects, getActivity, createCustomer, createInquiry, createQuotation, createBooking, createPayment, createEditingProject, sendQuotation, updateBookingStatus, updateEditingStatus, deleteInquiry, getCustomer } from './api';
import './App.css';

// ============================================
// Login Component
// ============================================
function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await login(username, password);
      onLogin(data.user);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <div className="login-screen">
      <div className="login-card">
        <div className="login-logo">
          <i className="fas fa-ring"></i>
          <h1>Team Shadow</h1>
          <p>Wedding CRM</p>
        </div>
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>Username</label>
            <input type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="Enter username" required />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Enter password" required />
          </div>
          {error && <div className="login-error">{error}</div>}
          <button type="submit" className="btn btn-primary btn-full">Sign In</button>
          <div className="login-hint">
            <p>Demo: admin / admin123</p>
            <p>Staff: sarah / staff123</p>
          </div>
        </form>
      </div>
    </div>
  );
}

// ============================================
// Sidebar Component
// ============================================
function Sidebar({ user, activeSection, onNavigate, counts }) {
  const menuItems = [
    { id: 'dashboard', icon: 'fa-th-large', label: 'Dashboard' },
    { id: 'inquiries', icon: 'fa-inbox', label: 'Inquiries', count: counts.inquiries },
    { id: 'customers', icon: 'fa-users', label: 'Customers' },
    { id: 'quotations', icon: 'fa-file-invoice', label: 'Quotations', count: counts.quotations },
    { id: 'bookings', icon: 'fa-check-circle', label: 'Bookings', count: counts.bookings },
    { id: 'editing', icon: 'fa-film', label: 'Editing' },
    { id: 'payments', icon: 'fa-money-bill', label: 'Payments' },
    { id: 'staff', icon: 'fa-user-tie', label: 'Staff' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">
          <i className="fas fa-ring"></i>
          <div className="logo-text">
            <span className="logo-title">Team Shadow</span>
            <span className="logo-subtitle">CRM</span>
          </div>
        </div>
      </div>
      <nav className="sidebar-nav">
        {menuItems.map(item => (
          <a key={item.id} href="#" className={`nav-item ${activeSection === item.id ? 'active' : ''}`}
             onClick={e => { e.preventDefault(); onNavigate(item.id); }}>
            <i className={`fas ${item.icon}`}></i>
            <span>{item.label}</span>
            {item.count !== undefined && <span className="badge">{item.count}</span>}
          </a>
        ))}
        <div className="nav-divider"></div>
        <a href="#" className="nav-item" onClick={e => { e.preventDefault(); onNavigate('portal'); }}>
          <i className="fas fa-user-circle"></i><span>Customer Portal</span>
        </a>
        <a href="#" className="nav-item" onClick={e => { e.preventDefault(); logout(); }}>
          <i className="fas fa-sign-out-alt"></i><span>Logout</span>
        </a>
      </nav>
      <div className="sidebar-footer">
        <div className="user-profile-sidebar">
          <div className="user-avatar-sm">{user?.full_name?.split(' ').map(w => w[0]).join('').slice(0, 2)}</div>
          <div className="user-info-sidebar">
            <span className="user-name">{user?.full_name}</span>
            <span className="user-role">{user?.role}</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

// ============================================
// Dashboard Page
// ============================================
function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const d = await getDashboard();
      setData(d);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  if (loading) return <div className="loading">Loading dashboard...</div>;
  if (!data) return <div className="loading">Failed to load dashboard</div>;

  const stats = [
    { icon: 'fa-inbox', color: '#6366f1', bg: '#eef2ff', value: data.total_inquiries, label: 'Total Inquiries' },
    { icon: 'fa-clock', color: '#f59e0b', bg: '#fef3c7', value: data.active_leads, label: 'Active Leads' },
    { icon: 'fa-file-invoice', color: '#3b82f6', bg: '#dbeafe', value: data.total_quotations, label: 'Quotations' },
    { icon: 'fa-check-circle', color: '#10b981', bg: '#d1fae5', value: data.confirmed_bookings, label: 'Confirmed' },
    { icon: 'fa-rupee-sign', color: '#8b5cf6', bg: '#ede9fe', value: `₹${(data.total_revenue || 0).toLocaleString()}`, label: 'Revenue' },
    { icon: 'fa-exclamation-triangle', color: '#ef4444', bg: '#fee2e2', value: data.pending_payments, label: 'Pending Payments' },
  ];

  const channelColors = { instagram: '#e1306c', whatsapp: '#25d366', website: '#2196f3', facebook: '#1877f2', google: '#f59e0b', referral: '#7b1fa2' };
  const channels = data.channels || {};
  const total = Object.values(channels).reduce((a, b) => a + b, 0) || 1;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of your wedding business</p>
      </div>
      <div className="stats-grid">
        {stats.map((s, i) => (
          <div key={i} className="stat-card">
            <div className="stat-icon" style={{ background: s.bg }}><i className={`fas ${s.icon}`} style={{ color: s.color }}></i></div>
            <div><span className="stat-value">{s.value}</span><span className="stat-label">{s.label}</span></div>
          </div>
        ))}
      </div>
      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header"><h3>Inquiries by Channel</h3></div>
          <div className="card-body">
            {Object.keys(channels).length ? Object.entries(channels).map(([k, v]) => (
              <div key={k} className="channel-item">
                <div className="channel-icon" style={{ background: channelColors[k] + '22' }}>
                  <i className={`fab fa-${k === 'website' ? 'globe' : k}`} style={{ color: channelColors[k] }}></i>
                </div>
                <div className="channel-info">
                  <span className="channel-name" style={{ textTransform: 'capitalize' }}>{k}</span>
                  <div className="channel-bar"><div className="channel-fill" style={{ width: `${(v / total * 100).toFixed(1)}%`, background: channelColors[k] }}></div></div>
                </div>
                <span className="channel-count">{v}</span>
              </div>
            )) : <p className="text-muted">No data yet</p>}
          </div>
        </div>
        <div className="card">
          <div className="card-header"><h3>Recent Activity</h3></div>
          <div className="card-body">
            {data.recent_activity?.length ? data.recent_activity.map(a => (
              <div key={a.id} className="activity-item">
                <div className="activity-dot" style={{ background: a.action === 'created' ? '#10b981' : '#6366f1' }}></div>
                <div><div className="activity-text">{a.description}</div><div className="activity-time">{timeAgo(a.created_at)}</div></div>
              </div>
            )) : <p className="text-muted">No recent activity</p>}
          </div>
        </div>
        <div className="card">
          <div className="card-header"><h3>Upcoming Events</h3></div>
          <div className="card-body">
            {data.upcoming_events?.length ? data.upcoming_events.map(e => (
              <div key={e.id} className="activity-item">
                <div className="activity-dot" style={{ background: '#6366f1' }}></div>
                <div><div className="activity-text"><strong>{e.customer_name}</strong> - {e.event_type || 'Wedding'}</div>
                <div className="activity-time">{e.event_date ? new Date(e.event_date).toLocaleDateString('en-IN') : 'TBD'} {e.venue ? `at ${e.venue}` : ''}</div></div>
              </div>
            )) : <p className="text-muted">No upcoming events</p>}
          </div>
        </div>
        <div className="card">
          <div className="card-header"><h3>Team Stats</h3></div>
          <div className="card-body">
            {data.team_stats?.length ? data.team_stats.map((t, i) => (
              <div key={i} className="activity-item">
                <div className="user-avatar-sm" style={{ background: ['#6366f1', '#f59e0b', '#10b981', '#ef4444'][i % 4] }}>{t.initials}</div>
                <div><div className="activity-text"><strong>{t.name}</strong> <span className="text-muted">({t.role})</span></div>
                <div className="activity-time">{t.inquiry_count} inquiries assigned</div></div>
              </div>
            )) : <p className="text-muted">No team data</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================
// Inquiries Page
// ============================================
function Inquiries() {
  const [data, setData] = useState([]);
  const [status, setStatus] = useState('all');
  const [source, setSource] = useState('all');
  const [showForm, setShowForm] = useState(false);
  const [customers, setCustomers] = useState([]);
  const [form, setForm] = useState({ customer_id: '', source: 'instagram', event_type: '', budget_estimate: '', notes: '', name: '', phone: '' });

  useEffect(() => { loadData(); loadCustomers(); }, [status, source]);

  const loadData = async () => {
    try { setData(await getInquiries({ status, source })); } catch (e) { console.error(e); }
  };
  const loadCustomers = async () => {
    try { setCustomers(await getCustomers()); } catch (e) { console.error(e); }
  };

  const handleCreate = async () => {
    try {
      let customerId = form.customer_id;
      if (!customerId) {
        const c = await createCustomer({ name: form.name, phone: form.phone });
        customerId = c.id;
      }
      await createInquiry({
        customer_id: parseInt(customerId), source: form.source,
        event_type: form.event_type, budget_estimate: parseFloat(form.budget_estimate) || null,
        notes: form.notes
      });
      setShowForm(false);
      loadData();
    } catch (e) { alert(e.response?.data?.detail || 'Error creating inquiry'); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this inquiry?')) return;
    try { await deleteInquiry(id); loadData(); } catch (e) { alert('Error deleting'); }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Inquiries</h1>
        <div className="page-actions">
          <select value={status} onChange={e => setStatus(e.target.value)} className="filter-select">
            <option value="all">All Status</option>
            <option value="new">New</option><option value="contacted">Contacted</option>
            <option value="qualified">Qualified</option><option value="quotation_sent">Quotation Sent</option>
            <option value="follow_up">Follow Up</option><option value="negotiation">Negotiation</option>
            <option value="booked">Booked</option><option value="lost">Lost</option>
          </select>
          <select value={source} onChange={e => setSource(e.target.value)} className="filter-select">
            <option value="all">All Sources</option>
            <option value="instagram">Instagram</option><option value="whatsapp">WhatsApp</option>
            <option value="website">Website</option><option value="facebook">Facebook</option>
            <option value="google">Google</option><option value="referral">Referral</option>
          </select>
          <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
            <i className="fas fa-plus"></i> New Inquiry
          </button>
        </div>
      </div>

      {showForm && (
        <div className="form-card">
          <h3>New Inquiry</h3>
          <div className="form-row">
            <div className="form-group">
              <label>Select Customer</label>
              <select value={form.customer_id} onChange={e => setForm({ ...form, customer_id: e.target.value })}>
                <option value="">+ Create New</option>
                {customers.map(c => <option key={c.id} value={c.id}>{c.name} ({c.phone})</option>)}
              </select>
            </div>
            {!form.customer_id && (
              <div className="form-row" style={{ gridColumn: '1 / -1' }}>
                <div className="form-group"><label>Name *</label><input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Client name" /></div>
                <div className="form-group"><label>Phone *</label><input value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} placeholder="Phone" /></div>
              </div>
            )}
          </div>
          <div className="form-row">
            <div className="form-group"><label>Source</label>
              <select value={form.source} onChange={e => setForm({ ...form, source: e.target.value })}>
                <option value="instagram">Instagram</option><option value="whatsapp">WhatsApp</option>
                <option value="website">Website</option><option value="facebook">Facebook</option>
                <option value="google">Google</option><option value="referral">Referral</option>
              </select>
            </div>
            <div className="form-group"><label>Event Type</label>
              <select value={form.event_type} onChange={e => setForm({ ...form, event_type: e.target.value })}>
                <option value="">Select</option><option value="Wedding">Wedding</option>
                <option value="Engagement">Engagement</option><option value="Reception">Reception</option>
                <option value="Pre-Wedding">Pre-Wedding</option><option value="Corporate">Corporate</option>
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group"><label>Budget (₹)</label><input type="number" value={form.budget_estimate} onChange={e => setForm({ ...form, budget_estimate: e.target.value })} placeholder="e.g. 500000" /></div>
            <div className="form-group"><label>Notes</label><textarea value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} rows="2"></textarea></div>
          </div>
          <div className="form-actions">
            <button className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleCreate}>Save Inquiry</button>
          </div>
        </div>
      )}

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr><th>Client</th><th>Source</th><th>Event</th><th>Budget</th><th>Status</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {data.length === 0 ? (
              <tr><td colSpan="6" className="empty-cell">No inquiries found</td></tr>
            ) : data.map(i => (
              <tr key={i.id}>
                <td><strong>{i.customer?.name || 'Unknown'}</strong><br /><span className="text-muted">{i.customer?.phone || ''}</span></td>
                <td><span className={`source-badge source-${i.source}`}><i className={`fab fa-${i.source === 'website' ? 'globe' : i.source}`}></i> {i.source}</span></td>
                <td>{i.event_type || '-'}</td>
                <td>{i.budget_estimate ? `₹${i.budget_estimate.toLocaleString()}` : '-'}</td>
                <td><span className={`status status-${i.status}`}>{i.status.replace('_', ' ')}</span></td>
                <td>
                  <button className="action-btn delete" onClick={() => handleDelete(i.id)} title="Delete"><i className="fas fa-trash"></i></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ============================================
// Customers Page
// ============================================
function Customers() {
  const [data, setData] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', phone: '', email: '', wedding_date: '', bride_name: '', groom_name: '', venue: '', notes: '' });
  const [detail, setDetail] = useState(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try { setData(await getCustomers()); } catch (e) { console.error(e); }
  };

  const handleCreate = async () => {
    try {
      await createCustomer(form);
      setShowForm(false);
      setForm({ name: '', phone: '', email: '', wedding_date: '', bride_name: '', groom_name: '', venue: '', notes: '' });
      loadData();
    } catch (e) { alert(e.response?.data?.detail || 'Error'); }
  };

  const viewDetail = async (id) => {
    try { setDetail(await getCustomer(id)); } catch (e) { console.error(e); }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Customers</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          <i className="fas fa-plus"></i> New Customer
        </button>
      </div>

      {showForm && (
        <div className="form-card">
          <h3>New Customer</h3>
          <div className="form-row">
            <div className="form-group"><label>Name *</label><input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} /></div>
            <div className="form-group"><label>Phone *</label><input value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} /></div>
          </div>
          <div className="form-row">
            <div className="form-group"><label>Email</label><input value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} /></div>
            <div className="form-group"><label>Wedding Date</label><input type="date" value={form.wedding_date} onChange={e => setForm({ ...form, wedding_date: e.target.value })} /></div>
          </div>
          <div className="form-row">
            <div className="form-group"><label>Bride</label><input value={form.bride_name} onChange={e => setForm({ ...form, bride_name: e.target.value })} /></div>
            <div className="form-group"><label>Groom</label><input value={form.groom_name} onChange={e => setForm({ ...form, groom_name: e.target.value })} /></div>
          </div>
          <div className="form-group"><label>Venue</label><input value={form.venue} onChange={e => setForm({ ...form, venue: e.target.value })} /></div>
          <div className="form-actions">
            <button className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleCreate}>Save</button>
          </div>
        </div>
      )}

      {detail && (
        <div className="modal-overlay" onClick={() => setDetail(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header"><h2>{detail.name}</h2><button className="modal-close" onClick={() => setDetail(null)}>&times;</button></div>
            <div className="modal-body">
              <div className="detail-grid">
                <div><strong>Phone:</strong> {detail.phone}</div>
                <div><strong>Email:</strong> {detail.email || '-'}</div>
                <div><strong>Bride:</strong> {detail.bride_name || '-'}</div>
                <div><strong>Groom:</strong> {detail.groom_name || '-'}</div>
                <div><strong>Wedding:</strong> {detail.wedding_date ? new Date(detail.wedding_date).toLocaleDateString('en-IN') : '-'}</div>
                <div><strong>Venue:</strong> {detail.venue || '-'}</div>
              </div>
              <h4 style={{ marginTop: 16 }}>Inquiries ({detail.inquiries?.length || 0})</h4>
              {detail.inquiries?.map(i => <div key={i.id} className="timeline-item">{i.source} - <span className={`status status-${i.status}`}>{i.status}</span></div>)}
              <h4 style={{ marginTop: 12 }}>Bookings ({detail.bookings?.length || 0})</h4>
              {detail.bookings?.map(b => <div key={b.id} className="timeline-item">{b.booking_number} - ₹{b.total_amount?.toLocaleString()}</div>)}
            </div>
          </div>
        </div>
      )}

      <div className="table-container">
        <table className="data-table">
          <thead><tr><th>Name</th><th>Phone</th><th>Email</th><th>Wedding Date</th><th>Actions</th></tr></thead>
          <tbody>
            {data.length === 0 ? <tr><td colSpan="5" className="empty-cell">No customers</td></tr> :
              data.map(c => (
                <tr key={c.id}>
                  <td><strong>{c.name}</strong></td>
                  <td>{c.phone}</td>
                  <td>{c.email || '-'}</td>
                  <td>{c.wedding_date ? new Date(c.wedding_date).toLocaleDateString('en-IN') : '-'}</td>
                  <td><button className="action-btn edit" onClick={() => viewDetail(c.id)}><i className="fas fa-eye"></i></button></td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ============================================
// Quotations Page
// ============================================
function Quotations() {
  const [data, setData] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [customers, setCustomers] = useState([]);
  const [form, setForm] = useState({ customer_id: '', package_name: '', base_amount: '', discount: '0', gst: '0', notes: '' });

  useEffect(() => { loadData(); loadCustomers(); }, []);

  const loadData = async () => { try { setData(await getQuotations()); } catch (e) { console.error(e); } };
  const loadCustomers = async () => { try { setCustomers(await getCustomers()); } catch (e) { console.error(e); } };

  const handleCreate = async () => {
    try {
      await createQuotation({ customer_id: parseInt(form.customer_id), package_name: form.package_name, base_amount: parseFloat(form.base_amount) || 0, discount: parseFloat(form.discount) || 0, gst: parseFloat(form.gst) || 0, notes: form.notes });
      setShowForm(false);
      loadData();
    } catch (e) { alert('Error creating quotation'); }
  };

  const handleSend = async (id) => {
    try { await sendQuotation(id); loadData(); } catch (e) { alert('Error sending'); }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Quotations</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}><i className="fas fa-plus"></i> New Quotation</button>
      </div>

      {showForm && (
        <div className="form-card">
          <h3>New Quotation</h3>
          <div className="form-group">
            <label>Client</label>
            <select value={form.customer_id} onChange={e => setForm({ ...form, customer_id: e.target.value })}>
              <option value="">Select client</option>
              {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="form-row">
            <div className="form-group"><label>Package</label><input value={form.package_name} onChange={e => setForm({ ...form, package_name: e.target.value })} /></div>
            <div className="form-group"><label>Amount (₹)</label><input type="number" value={form.base_amount} onChange={e => setForm({ ...form, base_amount: e.target.value })} /></div>
          </div>
          <div className="form-row">
            <div className="form-group"><label>Discount (%)</label><input type="number" value={form.discount} onChange={e => setForm({ ...form, discount: e.target.value })} /></div>
            <div className="form-group"><label>GST (%)</label><input type="number" value={form.gst} onChange={e => setForm({ ...form, gst: e.target.value })} /></div>
          </div>
          <div className="form-actions">
            <button className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleCreate}>Create</button>
          </div>
        </div>
      )}

      <div className="table-container">
        <table className="data-table">
          <thead><tr><th>Quote #</th><th>Client</th><th>Package</th><th>Amount</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            {data.length === 0 ? <tr><td colSpan="6" className="empty-cell">No quotations</td></tr> :
              data.map(q => (
                <tr key={q.id}>
                  <td><strong>{q.quote_number}</strong></td>
                  <td>{q.customer?.name || '-'}</td>
                  <td>{q.package_name || '-'}</td>
                  <td><strong>₹{q.total_amount?.toLocaleString()}</strong></td>
                  <td><span className={`status status-${q.status}`}>{q.status}</span></td>
                  <td>{q.status === 'draft' && <button className="action-btn quote" onClick={() => handleSend(q.id)}><i className="fas fa-paper-plane"></i></button>}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ============================================
// Bookings Page
// ============================================
function Bookings() {
  const [data, setData] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [customers, setCustomers] = useState([]);
  const [form, setForm] = useState({ customer_id: '', event_type: 'Wedding', event_date: '', total_amount: '', advance_amount: '', venue: '' });

  useEffect(() => { loadData(); loadCustomers(); }, []);

  const loadData = async () => { try { setData(await getBookings()); } catch (e) { console.error(e); } };
  const loadCustomers = async () => { try { setCustomers(await getCustomers()); } catch (e) { console.error(e); } };

  const handleCreate = async () => {
    try {
      await createBooking({ customer_id: parseInt(form.customer_id), event_type: form.event_type, event_date: form.event_date, total_amount: parseFloat(form.total_amount) || 0, advance_amount: parseFloat(form.advance_amount) || 0, venue: form.venue });
      setShowForm(false);
      loadData();
    } catch (e) { alert('Error creating booking'); }
  };

  const handleStatus = async (id) => {
    const statuses = ['booked', 'advance_received', 'event_scheduled', 'event_completed', 'editing', 'album_designing', 'client_approval', 'printing', 'delivered', 'closed'];
    const status = window.prompt(`Update status:\n${statuses.join(', ')}`);
    if (status && statuses.includes(status)) {
      try { await updateBookingStatus(id, status); loadData(); } catch (e) { alert('Error updating'); }
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Bookings</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}><i className="fas fa-plus"></i> New Booking</button>
      </div>

      {showForm && (
        <div className="form-card">
          <h3>New Booking</h3>
          <div className="form-group"><label>Client</label>
            <select value={form.customer_id} onChange={e => setForm({ ...form, customer_id: e.target.value })}>
              <option value="">Select</option>
              {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="form-row">
            <div className="form-group"><label>Event Type</label>
              <select value={form.event_type} onChange={e => setForm({ ...form, event_type: e.target.value })}>
                <option value="Wedding">Wedding</option><option value="Engagement">Engagement</option>
                <option value="Reception">Reception</option><option value="Pre-Wedding">Pre-Wedding</option>
              </select>
            </div>
            <div className="form-group"><label>Event Date</label><input type="date" value={form.event_date} onChange={e => setForm({ ...form, event_date: e.target.value })} /></div>
          </div>
          <div className="form-row">
            <div className="form-group"><label>Total (₹)</label><input type="number" value={form.total_amount} onChange={e => setForm({ ...form, total_amount: e.target.value })} /></div>
            <div className="form-group"><label>Advance (₹)</label><input type="number" value={form.advance_amount} onChange={e => setForm({ ...form, advance_amount: e.target.value })} /></div>
          </div>
          <div className="form-group"><label>Venue</label><input value={form.venue} onChange={e => setForm({ ...form, venue: e.target.value })} /></div>
          <div className="form-actions">
            <button className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleCreate}>Confirm Booking</button>
          </div>
        </div>
      )}

      <div className="table-container">
        <table className="data-table">
          <thead><tr><th>Booking #</th><th>Client</th><th>Event</th><th>Amount</th><th>Paid</th><th>Status</th><th>Date</th><th>Actions</th></tr></thead>
          <tbody>
            {data.length === 0 ? <tr><td colSpan="8" className="empty-cell">No bookings</td></tr> :
              data.map(b => (
                <tr key={b.id}>
                  <td><strong>{b.booking_number}</strong></td>
                  <td>{b.customer?.name || '-'}</td>
                  <td>{b.event_type || 'Wedding'}</td>
                  <td>₹{b.total_amount?.toLocaleString()}</td>
                  <td>₹{b.advance_amount?.toLocaleString()}</td>
                  <td><span className={`status status-${b.status}`}>{b.status.replace('_', ' ')}</span></td>
                  <td>{b.event_date ? new Date(b.event_date).toLocaleDateString('en-IN') : '-'}</td>
                  <td>
                    <button className="action-btn edit" onClick={() => handleStatus(b.id)} title="Update Status"><i className="fas fa-arrow-right"></i></button>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ============================================
// Payments Page
// ============================================
function Payments() {
  const [data, setData] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [bookings, setBookings] = useState([]);
  const [form, setForm] = useState({ booking_id: '', amount: '', payment_type: 'advance', payment_method: 'cash' });

  useEffect(() => { loadData(); loadBookings(); }, []);

  const loadData = async () => { try { setData(await getPayments()); } catch (e) { console.error(e); } };
  const loadBookings = async () => { try { setBookings(await getBookings()); } catch (e) { console.error(e); } };

  const handleCreate = async () => {
    try {
      await createPayment({ booking_id: parseInt(form.booking_id), amount: parseFloat(form.amount), payment_type: form.payment_type, payment_method: form.payment_method });
      setShowForm(false);
      loadData();
    } catch (e) { alert('Error recording payment'); }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Payments</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}><i className="fas fa-plus"></i> Record Payment</button>
      </div>

      {showForm && (
        <div className="form-card">
          <h3>Record Payment</h3>
          <div className="form-group"><label>Booking</label>
            <select value={form.booking_id} onChange={e => setForm({ ...form, booking_id: e.target.value })}>
              <option value="">Select booking</option>
              {bookings.map(b => <option key={b.id} value={b.id}>{b.booking_number} - {b.customer?.name}</option>)}
            </select>
          </div>
          <div className="form-row">
            <div className="form-group"><label>Amount (₹)</label><input type="number" value={form.amount} onChange={e => setForm({ ...form, amount: e.target.value })} /></div>
            <div className="form-group"><label>Type</label>
              <select value={form.payment_type} onChange={e => setForm({ ...form, payment_type: e.target.value })}>
                <option value="advance">Advance</option><option value="milestone">Milestone</option><option value="final">Final</option>
              </select>
            </div>
          </div>
          <div className="form-actions">
            <button className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleCreate}>Record</button>
          </div>
        </div>
      )}

      <div className="table-container">
        <table className="data-table">
          <thead><tr><th>Booking</th><th>Amount</th><th>Type</th><th>Method</th><th>Status</th><th>Date</th></tr></thead>
          <tbody>
            {data.length === 0 ? <tr><td colSpan="6" className="empty-cell">No payments</td></tr> :
              data.map(p => (
                <tr key={p.id}>
                  <td>#{p.booking_id}</td>
                  <td><strong>₹{p.amount?.toLocaleString()}</strong></td>
                  <td style={{ textTransform: 'capitalize' }}>{p.payment_type}</td>
                  <td style={{ textTransform: 'capitalize' }}>{p.payment_method}</td>
                  <td><span className={`status status-${p.status}`}>{p.status}</span></td>
                  <td>{p.payment_date ? new Date(p.payment_date).toLocaleDateString('en-IN') : '-'}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ============================================
// Staff Page
// ============================================
function StaffPage() {
  const [data, setData] = useState([]);
  useEffect(() => { loadData(); }, []);
  const loadData = async () => { try { setData(await getStaff()); } catch (e) { console.error(e); } };

  return (
    <div className="page">
      <div className="page-header"><h1>Staff</h1></div>
      <div className="table-container">
        <table className="data-table">
          <thead><tr><th>Name</th><th>Role</th><th>Specialization</th><th>Available</th><th>Rate</th></tr></thead>
          <tbody>
            {data.length === 0 ? <tr><td colSpan="5" className="empty-cell">No staff</td></tr> :
              data.map(s => (
                <tr key={s.id}>
                  <td><div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div className="user-avatar-sm" style={{ width: 28, height: 28, fontSize: 10 }}>{s.initials}</div> {s.name}
                  </div></td>
                  <td style={{ textTransform: 'capitalize' }}>{s.role}</td>
                  <td>{s.specialization || '-'}</td>
                  <td>{s.is_available ? <span style={{ color: 'var(--success)' }}>Available</span> : <span style={{ color: 'var(--danger)' }}>Busy</span>}</td>
                  <td>₹{s.daily_rate}/day</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ============================================
// Editing Page
// ============================================
function Editing() {
  const [data, setData] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [bookings, setBookings] = useState([]);
  const [form, setForm] = useState({ booking_id: '', editing_notes: '' });

  useEffect(() => { loadData(); loadBookings(); }, []);

  const loadData = async () => { try { setData(await getEditingProjects()); } catch (e) { console.error(e); } };
  const loadBookings = async () => { try { setBookings(await getBookings()); } catch (e) { console.error(e); } };

  const handleCreate = async () => {
    try {
      await createEditingProject({ booking_id: parseInt(form.booking_id), editing_notes: form.editing_notes });
      setShowForm(false);
      loadData();
    } catch (e) { alert('Error creating project'); }
  };

  const handleStatus = async (id) => {
    const statuses = ['raw_received', 'editing_started', 'review', 'client_review', 'approved', 'delivered'];
    const status = window.prompt(`Update status:\n${statuses.join(', ')}`);
    if (status && statuses.includes(status)) {
      try { await updateEditingStatus(id, status); loadData(); } catch (e) { alert('Error updating'); }
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Editing Projects</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}><i className="fas fa-plus"></i> New Project</button>
      </div>

      {showForm && (
        <div className="form-card">
          <h3>New Editing Project</h3>
          <div className="form-group"><label>Booking</label>
            <select value={form.booking_id} onChange={e => setForm({ ...form, booking_id: e.target.value })}>
              <option value="">Select</option>
              {bookings.filter(b => ['event_completed', 'editing'].includes(b.status)).map(b => (
                <option key={b.id} value={b.id}>{b.booking_number} - {b.customer?.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group"><label>Notes</label><textarea value={form.editing_notes} onChange={e => setForm({ ...form, editing_notes: e.target.value })} rows="2"></textarea></div>
          <div className="form-actions">
            <button className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            <button className="btn btn-primary" onClick={handleCreate}>Create</button>
          </div>
        </div>
      )}

      <div className="table-container">
        <table className="data-table">
          <thead><tr><th>Booking</th><th>Client</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            {data.length === 0 ? <tr><td colSpan="4" className="empty-cell">No editing projects</td></tr> :
              data.map(p => (
                <tr key={p.id}>
                  <td>{p.booking_number || '-'}</td>
                  <td>{p.customer_name || '-'}</td>
                  <td><span className={`status status-${p.status === 'raw_received' ? 'new' : p.status === 'delivered' ? 'completed' : 'qualified'}`}>{p.status.replace('_', ' ')}</span></td>
                  <td><button className="action-btn edit" onClick={() => handleStatus(p.id)}><i className="fas fa-arrow-right"></i></button></td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ============================================
// Customer Portal Page
// ============================================
function Portal() {
  const [data, setData] = useState([]);
  useEffect(() => { loadData(); }, []);
  const loadData = async () => { try { setData(await getBookings()); } catch (e) { console.error(e); } };

  const stages = ['booked', 'advance_received', 'event_scheduled', 'event_completed', 'editing', 'album_designing', 'client_approval', 'printing', 'delivered', 'closed'];

  return (
    <div className="page">
      <div className="page-header"><h1>Customer Portal</h1><p>Track wedding project status</p></div>
      <div className="portal-grid">
        {data.length === 0 ? <p className="text-muted" style={{ gridColumn: '1/-1', textAlign: 'center', padding: 40 }}>No active projects</p> :
          data.slice(0, 6).map(b => {
            const currentIdx = stages.indexOf(b.status);
            return (
              <div key={b.id} className="portal-card">
                <h3>{b.customer?.name || 'Client'}</h3>
                <p className="text-muted">{b.event_type || 'Wedding'} | {b.event_date ? new Date(b.event_date).toLocaleDateString('en-IN') : 'TBD'}</p>
                <span className={`status status-${b.status}`}>{b.status.replace('_', ' ')}</span>
                <div className="portal-progress">
                  {stages.slice(0, 6).map((s, i) => (
                    <div key={s} className={`progress-step ${i < currentIdx ? 'step-done' : i === currentIdx ? 'step-current' : 'step-pending'}`}>
                      <i className={`fas ${i < currentIdx ? 'fa-check-circle' : 'fa-circle'}`}></i> {s.replace('_', ' ')}
                    </div>
                  ))}
                </div>
                <div className="portal-footer">
                  <span>Total: <strong>₹{b.total_amount?.toLocaleString()}</strong></span>
                  <span>Paid: <strong>₹{b.advance_amount?.toLocaleString()}</strong></span>
                </div>
              </div>
            );
          })}
      </div>
    </div>
  );
}

// ============================================
// Helper
// ============================================
function timeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = Math.floor((new Date() - new Date(dateStr)) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
  return new Date(dateStr).toLocaleDateString('en-IN');
}

// ============================================
// Main App
// ============================================
function App() {
  const [user, setUser] = useState(null);
  const [section, setSection] = useState('dashboard');
  const [counts, setCounts] = useState({ inquiries: 0, quotations: 0, bookings: 0 });

  useEffect(() => {
    const saved = localStorage.getItem('ts_user');
    if (saved) {
      setUser(JSON.parse(saved));
      loadCounts();
    }
  }, []);

  const loadCounts = async () => {
    try {
      const d = await getDashboard();
      setCounts({ inquiries: d.total_inquiries, quotations: d.total_quotations, bookings: d.confirmed_bookings });
    } catch (e) { console.error(e); }
  };

  const handleLogin = (userData) => {
    setUser(userData);
    loadCounts();
  };

  const handleNavigate = (section) => {
    setSection(section);
    if (section === 'dashboard') loadCounts();
  };

  if (!user) return <Login onLogin={handleLogin} />;

  const renderSection = () => {
    switch (section) {
      case 'dashboard': return <Dashboard />;
      case 'inquiries': return <Inquiries />;
      case 'customers': return <Customers />;
      case 'quotations': return <Quotations />;
      case 'bookings': return <Bookings />;
      case 'payments': return <Payments />;
      case 'staff': return <StaffPage />;
      case 'editing': return <Editing />;
      case 'portal': return <Portal />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar user={user} activeSection={section} onNavigate={handleNavigate} counts={counts} />
      <main className="main-content">
        <header className="top-bar">
          <div className="top-bar-left">
            <div className="date-display">{new Date().toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })}</div>
          </div>
          <div className="top-bar-right">
            <div className="user-profile">
              <div className="user-avatar-sm">{user.full_name?.split(' ').map(w => w[0]).join('').slice(0, 2)}</div>
              <span>{user.full_name}</span>
            </div>
          </div>
        </header>
        <div className="content-area">
          {renderSection()}
        </div>
      </main>
    </div>
  );
}

export default App;