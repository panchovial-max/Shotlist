// Campaign Calendar JavaScript

let currentMonth = new Date();
let calendarEvents = [];

// Initialize calendar
function initializeCalendar() {
    renderCalendar();
    loadCalendarEvents();
}

// Render calendar grid
function renderCalendar() {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();

    // Update month display
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];
    document.getElementById('calendarMonth').textContent = `${monthNames[month]} ${year}`;

    // Get first day of month and number of days
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const daysInPrevMonth = new Date(year, month, 0).getDate();

    const calendarGrid = document.getElementById('calendarGrid');
    calendarGrid.innerHTML = '';

    // Add day headers
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    dayNames.forEach(day => {
        const header = document.createElement('div');
        header.className = 'calendar-day-header';
        header.textContent = day;
        calendarGrid.appendChild(header);
    });

    // Add previous month days
    for (let i = firstDay - 1; i >= 0; i--) {
        const day = daysInPrevMonth - i;
        const dayElement = createDayElement(day, 'other-month');
        calendarGrid.appendChild(dayElement);
    }

    // Add current month days
    const today = new Date();
    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(year, month, day);
        const isToday = date.toDateString() === today.toDateString();
        const dayElement = createDayElement(day, isToday ? 'today' : '');

        // Add events for this day
        const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const dayEvents = calendarEvents.filter(e => e.event_date === dateString);

        if (dayEvents.length > 0) {
            const eventsContainer = document.createElement('div');
            eventsContainer.className = 'calendar-events';

            dayEvents.slice(0, 3).forEach(event => {  // Show max 3 events
                const eventElement = document.createElement('div');
                eventElement.className = `calendar-event ${event.event_type}`;
                eventElement.textContent = event.event_title;
                eventElement.title = event.event_description;
                eventElement.onclick = () => showEventModal(event);
                eventsContainer.appendChild(eventElement);
            });

            if (dayEvents.length > 3) {
                const moreElement = document.createElement('div');
                moreElement.className = 'calendar-event';
                moreElement.textContent = `+${dayEvents.length - 3} more`;
                moreElement.style.background = '#F5F5F5';
                moreElement.style.color = '#737373';
                eventsContainer.appendChild(moreElement);
            }

            dayElement.appendChild(eventsContainer);
        }

        calendarGrid.appendChild(dayElement);
    }

    // Add next month days
    const remainingCells = 42 - (firstDay + daysInMonth); // 6 rows * 7 days
    for (let day = 1; day <= remainingCells; day++) {
        const dayElement = createDayElement(day, 'other-month');
        calendarGrid.appendChild(dayElement);
    }
}

// Create day element
function createDayElement(day, className) {
    const dayElement = document.createElement('div');
    dayElement.className = `calendar-day ${className}`;

    const dayNumber = document.createElement('div');
    dayNumber.className = 'calendar-day-number';
    dayNumber.textContent = day;
    dayElement.appendChild(dayNumber);

    return dayElement;
}

// Load calendar events from API
async function loadCalendarEvents() {
    const sessionId = localStorage.getItem('session_id');
    if (!sessionId) return;

    const year = currentMonth.getFullYear();
    const month = String(currentMonth.getMonth() + 1).padStart(2, '0');
    const monthString = `${year}-${month}`;

    try {
        const response = await fetch(`${API_BASE}/calendar?month=${monthString}`, {
            headers: {
                'X-Session-ID': sessionId
            }
        });

        const data = await response.json();

        if (data.events) {
            calendarEvents = data.events;
            renderCalendar();
            renderUpcomingEvents();
        }
    } catch (error) {
        console.error('Error loading calendar events:', error);
    }
}

// Navigate calendar
function previousMonth() {
    currentMonth.setMonth(currentMonth.getMonth() - 1);
    renderCalendar();
    loadCalendarEvents();
}

function nextMonth() {
    currentMonth.setMonth(currentMonth.getMonth() + 1);
    renderCalendar();
    loadCalendarEvents();
}

function goToToday() {
    currentMonth = new Date();
    renderCalendar();
    loadCalendarEvents();
}

// Show event modal
function showEventModal(event) {
    const modal = document.getElementById('eventModal');

    document.getElementById('modalEventTitle').textContent = event.event_title;
    document.getElementById('modalEventDescription').textContent = event.event_description || 'No description';
    document.getElementById('modalEventDate').textContent = formatDate(event.event_date);
    document.getElementById('modalEventTime').textContent = event.event_time || 'All day';
    document.getElementById('modalEventType').textContent = formatEventType(event.event_type);
    document.getElementById('modalEventCampaign').textContent = event.campaign_name || 'General';

    const priorityBadge = document.getElementById('modalEventPriority');
    priorityBadge.textContent = event.priority.toUpperCase();
    priorityBadge.className = `event-badge ${event.priority}`;

    modal.classList.add('active');
}

// Close event modal
function closeEventModal() {
    document.getElementById('eventModal').classList.remove('active');
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString + 'T00:00:00');
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Format event type
function formatEventType(type) {
    const types = {
        'campaign_start': 'Campaign Launch',
        'campaign_end': 'Campaign End',
        'meeting': 'Meeting',
        'deadline': 'Deadline',
        'milestone': 'Milestone'
    };
    return types[type] || type;
}

// Render upcoming events
function renderUpcomingEvents() {
    const container = document.getElementById('upcomingEventsList');
    if (!container) return;

    // Get upcoming events (next 7 days)
    const today = new Date();
    const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);

    const upcoming = calendarEvents
        .filter(e => {
            const eventDate = new Date(e.event_date + 'T00:00:00');
            return eventDate >= today && eventDate <= nextWeek;
        })
        .sort((a, b) => new Date(a.event_date) - new Date(b.event_date))
        .slice(0, 5);

    if (upcoming.length === 0) {
        container.innerHTML = '<p style="color: #737373; text-align: center;">No upcoming events</p>';
        return;
    }

    container.innerHTML = '';

    upcoming.forEach(event => {
        const date = new Date(event.event_date + 'T00:00:00');
        const day = date.getDate();
        const month = date.toLocaleDateString('en-US', { month: 'short' });

        const item = document.createElement('div');
        item.className = 'upcoming-event-item';
        item.onclick = () => showEventModal(event);

        item.innerHTML = `
            <div class="upcoming-event-date">
                <div class="upcoming-event-day">${day}</div>
                <div class="upcoming-event-month">${month}</div>
            </div>
            <div class="upcoming-event-details">
                <div class="upcoming-event-title">${event.event_title}</div>
                <div class="upcoming-event-time">
                    ${event.event_time || 'All day'} • ${formatEventType(event.event_type)}
                    ${event.campaign_name ? ` • ${event.campaign_name}` : ''}
                </div>
            </div>
        `;

        container.appendChild(item);
    });
}

// Export for use in dashboard
window.calendarAPI = {
    initialize: initializeCalendar,
    previousMonth: previousMonth,
    nextMonth: nextMonth,
    goToToday: goToToday,
    closeModal: closeEventModal
};
