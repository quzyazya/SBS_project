<%def name="render_calendar(calendar_data, current_user, year, month)">
<%
    from datetime import datetime, timedelta
    from calendar import monthrange
    import calendar as cal
    
    today = datetime.utcnow().date()
    
    display_date = datetime(year, month, 1)
    first_day_of_month = display_date
    start_weekday = first_day_of_month.weekday()
    days_in_month = monthrange(year, month)[1]
    
    # Предыдущий и следующий месяц
    if month == 1:
        prev_year = year - 1
        prev_month = 12
    else:
        prev_year = year
        prev_month = month - 1
    
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1
    
    # Создаём словарь {дата: список задач}
    tasks_by_date = {}
    for task in calendar_data:
        date_str = task['date']
        if date_str not in tasks_by_date:
            tasks_by_date[date_str] = []
        tasks_by_date[date_str].append(task)
    
    month_names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 
                   'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
%>

<div class="calendar">
    <div class="d-flex justify-content-between align-items-center mb-2">
        <a href="/?year=${prev_year}&month=${prev_month}" class="btn btn-sm btn-outline-secondary">&lt;</a>
        <span class="fw-bold">${month_names[month-1]} ${year}</span>
        <a href="/?year=${next_year}&month=${next_month}" class="btn btn-sm btn-outline-secondary">&gt;</a>
    </div>
    
    <div class="calendar-weekdays d-grid" style="grid-template-columns: repeat(7, 1fr); gap: 5px; margin-bottom: 5px;">
        <div class="text-center small fw-bold">Пн</div>
        <div class="text-center small fw-bold">Вт</div>
        <div class="text-center small fw-bold">Ср</div>
        <div class="text-center small fw-bold">Чт</div>
        <div class="text-center small fw-bold">Пт</div>
        <div class="text-center small fw-bold">Сб</div>
        <div class="text-center small fw-bold">Вс</div>
    </div>
    
    <div class="calendar-days d-grid" style="grid-template-columns: repeat(7, 1fr); gap: 5px;">
        % for i in range(start_weekday):
            <div class="text-center p-1 text-muted" style="min-height: 60px;"></div>
        % endfor
        
        % for day in range(1, days_in_month + 1):
            <%
                date_str = f"{year}-{month:02d}-{day:02d}"
                tasks_on_day = tasks_by_date.get(date_str, [])
                has_tasks = len(tasks_on_day) > 0
                is_today = (year == today.year and month == today.month and day == today.day)
                
                if has_tasks:
                    first_task = tasks_on_day[0]
                    color_class = first_task.get('color', 'secondary')
                    if color_class == 'red':
                        number_color = 'text-danger fw-bold'
                    elif color_class == 'orange':
                        number_color = 'text-warning fw-bold'
                    elif color_class == 'green':
                        number_color = 'text-success fw-bold'
                    else:
                        number_color = 'text-secondary'
                else:
                    number_color = 'text-secondary'
                
                if is_today:
                    number_color = 'bg-primary text-white rounded-circle d-inline-block'
            %>
            <div class="calendar-day text-center p-1 position-relative" style="min-height: 60px; border: 1px solid #e9ecef; border-radius: 8px;">
                <a href="/create-task?deadline=${date_str}" style="text-decoration: none; color: inherit;">
                    <div class="day-number ${number_color}" style="${'width: 28px; margin: 0 auto;' if is_today else ''}">${day}</div>
                </a>
                % for task in tasks_on_day:
                    <div class="task-badge mt-1" style="font-size: 10px; background-color: #f8f9fa; border-radius: 10px; padding: 2px 4px;">
                        % if task.get('number'):
                            <a href="/api/tasks/${task['id']}/edit-form" style="text-decoration: none; color: #0d6efd;">#${task['number']}</a>
                        % else:
                            <span class="text-muted" title="${task['title']}">✓</span>
                        % endif
                    </div>
                % endfor
            </div>
        % endfor
    </div>
</div>
</%def>