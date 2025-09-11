# NGO School Session Recording System - Implementation Plan

## Project Overview
A Django-based web application to track teaching sessions, attendance, and activities across multiple NGO school classes. The system includes form-based session recording, people directory, and automated file management.

## Application Structure

### Frontend Pages

**Sessions Page**
- Form for recording school session data
- Mobile-first interface with touch-friendly inputs
- Dynamic session modules (add/remove as needed)
- Real-time form validation

**People Directory Page**
- Grid layout of profile photo thumbnails
- Name, role badge, and school affiliation displayed
- Filtering by role, school, and active status
- Search functionality by name
- Responsive grid design

**Individual Profile Pages**
- Public view: photo, name, role, bio, school affiliation, recent sessions
- Edit mode: profile photo upload, bio editing (own profile only)
- URL structure: `/people/{person-id}/`

**School Profile Pages**
- School overview: name, palika, operating schedule, location map
- Interactive Google Maps embed with GPS coordinates
- Complete session history timeline with date filtering
- Teacher gallery: photos, names, bios, and average involvement ratings
- Class attendance trends and statistics
- Recent activity feed
- Photo gallery from all sessions
- URL structure: `/schools/{school-id}/`

## Session Recording Form Specification

### Core Information Section (Required)
- **Palika**: Dropdown from database
- **Date**: Date picker with auto-populated day of week
- **School**: Filtered dropdown (matching palika + operating day)
- **People Present**: Multi-select with role badges
- **Class Attendance**: Number inputs for classes 1-6

### Session Modules (Dynamic)
- **Class**: Dropdown (1-6)
- **Games**: Multi-select from games database
- **Time**: Auto-populated with manual override toggle
- **Images**: 3 upload slots (optional)
- **Teacher**: Dropdown + manual add option
- **Teacher Involvement**: 1-5 star rating
- **Remarks**: Text area (optional)

## Database Schema

### Schools Table
```
- id (primary key)
- name
- palika_name
- operating_days (JSON array)
- first_session_start_time
- second_session_start_time  
- class_duration (minutes)
- max_students_per_class
- address (text field)
- gps_latitude (decimal)
- gps_longitude (decimal)
- google_maps_url (text field)
- school_description (text area)
- contact_phone (optional)
- principal_id (foreign key to people table, optional)
```

### People Table (Unified)
```
- id (primary key)
- name
- email (for authentication)
- profile_photo (file path)
- bio (text field)
- role (teacher/principal/coordinator/intern/fellow/full-timer)
- school_id (foreign key, optional)
- active_status (boolean)
- additional_info (JSON field)
```

### Games Table
```
- id (primary key)
- game_name
- category (optional)
- age_group (optional)
```

### Sessions Table (One record per school per day)
```
- palika_name + school_id + session_date (composite primary key)
- day_of_week
- people_present (JSON array of people IDs)
- class_attendance (JSON: {class1: count, class2: count, ...})
- session_modules (JSON array):
  [
    {
      "class_number": 1,
      "games": [game_id1, game_id2],
      "start_time": "10:00",
      "end_time": "11:00", 
      "teacher_id": 123,
      "teacher_involvement_rating": 4,
      "remarks": "optional text",
      "image_paths": ["path1.jpg", "path2.jpg"]
    }
  ]
- created_on, created_by
- last_edited_on, last_edited_by
```

## Technical Implementation

### Tech Stack
- **Backend**: Django/Python
- **Database**: SQLite
- **Frontend**: HTML/CSS with minimal JavaScript
- **Image Processing**: ImageMagick via Python

### Smart Features
- **Cascading Dropdowns**: Palika → Schools → Default times
- **Permission System**: Edit access for people present + super admins
- **Mobile Optimization**: Touch-friendly inputs, large tap targets
- **Dynamic Teacher Database**: New entries auto-save to people table
- **Time Override Mode**: Manual time editing when defaults don't apply

### Image Processing Pipeline
1. Upload handling (any format)
2. EXIF data extraction
3. JPG conversion
4. Compression with ImageMagick
5. Resolution downscaling
6. Posterized version creation
7. Dual storage (original + posterized)
8. Auto-cleanup after 1 week (keep posterized only)

### File Storage Structure
```
/media/
  └── palika_name/
      └── school_name/
          └── year/
              └── month/
                  └── date/
                      ├── session_images/
                      │   ├── original_compressed/
                      │   └── posterized/
                      └── index.html
```

### User Authentication & Permissions
- Django authentication required for form editing
- Profile editing: users can edit own profiles only
- Form editing: accessible to people present in that session + admins
- Public viewing: profiles and generated session pages publicly accessible

## Backend Processing Flow

### Session Form Submission
1. Receive form data via Django view
2. Validate required fields and data integrity
3. Process and store uploaded images
4. Save session record to database
5. Generate public HTML representation
6. Create directory structure if needed
7. Store file paths and complete transaction

### Profile Management
- User registration/login via Django auth
- Profile photo upload with compression
- Bio editing with rich text support
- Role-based access control

## Implementation Phases

### Phase 1: Core Infrastructure
- Django project setup
- Database models and migrations
- Basic authentication system
- Session form structure (no images)

### Phase 2: Form Functionality  
- Cascading dropdown implementation
- Dynamic session modules
- Form validation and submission
- Basic file storage

### Phase 3: Image Processing
- Upload handling
- ImageMagick integration
- Dual storage system
- Auto-cleanup scheduling

### Phase 4: People & School Directories
- Profile photo management
- People index page
- Individual profile pages
- School profile pages with maps integration
- Teacher ratings aggregation
- Search and filtering

### Phase 5: Polish & Optimization
- Mobile responsiveness
- Performance optimization
- Error handling
- User experience refinements