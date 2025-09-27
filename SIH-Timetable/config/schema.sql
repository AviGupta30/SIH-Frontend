-- Create tables for our application

-- Students table
create table public.students (
    id uuid default uuid_generate_v4() primary key,
    name text not null,
    email text unique not null,
    phone text,
    section_id text not null,
    semester integer not null,
    notification_preferences jsonb default '{"email": true, "push": true}',
    learning_style text,
    location_tracking_enabled boolean default true,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Courses table
create table public.courses (
    id uuid default uuid_generate_v4() primary key,
    name text not null,
    teacher_id uuid not null,
    credits integer not null,
    has_lab boolean default false,
    can_be_online boolean default false,
    section_id text not null,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Rooms table
create table public.rooms (
    id uuid default uuid_generate_v4() primary key,
    name text not null,
    type text not null,
    capacity integer,
    has_ac boolean default false,
    has_projector boolean default false,
    building text not null,
    floor integer not null,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Schedules table
create table public.schedules (
    id uuid default uuid_generate_v4() primary key,
    course_id uuid references public.courses(id),
    room_id uuid references public.rooms(id),
    section_id text not null,
    day_of_week text not null,
    start_time time not null,
    end_time time not null,
    is_online boolean default false,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Attendance table
create table public.attendance (
    id uuid default uuid_generate_v4() primary key,
    student_id uuid references public.students(id),
    schedule_id uuid references public.schedules(id),
    status boolean not null,
    timestamp timestamp with time zone default timezone('utc'::text, now())
);

-- Weather logs table
create table public.weather_logs (
    id uuid default uuid_generate_v4() primary key,
    status text not null,
    temperature float not null,
    humidity float,
    wind_speed float,
    precipitation float,
    timestamp timestamp with time zone default timezone('utc'::text, now())
);

-- Notifications table
create table public.notifications (
    id uuid default uuid_generate_v4() primary key,
    student_id uuid references public.students(id),
    title text not null,
    message text not null,
    type text not null,
    read boolean default false,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Stored procedure for getting available rooms
create or replace function get_available_rooms(p_date date, p_time_slot text)
returns setof public.rooms as $$
begin
    return query
    select r.* from public.rooms r
    where r.id not in (
        select room_id from public.schedules
        where date(created_at) = p_date
        and start_time::text = p_time_slot
    );
end;
$$ language plpgsql;
