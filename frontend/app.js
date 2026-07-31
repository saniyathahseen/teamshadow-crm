// ============================================
// Team Shadow Weddings CRM - Frontend App
// ============================================

const API = 'http://localhost:8000/api';
let TOKEN = localStorage.getItem('ts_token');
let CURRENT_USER = null;
let CURRENT_SECTION = 'dashboard';

// ============================================
// API Helper
// ============================================
async function api(path, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (TOKEN) headers['Authorization'] = `Bearer ${TOKEN}`;
    const res = await fetch(`${API}${path}`, { ...options, headers });
    if (res.status === 401) { logout(); throw new Error('Session expired'); }
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'API Error');
    return data;
}

// ============================================
// Toast Notifications
// ============================================
function toast(msg, type = 'success') {
    const container = document.getElementById('toastContainer');
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i> ${msg}`;
    container.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 3000);
}

// ============================================
// Auth
// ============================================
async function login(username, password) {
    const data = await api('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
    });
    TOKEN = data.access_token;
    CURRENT_USER = data.user;
    localStorage.setItem('ts_token', TOKEN);
    localStorage.setItem('ts_user', JSON.stringify(CURRENT_USER));
    showApp();
    toast(`Welcome, ${CURRENT_USER.full_name}!`);
    loadDashboard();
}

function logout() {
    TOKEN = null;
    CURRENT_USER = null;
    localStorage.removeItem('ts_token');
    localStorage.removeItem('ts_user');
    document.getElementById('appContainer').style.display = 'none';
    document.getElementById('loginScreen').style.display = 'flex';
}

function showApp() {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('appContainer').style.display = 'flex';
    document.getElementById('userName').textContent = CURRENT_USER.full_name;
    document.getElementById('userRole').textContent = CURRENT_USER.role;
    document.getElementById('userAvatar').textContent = CURRENT_USER.full_name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
    document.getElementById('dateDisplay').textContent = new Date().toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
}

// ============================================
// Navigation
// ============================================
document.querySelectorAll('.nav-item[data-section]').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const section = item.dataset.section;
        switchSection(section);
    });
});

function switchSection(section) {
    CURRENT_SECTION = section;
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.querySelector(`.nav-item[data-section="${section}"]`)?.classList.add('active');
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(`section-${section}`)?.classList.add('active');
    
    // Update add button
    const addBtn = document.getElementById('addBtn');
    const addText = document.getElementById('addBtnText');
    const actions = { inquiries: 'New Inquiry', customers: 'New Customer', quotations: 'New Quotation', bookings: 'New Booking', editing: 'New Project', payments: 'Record Payment' };
    addText.textContent = actions[section] || 'New';
    addBtn.style.display = actions[section] ? 'inline-flex' : 'none';
    
    // Load section data
    const loaders = {
        dashboard: loadDashboard, inquiries: loadInquiries, customers: loadCustomers,
        quotations: loadQuotations, bookings: loadBookings, editing: loadEditing,
        payments: loadPayments, staff: loadStaff, 'customers-portal': loadPortal
    };
    if (loaders[section]) loaders[section]();
}

// ============================================
// Dashboard
// ============================================
async function loadDashboard() {
    try {
        const data = await api('/dashboard');
        const stats = [
            { icon: 'fa-inbox', color: '#6366f1', bg: '#eef2ff', value: data.total_inquiries, label: 'Total Inquiries' },
            { icon: 'fa-clock', color: '#f59e0b', bg: '#fef3c7', value: data.active_leads, label: 'Active Leads' },
            { icon: 'fa-file-invoice', color: '#3b82f6', bg: '#dbeafe', value: data.total_quotations, label: 'Quotations' },
            { icon: 'fa-check-circle', color: '#10b981', bg: '#d1fae5', value: data.confirmed_bookings, label: 'Confirmed' },
            { icon: 'fa-rupee-sign', color: '#8b5cf6', bg: '#ede9fe', value: `₹${(data.total_revenue || 0).toLocaleString()}`, label: 'Revenue' },
            { icon: 'fa-exclamation-triangle', color: '#ef4444', bg: '#fee2e2', value: data.pending_payments, label: 'Pending Payments' }
        ];
        document.getElementById('statsGrid').innerHTML = stats.map(s => `
            <div class="stat-card">
                <div class="stat-icon" style="background:${s.bg}"><i class="fas ${s.icon}" style="color:${s.color}"></i></div>
                <div class="stat-info"><span class="stat-value">${s.value}</span><span class="stat-label">${s.label}</span></div>
            </div>
        `).join('');

        // Channel breakdown
        const channels = data.channels || {};
        const total = Object.values(channels).reduce((a, b) => a + b, 0) || 1;
        const channelColors = { instagram: '#e1306c', whatsapp: '#25d366', website: '#2196f3', facebook: '#1877f2', google: '#f59e0b', referral: '#7b1fa2' };
        document.getElementById('channelBreakdown').innerHTML = Object.entries(channels).length ? 
            Object.entries(channels).map(([k, v]) => `
                <div class="channel-item">
                    <div class="channel-icon" style="background:${channelColors[k]}22"><i class="fab fa-${k === 'website' ? 'globe' : k}" style="color:${channelColors[k]}"></i></div>
                    <div class="channel-info"><span class="channel-name" style="text-transform:capitalize">${k}</span><div class="channel-bar"><div class="channel-fill" style="width:${(v/total*100).toFixed(1)}%;background:${channelColors[k]}"></div></div></div>
                    <span class="channel-count">${v}</span>
                </div>
            `).join('') : '<div class="empty-state"><i class="fas fa-chart-bar"></i><p>No data yet</p></div>';

        // Activity
        document.getElementById('activityList').innerHTML = data.recent_activity?.length ?
            data.recent_activity.map(a => `
                <div class="activity-item">
                    <div class="activity-dot" style="background:${a.action === 'created' ? '#10b981' : a.action === 'payment_received' ? '#f59e0b' : '#6366f1'}"></div>
                    <div><div class="activity-text">${a.description}</div><div class="activity-time">${timeAgo(a.created_at)}</div></div>
                </div>
            `).join('') : '<div class="empty-state"><i class="fas fa-clock"></i><p>No recent activity</p></div>';

        // Upcoming events
        document.getElementById('upcomingEvents').innerHTML = data.upcoming_events?.length ?
            data.upcoming_events.map(e => `
                <div class="activity-item">
                    <div class="activity-dot" style="background:#6366f1"></div>
                    <div><div class="activity-text"><strong>${e.customer_name}</strong> - ${e.event_type || 'Wedding'}</div>
                    <div class="activity-time">${e.event_date ? new Date(e.event_date).toLocaleDateString('en-IN') : 'TBD'} ${e.venue ? 'at ' + e.venue : ''}</div></div>
                </div>
            `).join('') : '<div class="empty-state"><i class="fas fa-calendar"></i><p>No upcoming events</p></div>';

        // Team stats
        document.getElementById('teamStats').innerHTML = data.team_stats?.length ?
            data.team_stats.map(t => `
                <div class="activity-item">
                    <div class="user-avatar-sm" style="background:${['#6366f1','#f59e0b','#10b981','#ef4444'][Math.floor(Math.random()*4)]}">${t.initials}</div>
                    <div><div class="activity-text"><strong>${t.name}</strong> <span style="color:var(--text-secondary);font-size:12px">(${t.role})</span></div>
                    <div class="activity-time">${t.inquiry_count} inquiries assigned</div></div>
                </div>
            `).join('') : '<div class="empty-state"><i class="fas fa-users"></i><p>No team data</p></div>';

        // Update badges
        document.getElementById('inquiryBadge').textContent = data.total_inquiries;
        document.getElementById('quotBadge').textContent = data.total_quotations;
        document.getElementById('bookBadge').textContent = data.confirmed_bookings;
    } catch (e) { toast(e.message, 'error'); }
}

// ============================================
// Inquiries
// ============================================
async function loadInquiries() {
    const status = document.getElementById('inqStatusFilter').value;
    const source = document.getElementById('inqSourceFilter').value;
    try {
        const data = await api(`/inquiries?status=${status}&source=${source}`);
        const tbody = document.getElementById('inquiryBody');
        if (!data.length) {
            tbody.innerHTML = '<tr class="empty"><td colspan="7"><div class="empty-state"><i class="fas fa-inbox"></i><p>No inquiries found</p></div></td></tr>';
            return;
        }
        tbody.innerHTML = data.map(i => `
            <tr>
                <td><strong>${i.customer?.name || 'Unknown'}</strong><br><span style="font-size:11px;color:var(--text-light)">${i.customer?.phone || ''}</span></td>
                <td><span class="source-badge source-${i.source}"><i class="fab fa-${i.source === 'website' ? 'globe' : i.source}"></i> ${i.source}</span></td>
                <td>${i.event_type || '-'}</td>
                <td>${i.budget_estimate ? '₹' + i.budget_estimate.toLocaleString() : '-'}</td>
                <td><span class="status status-${i.status}">${i.status.replace('_', ' ')}</span></td>
                <td>${i.assigned_to ? `<div class="user-avatar-sm" style="width:26px;height:26px;font-size:9px;display:inline-flex">${i.assigned_to.initials}</div>` : '<span style="color:var(--text-light)">Unassigned</span>'}</td>
                <td>
                    <button class="action-btn edit" onclick="editInquiry(${i.id})" title="Edit"><i class="fas fa-edit"></i></button>
                    <button class="action-btn quote" onclick="createQuotation(${i.id}, ${i.customer?.id})" title="Create Quote"><i class="fas fa-file-invoice"></i></button>
                    <button class="action-btn delete" onclick="deleteInquiry(${i.id})" title="Delete"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `).join('');
    } catch (e) { toast(e.message, 'error'); }
}

document.getElementById('inqStatusFilter')?.addEventListener('change', loadInquiries);
document.getElementById('inqSourceFilter')?.addEventListener('change', loadInquiries);

async function deleteInquiry(id) {
    if (!confirm('Delete this inquiry?')) return;
    try { await api(`/inquiries/${id}`, { method: 'DELETE' }); toast('Inquiry deleted'); loadInquiries(); loadDashboard(); }
    catch (e) { toast(e.message, 'error'); }
}

// ============================================
// Customers
// ============================================
async function loadCustomers() {
    try {
        const data = await api('/customers');
        const tbody = document.getElementById('customerBody');
        if (!data.length) { tbody.innerHTML = '<tr class="empty"><td colspan="6"><div class="empty-state"><i class="fas fa-users"></i><p>No customers yet</p></div></td></tr>'; return; }
        tbody.innerHTML = data.map(c => `
            <tr>
                <td><strong>${c.name}</strong></td>
                <td>${c.phone}</td>
                <td>${c.email || '-'}</td>
                <td>${c.wedding_date ? new Date(c.wedding_date).toLocaleDateString('en-IN') : '-'}</td>
                <td style="max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${c.notes || '-'}</td>
                <td><button class="action-btn edit" onclick="viewCustomer(${c.id})"><i class="fas fa-eye"></i></button></td>
            </tr>
        `).join('');
    } catch (e) { toast(e.message, 'error'); }
}

async function viewCustomer(id) {
    try {
        const c = await api(`/customers/${id}`);
        showModal(`Customer: ${c.name}`, `
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px">
                <div><strong>Phone:</strong> ${c.phone}</div>
                <div><strong>Email:</strong> ${c.email || '-'}</div>
                <div><strong>Bride:</strong> ${c.bride_name || '-'}</div>
                <div><strong>Groom:</strong> ${c.groom_name || '-'}</div>
                <div><strong>Wedding:</strong> ${c.wedding_date ? new Date(c.wedding_date).toLocaleDateString('en-IN') : '-'}</div>
                <div><strong>Venue:</strong> ${c.venue || '-'}</div>
            </div>
            ${c.notes ? `<p><strong>Notes:</strong> ${c.notes}</p>` : ''}
            <h4 style="margin-top:16px;margin-bottom:8px">Inquiries (${c.inquiries?.length || 0})</h4>
            ${(c.inquiries || []).map(i => `<div style="font-size:13px;padding:4px 0">${i.source} - <span class="status status-${i.status}">${i.status}</span> <span style="color:var(--text-light)">${timeAgo(i.created_at)}</span></div>`).join('') || '<p style="color:var(--text-light)">No inquiries</p>'}
            <h4 style="margin-top:12px;margin-bottom:8px">Bookings (${c.bookings?.length || 0})</h4>
            ${(c.bookings || []).map(b => `<div style="font-size:13px;padding:4px 0">${b.booking_number} - ₹${b.total_amount.toLocaleString()} - <span class="status status-${b.status}">${b.status}</span></div>`).join('') || '<p style="color:var(--text-light)">No bookings</p>'}
        `, `<button class="btn btn-secondary" onclick="closeModal()">Close</button>`);
    } catch (e) { toast(e.message, 'error'); }
}

// ============================================
// Quotations
// ============================================
async function loadQuotations() {
    try {
        const data = await api('/quotations');
        const tbody = document.getElementById('quotationBody');
        if (!data.length) { tbody.innerHTML = '<tr class="empty"><td colspan="7"><div class="empty-state"><i class="fas fa-file-invoice"></i><p>No quotations yet</p></div></td></tr>'; return; }
        tbody.innerHTML = data.map(q => `
            <tr>
                <td><strong>${q.quote_number}</strong></td>
                <td>${q.customer?.name || 'Unknown'}</td>
                <td>${q.package_name || '-'}</td>
                <td><strong>₹${q.total_amount.toLocaleString()}</strong></td>
                <td><span class="status status-${q.status}">${q.status}</span></td>
                <td>${q.created_at ? new Date(q.created_at).toLocaleDateString('en-IN') : '-'}</td>
                <td>
                    ${q.status === 'draft' ? `<button class="action-btn quote" onclick="sendQuotation(${q.id})"><i class="fas fa-paper-plane"></i></button>` : ''}
                    <button class="action-btn edit" onclick="viewQuotation(${q.id})"><i class="fas fa-eye"></i></button>
                </td>
            </tr>
        `).join('');
    } catch (e) { toast(e.message, 'error'); }
}

async function sendQuotation(id) {
    try { await api(`/quotations/${id}/send`, { method: 'PUT' }); toast('Quotation sent!'); loadQuotations(); }
    catch (e) { toast(e.message, 'error'); }
}

function viewQuotation(id) {
    // Simplified - just show a toast for now
    toast('View quotation details in the API response');
}

// ============================================
// Bookings
// ============================================
async function loadBookings() {
    try {
        const data = await api('/bookings');
        const tbody = document.getElementById('bookingBody');
        if (!data.length) { tbody.innerHTML = '<tr class="empty"><td colspan="8"><div class="empty-state"><i class="fas fa-check-circle"></i><p>No bookings yet</p></div></td></tr>'; return; }
        tbody.innerHTML = data.map(b => `
            <tr>
                <td><strong>${b.booking_number}</strong></td>
                <td>${b.customer?.name || 'Unknown'}</td>
                <td>${b.event_type || 'Wedding'}</td>
                <td><strong>₹${b.total_amount.toLocaleString()}</strong></td>
                <td>₹${b.advance_amount.toLocaleString()}</td>
                <td><span class="status status-${b.status}">${b.status.replace('_', ' ')}</span></td>
                <td>${b.event_date ? new Date(b.event_date).toLocaleDateString('en-IN') : '-'}</td>
                <td>
                    <button class="action-btn edit" onclick="updateBookingStatus(${b.id})"><i class="fas fa-arrow-right"></i></button>
                    <button class="action-btn pay" onclick="recordPayment(${b.id})"><i class="fas fa-money-bill"></i></button>
                </td>
            </tr>
        `).join('');
    } catch (e) { toast(e.message, 'error'); }
}

async function updateBookingStatus(id) {
    const statuses = ['booked', 'advance_received', 'event_scheduled', 'event_completed', 'editing', 'album_designing', 'client_approval', 'printing', 'delivered', 'closed'];
    const status = prompt(`Enter new status:\n${statuses.join(', ')}`);
    if (!status || !statuses.includes(status)) return;
    try { await api(`/bookings/${id}/status?status=${status}`, { method: 'PUT' }); toast(`Status updated to ${status}`); loadBookings(); }
    catch (e) { toast(e.message, 'error'); }
}

// ============================================
// Editing
// ============================================
async function loadEditing() {
    try {
        const data = await api('/editing-projects');
        const tbody = document.getElementById('editingBody');
        if (!data.length) { tbody.innerHTML = '<tr class="empty"><td colspan="6"><div class="empty-state"><i class="fas fa-film"></i><p>No editing projects</p></div></td></tr>'; return; }
        tbody.innerHTML = data.map(p => `
            <tr>
                <td>${p.booking_number || '-'}</td>
                <td>${p.customer_name || 'Unknown'}</td>
                <td>${p.editor?.full_name || 'Unassigned'}</td>
                <td>${p.designer?.full_name || 'Unassigned'}</td>
                <td><span class="status status-${p.status === 'raw_received' ? 'new' : p.status === 'editing_started' ? 'contacted' : p.status === 'delivered' ? 'completed' : 'qualified'}">${p.status.replace('_', ' ')}</span></td>
                <td><button class="action-btn edit" onclick="updateEditingStatus(${p.id})"><i class="fas fa-arrow-right"></i></button></td>
            </tr>
        `).join('');
    } catch (e) { toast(e.message, 'error'); }
}

async function updateEditingStatus(id) {
    const statuses = ['raw_received', 'editing_started', 'review', 'client_review', 'approved', 'delivered'];
    const status = prompt(`Update editing status:\n${statuses.join(', ')}`);
    if (!status || !statuses.includes(status)) return;
    try { await api(`/editing-projects/${id}/status?status=${status}`, { method: 'PUT' }); toast(`Editing status: ${status}`); loadEditing(); }
    catch (e) { toast(e.message, 'error'); }
}

// ============================================
// Payments
// ============================================
async function loadPayments() {
    try {
        const data = await api('/payments');
        const tbody = document.getElementById('paymentBody');
        if (!data.length) { tbody.innerHTML = '<tr class="empty"><td colspan="6"><div class="empty-state"><i class="fas fa-money-bill"></i><p>No payments recorded</p></div></td></tr>'; return; }
        tbody.innerHTML = data.map(p => `
            <tr>
                <td>#${p.booking_id}</td>
                <td><strong>₹${p.amount.toLocaleString()}</strong></td>
                <td style="text-transform:capitalize">${p.payment_type}</td>
                <td style="text-transform:capitalize">${p.payment_method}</td>
                <td><span class="status status-${p.status}">${p.status}</span></td>
                <td>${p.payment_date ? new Date(p.payment_date).toLocaleDateString('en-IN') : '-'}</td>
            </tr>
        `).join('');
    } catch (e) { toast(e.message, 'error'); }
}

// ============================================
// Staff
// ============================================
async function loadStaff() {
    try {
        const data = await api('/staff');
        const tbody = document.getElementById('staffBody');
        if (!data.length) { tbody.innerHTML = '<tr class="empty"><td colspan="5"><div class="empty-state"><i class="fas fa-user-tie"></i><p>No staff added</p></div></td></tr>'; return; }
        tbody.innerHTML = data.map(s => `
            <tr>
                <td><div style="display:flex;align-items:center;gap:8px"><div class="user-avatar-sm" style="width:28px;height:28px;font-size:10px">${s.initials}</div> ${s.name}</div></td>
                <td style="text-transform:capitalize">${s.role}</td>
                <td>${s.specialization || '-'}</td>
                <td>${s.is_available ? '<span style="color:var(--success)">Available</span>' : '<span style="color:var(--danger)">Busy</span>'}</td>
                <td>₹${s.daily_rate}/day</td>
            </tr>
        `).join('');
    } catch (e) { toast(e.message, 'error'); }
}

// ============================================
// Customer Portal
// ============================================
async function loadPortal() {
    try {
        const data = await api('/bookings');
        const grid = document.getElementById('portalGrid');
        if (!data.length) { grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><i class="fas fa-user-circle"></i><p>No active projects to display</p></div>'; return; }
        
        const stages = ['booked', 'advance_received', 'event_scheduled', 'event_completed', 'editing', 'album_designing', 'client_approval', 'printing', 'delivered', 'closed'];
        
        grid.innerHTML = data.slice(0, 6).map(b => {
            const currentIdx = stages.indexOf(b.status);
            return `
                <div class="portal-card">
                    <h3>${b.customer?.name || 'Client'}</h3>
                    <p style="color:var(--text-secondary);font-size:13px">${b.event_type || 'Wedding'} | ${b.event_date ? new Date(b.event_date).toLocaleDateString('en-IN') : 'TBD'}</p>
                    <span class="status status-${b.status}">${b.status.replace('_', ' ')}</span>
                    <div class="portal-progress">
                        ${stages.slice(0, 6).map((s, i) => `
                            <div class="progress-step ${i < currentIdx ? 'step-done' : i === currentIdx ? 'step-current' : 'step-pending'}">
                                <i class="fas ${i < currentIdx ? 'fa-check-circle' : i === currentIdx ? 'fa-circle' : 'fa-circle'}"></i>
                                ${s.replace('_', ' ')}
                            </div>
                        `).join('')}
                    </div>
                    <div style="margin-top:12px;padding-top:12px;border-top:1px solid var(--border-light);display:flex;justify-content:space-between;font-size:13px">
                        <span>Total: <strong>₹${b.total_amount.toLocaleString()}</strong></span>
                        <span>Paid: <strong>₹${b.advance_amount.toLocaleString()}</strong></span>
                    </div>
                </div>
            `;
        }).join('');
    } catch (e) { toast(e.message, 'error'); }
}

// ============================================
// Modal System
// ============================================
function showModal(title, body, footer = '') {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalBody').innerHTML = body;
    document.getElementById('modalFooter').innerHTML = footer;
    document.getElementById('modalOverlay').classList.add('active');
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('active');
}

document.getElementById('modalClose').addEventListener('click', closeModal);
document.getElementById('modalOverlay').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeModal();
});

// ============================================
// Add Button Handler
// ============================================
document.getElementById('addBtn').addEventListener('click', () => {
    const actions = {
        inquiries: showAddInquiry,
        customers: showAddCustomer,
        quotations: showAddQuotation,
        bookings: showAddBooking,
        editing: showAddEditing,
        payments: showAddPayment
    };
    if (actions[CURRENT_SECTION]) actions[CURRENT_SECTION]();
});

// ============================================
// Add Inquiry Form
// ============================================
async function showAddInquiry() {
    let customers = [];
    try { customers = await api('/customers'); } catch(e) {}
    
    showModal('New Inquiry', `
        <div class="form-group"><label>Customer</label>
            <select id="f_customer">
                <option value="">+ Create New Customer</option>
                ${customers.map(c => `<option value="${c.id}">${c.name} (${c.phone})</option>`).join('')}
            </select>
        </div>
        <div id="newCustomerFields">
            <div class="form-row"><div class="form-group"><label>Client Name *</label><input id="f_name" placeholder="e.g. Priya & Rahul"></div>
            <div class="form-group"><label>Phone *</label><input id="f_phone" placeholder="+91 98765 43210"></div></div>
            <div class="form-row"><div class="form-group"><label>Email</label><input id="f_email" placeholder="email@example.com"></div>
            <div class="form-group"><label>Bride Name</label><input id="f_bride" placeholder="Bride's name"></div></div>
            <div class="form-row"><div class="form-group"><label>Groom Name</label><input id="f_groom" placeholder="Groom's name"></div>
            <div class="form-group"><label>Wedding Date</label><input id="f_wedding" type="date"></div></div>
        </div>
        <div class="form-row">
            <div class="form-group"><label>Source *</label><select id="f_source"><option value="instagram">Instagram</option><option value="whatsapp">WhatsApp</option><option value="website">Website</option><option value="facebook">Facebook</option><option value="google">Google</option><option value="referral">Referral</option></select></div>
            <div class="form-group"><label>Event Type</label><select id="f_event"><option value="">Select</option><option value="Wedding">Wedding</option><option value="Engagement">Engagement</option><option value="Reception">Reception</option><option value="Pre-Wedding">Pre-Wedding</option><option value="Corporate">Corporate</option></select></div>
        </div>
        <div class="form-row">
            <div class="form-group"><label>Budget (₹)</label><input id="f_budget" type="number" placeholder="e.g. 500000"></div>
            <div class="form-group"><label>Guests</label><input id="f_guests" type="number" placeholder="e.g. 200"></div>
        </div>
        <div class="form-group"><label>Notes</label><textarea id="f_notes" rows="2" placeholder="Requirements..."></textarea></div>
    `, `
        <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="saveInquiry()">Save Inquiry</button>
    `);
    
    document.getElementById('f_customer').addEventListener('change', function() {
        document.getElementById('newCustomerFields').style.display = this.value ? 'none' : 'block';
    });
}

async function saveInquiry() {
    const customerSelect = document.getElementById('f_customer');
    let customerId = customerSelect.value;
    
    if (!customerId) {
        const name = document.getElementById('f_name').value;
        const phone = document.getElementById('f_phone').value;
        if (!name || !phone) { toast('Please enter customer name and phone', 'error'); return; }
        try {
            const newCust = await api('/customers', {
                method: 'POST',
                body: JSON.stringify({
                    name, phone,
                    email: document.getElementById('f_email').value,
                    bride_name: document.getElementById('f_bride').value,
                    groom_name: document.getElementById('f_groom').value,
                    wedding_date: document.getElementById('f_wedding').value
                })
            });
            customerId = newCust.id;
        } catch(e) { toast(e.message, 'error'); return; }
    }
    
    try {
        await api('/inquiries', {
            method: 'POST',
            body: JSON.stringify({
                customer_id: parseInt(customerId),
                source: document.getElementById('f_source').value,
                event_type: document.getElementById('f_event').value,
                budget_estimate: parseFloat(document.getElementById('f_budget').value) || null,
                guest_count: parseInt(document.getElementById('f_guests').value) || null,
                notes: document.getElementById('f_notes').value
            })
        });
        toast('Inquiry created!');
        closeModal();
        loadInquiries();
        loadDashboard();
    } catch(e) { toast(e.message, 'error'); }
}

// ============================================
// Add Customer Form
// ============================================
function showAddCustomer() {
    showModal('New Customer', `
        <div class="form-row"><div class="form-group"><label>Name *</label><input id="c_name" placeholder="Client name"></div>
        <div class="form-group"><label>Phone *</label><input id="c_phone" placeholder="+91 98765 43210"></div></div>
        <div class="form-row"><div class="form-group"><label>Email</label><input id="c_email" placeholder="email@example.com"></div>
        <div class="form-group"><label>Wedding Date</label><input id="c_wedding" type="date"></div></div>
        <div class="form-row"><div class="form-group"><label>Bride Name</label><input id="c_bride"></div>
        <div class="form-group"><label>Groom Name</label><input id="c_groom"></div></div>
        <div class="form-group"><label>Venue</label><input id="c_venue" placeholder="Wedding venue"></div>
        <div class="form-group"><label>Notes</label><textarea id="c_notes" rows="2"></textarea></div>
    `, `
        <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="saveCustomer()">Save Customer</button>
    `);
}

async function saveCustomer() {
    const name = document.getElementById('c_name').value;
    const phone = document.getElementById('c_phone').value;
    if (!name || !phone) { toast('Name and phone are required', 'error'); return; }
    try {
        await api('/customers', {
            method: 'POST',
            body: JSON.stringify({
                name, phone,
                email: document.getElementById('c_email').value,
                wedding_date: document.getElementById('c_wedding').value,
                bride_name: document.getElementById('c_bride').value,
                groom_name: document.getElementById('c_groom').value,
                venue: document.getElementById('c_venue').value,
                notes: document.getElementById('c_notes').value
            })
        });
        toast('Customer created!');
        closeModal();
        loadCustomers();
    } catch(e) { toast(e.message, 'error'); }
}

// ============================================
// Add Quotation Form
// ============================================
async function showAddQuotation() {
    let customers = [];
    try { customers = await api('/customers'); } catch(e) {}
    
    showModal('New Quotation', `
        <div class="form-group"><label>Client *</label>
            <select id="q_customer">
                <option value="">Select client</option>
                ${customers.map(c => `<option value="${c.id}">${c.name} (${c.phone})</option>`).join('')}
            </select>
        </div>
        <div class="form-row">
            <div class="form-group"><label>Package Name</label><input id="q_package" placeholder="e.g. Premium Wedding"></div>
            <div class="form-group"><label>Base Amount (₹)</label><input id="q_amount" type="number" placeholder="e.g. 500000"></div>
        </div>
        <div class="form-row">
            <div class="form-group"><label>Discount (%)</label><input id="q_discount" type="number" value="0" min="0" max="100"></div>
            <div class="form-group"><label>GST (%)</label><input id="q_gst" type="number" value="0" min="0"></div>
        </div>
        <div class="form-group"><label>Notes</label><textarea id="q_notes" rows="2" placeholder="Payment terms, validity..."></textarea></div>
        <div class="form-group"><label>Valid Until</label><input id="q_valid" type="date"></div>
    `, `
        <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="saveQuotation()">Create Quotation</button>
    `);
}

async function saveQuotation() {
    const customerId = document.getElementById('q_customer').value;
    if (!customerId) { toast('Please select a client', 'error'); return; }
    try {
        await api('/quotations', {
            method: 'POST',
            body: JSON.stringify({
                customer_id: parseInt(customerId),
                package_name: document.getElementById('q_package').value,
                base_amount: parseFloat(document.getElementById('q_amount').value) || 0,
                discount: parseFloat(document.getElementById('q_discount').value) || 0,
                gst: parseFloat(document.getElementById('q_gst').value) || 0,
                notes: document.getElementById('q_notes').value,
                valid_until: document.getElementById('q_valid').value
            })
        });
        toast('Quotation created!');
        closeModal();
        loadQuotations();
        loadDashboard();
    } catch(e) { toast(e.message, 'error'); }
}

// ============================================
// Add Booking Form
// ============================================
async function showAddBooking() {
    let customers = [];
    try { customers = await api('/customers'); } catch(e) {}
    
    showModal('New Booking', `
        <div class="form-group"><label>Client *</label>
            <select id="b_customer">
                <option value="">Select client</option>
                ${customers.map(c => `<option value="${c.id}">${c.name} (${c.phone})</option>`).join('')}
            </select>
        </div>
        <div class="form-row">
            <div class="form-group"><label>Event Type</label><select id="b_event"><option value="Wedding">Wedding</option><option value="Engagement">Engagement</option><option value="Reception">Reception</option><option value="Pre-Wedding">Pre-Wedding</option><option value="Corporate">Corporate</option></select></div>
            <div class="form-group"><label>Event Date</label><input id="b_date" type="date"></div>
        </div>
        <div class="form-row">
            <div class="form-group"><label>Total Amount (₹)</label><input id="b_total" type="number" placeholder="e.g. 800000"></div>
            <div class="form-group"><label>Advance (₹)</label><input id="b_advance" type="number" placeholder="e.g. 200000"></div>
        </div>
        <div class="form-group"><label>Venue</label><input id="b_venue" placeholder="Venue name"></div>
        <div class="form-group"><label>Notes</label><textarea id="b_notes" rows="2"></textarea></div>
    `, `
        <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="saveBooking()">Confirm Booking</button>
    `);
}

async function saveBooking() {
    const customerId = document.getElementById('b_customer').value;
    if (!customerId) { toast('Please select a client', 'error'); return; }
    try {
        await api('/bookings', {
            method: 'POST',
            body: JSON.stringify({
                customer_id: parseInt(customerId),
                event_type: document.getElementById('b_event').value,
                event_date: document.getElementById('b_date').value,
                total_amount: parseFloat(document.getElementById('b_total').value) || 0,
                advance_amount: parseFloat(document.getElementById('b_advance').value) || 0,
                venue: document.getElementById('b_venue').value,
                notes: document.getElementById('b_notes').value
            })
        });
        toast('Booking confirmed!');
        closeModal();
        loadBookings();
        loadDashboard();
    } catch(e) { toast(e.message, 'error'); }
}

// ============================================
// Add Editing Project
// ============================================
async function showAddEditing() {
    let bookings = [], users = [];
    try { bookings = await api('/bookings'); users = await api('/users'); } catch(e) {}
    
    showModal('New Editing Project', `
        <div class="form-group"><label>Booking *</label>
            <select id="e_booking">
                <option value="">Select booking</option>
                ${bookings.filter(b => b.status === 'event_completed' || b.status === 'editing').map(b => `<option value="${b.id}">${b.booking_number} - ${b.customer?.name || ''}</option>`).join('')}
            </select>
        </div>
        <div class="form-row">
            <div class="form-group"><label>Editor</label>
                <select id="e_editor"><option value="">Select</option>${users.filter(u => u.role === 'editor').map(u => `<option value="${u.id}">${u.full_name}</option>`).join('')}</select>
            </div>
            <div class="form-group"><label>Designer</label>
                <select id="e_designer"><option value="">Select</option>${users.filter(u => u.role === 'album_designer' || u.role === 'editor').map(u => `<option value="${u.id}">${u.full_name}</option>`).join('')}</select>
            </div>
        </div>
        <div class="form-group"><label>Notes</label><textarea id="e_notes" rows="2"></textarea></div>
    `, `
        <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="saveEditing()">Create Project</button>
    `);
}

async function saveEditing() {
    const bookingId = document.getElementById('e_booking').value;
    if (!bookingId) { toast('Please select a booking', 'error'); return; }
    try {
        await api('/editing-projects', {
            method: 'POST',
            body: JSON.stringify({
                booking_id: parseInt(bookingId),
                editor_id: parseInt(document.getElementById('e_editor').value) || null,
                designer_id: parseInt(document.getElementById('e_designer').value) || null,
                editing_notes: document.getElementById('e_notes').value
            })
        });
        toast('Editing project created!');
        closeModal();
        loadEditing();
    } catch(e) { toast(e.message, 'error'); }
}

// ============================================
// Record Payment
// ============================================
async function recordPayment(bookingId) {
    showModal('Record Payment', `
        <div class="form-group"><label>Amount (₹)</label><input id="p_amount" type="number" placeholder="Enter amount"></div>
        <div class="form-row">
            <div class="form-group"><label>Type</label><select id="p_type"><option value="advance">Advance</option><option value="milestone">Milestone</option><option value="final">Final</option></select></div>
            <div class="form-group"><label>Method</label><select id="p_method"><option value="cash">Cash</option><option value="bank_transfer">Bank Transfer</option><option value="upi">UPI</option><option value="card">Card</option></select></div>
        </div>
        <div class="form-group"><label>Transaction ID</label><input id="p_txn" placeholder="Optional"></div>
        <div class="form-group"><label>Notes</label><textarea id="p_notes" rows="2"></textarea></div>
    `, `
        <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="savePayment(${bookingId})">Record Payment</button>
    `);
}

async function savePayment(bookingId) {
    const amount = parseFloat(document.getElementById('p_amount').value);
    if (!amount || amount <= 0) { toast('Enter a valid amount', 'error'); return; }
    try {
        await api('/payments', {
            method: 'POST',
            body: JSON.stringify({
                booking_id: bookingId,
                amount,
                payment_type: document.getElementById('p_type').value,
                payment_method: document.getElementById('p_method').value,
                transaction_id: document.getElementById('p_txn').value,
                notes: document.getElementById('p_notes').value
            })
        });
        toast(`Payment of ₹${amount.toLocaleString()} recorded!`);
        closeModal();
        loadPayments();
        loadBookings();
        loadDashboard();
    } catch(e) { toast(e.message, 'error'); }
}

// ============================================
// Search
// ============================================
let searchTimeout;
document.getElementById('searchInput').addEventListener('input', function() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const q = this.value.trim();
        if (CURRENT_SECTION === 'inquiries') loadInquiries();
        else if (CURRENT_SECTION === 'customers') loadCustomers();
    }, 300);
});

// ============================================
// Helpers
// ============================================
function timeAgo(dateStr) {
    if (!dateStr) return '';
    const now = new Date();
    const date = new Date(dateStr);
    const diff = Math.floor((now - date) / 1000);
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
    return date.toLocaleDateString('en-IN');
}

// ============================================
// Init
// ============================================
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    try {
        await login(username, password);
    } catch (err) {
        document.getElementById('loginError').textContent = err.message;
        document.getElementById('loginError').style.display = 'block';
    }
});

document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    logout();
});

// Auto-login if token exists
if (TOKEN) {
    const saved = localStorage.getItem('ts_user');
    if (saved) {
        CURRENT_USER = JSON.parse(saved);
        showApp();
        loadDashboard();
    } else {
        logout();
    }
}