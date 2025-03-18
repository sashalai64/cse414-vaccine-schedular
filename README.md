# Python Application for Vaccine Scheduler

## Overview
This project is a command-line appointment scheduler for vaccinations. It allows patients to schedule appointments while caregivers manage appointment slots and vaccine inventory.

The application connects to a local SQLite database, which stores all relevant data, including users, reservations, and vaccine stock levels.

## Features
- **User Authentication**
  - Supports register and login for both patients and caregivers

- **Caregiver Functionality**
  - Search for available caregivers by date
  - Manage vaccine stock
  - Open appointment slots
  - View scheduled appointments
  - Cancel scheduled appointments

- **Patient Functionality**
  - Search for available caregivers by date
  - Schedule a vaccination appointment with available caregivers
  - View scheduled appointments
  - Cancel scheduled appointments



- **Database Integration**
  - Uses SQLite to store users, appointments, and vaccine inventory


## Database Schema
The application uses a SQLite database with the following tables:

[Database Design](https://github.com/sashalai64/cse414-vaccine-schedular/blob/211c2853a159732c06a09f3695831c2c2362af1d/src/main/resources/design.pdf)

- **Caregivers**: Stores caregiver credentials and information
- **Patients**: Stores patient credentials and information
- **Availabilities**: Tracks which caregivers are available on which dates
- **Vaccines**: Tracks vaccines and their available doses
- **Reservations**: Stores appointment information linking patients, caregivers, and vaccines


## Usage

### Prerequisites
- Python
- SQLite3

### Setup
1. Clone this repository
2. Run ```python your_path_to/vaccine-scheduler-python-main/src/main/scheduler/Scheduler.py``` to start the application

### Commands
```
> create_patient <username> <password>       # Create a new patient account
> create_caregiver <username> <password>     # Create a new caregiver account
> login_patient <username> <password>        # Login as a patient
> login_caregiver <username> <password>      # Login as a caregiver
> search_caregiver_schedule <date>           # Check available caregivers on a date (YYY-MM-DD)
> reserve <date> <vaccine>                   # Make a vaccination appointment (YYY-MM-DD)
> upload_availability <date>                 # Upload caregiver availability (YYY-MM-DD)
> cancel <appointment_id>                    # Cancel an appointment
> add_doses <vaccine> <number>               # Add doses to vaccine inventory
> show_appointments                          # Show current user's appointments
> logout                                     # Logout current user
> quit                                       # Exit application
```

### Example Workflow
#### Caregiver Workflow:
```
> create_caregiver c1 cpw1
> login_caregiver c1 cpw1
> upload_availability 2023-03-20
> add_doses covid 100
> show_appointments
> logout
```
#### Patient Workflow:
```
> create_patient p1 ppw1
> login_patient p1 ppw1
> search_caregiver_schedule 2023-03-20
> reserve 2023-03-20 covid
> show_appointments
> logout
```
