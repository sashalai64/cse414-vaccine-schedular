def reserve(tokens):
    # reserve <date> <vaccine>
    # check 1: check if the current logged-in user is a patient
    if current_caregiver:
        print("Please login as a patient")
        return
    if current_patient is None:
        print("Please login first")
        return
    
    # check 2: the length for tokens need to be exactly 3
    if len(tokens) != 3:
        print("Please try again")
        return

    date = tokens[1]
    vaccine_name = tokens[2]
    
    date_tokens = date.split("-")

    try:
        # Make sure we have the right format
        if len(date_tokens) != 3:
            print("Please try again")
            return
            
        year = int(date_tokens[0])
        month = int(date_tokens[1])
        day = int(date_tokens[2])
        d = f"{year}-{month:02d}-{day:02d} 00:00:00"
        
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        # First check if the exact date format exists in Availabilities
        cursor.execute("SELECT * FROM Availabilities WHERE Time = ?", (d,))
        existing_avails = cursor.fetchall()
        print(f"DEBUG: Found {len(existing_avails)} availabilities matching this exact date format")
        
        # Check if there's any available caregiver
        available_caregiver_query = """
            SELECT A.Username
            FROM Availabilities AS A
            WHERE A.Time = ?
            AND A.Username NOT IN (
                SELECT R.Cusername
                FROM Reservations AS R
                WHERE R.Time = ?
            )
            ORDER BY A.Username
            LIMIT 1
        """
        cursor.execute(available_caregiver_query, (d, d))
        caregiver_row = cursor.fetchone()
        
        if caregiver_row is None:
            print("No caregiver is available")
            cm.close_connection()
            return
        
        caregiver_username = caregiver_row['Username']
        print(f"DEBUG: Found available caregiver: {caregiver_username}")
        
        # Check if the vaccine exists and has available doses
        vaccine = None
        try:
            vaccine = Vaccine(vaccine_name, 0).get()
            if vaccine is None:
                print("Please try again")
                cm.close_connection()
                return
                
            if vaccine.get_available_doses() <= 0:
                print("Not enough available doses")
                cm.close_connection()
                return
                
        except sqlite3.Error as e:
            print("Please try again")
            cm.close_connection()
            return
        except Exception as e:
            print("Please try again")
            cm.close_connection()
            return
        
        patient_username = current_patient.get_username()

        # If we get here, we have an available caregiver and vaccine doses
        # Make the reservation
        try:
            print(f"DEBUG: Creating reservation with Time={d}, Caregiver={caregiver_username}, Patient={patient_username}, Vaccine={vaccine_name}")
            
            # Double-check availability exists and matches format exactly
            check_avail = "SELECT * FROM Availabilities WHERE Time = ? AND Username = ?"
            cursor.execute(check_avail, (d, caregiver_username))
            avail_exists = cursor.fetchone()
            
            if not avail_exists:
                print(f"DEBUG: CRITICAL ERROR - No matching availability for Time={d}, Username={caregiver_username}")
                print("Please try again")
                cm.close_connection()
                return
            else:
                print(f"DEBUG: Confirmed availability exists in exact format: {avail_exists['Time']}")
            reservation = Reservation(time=d, cusername=caregiver_username, pusername=patient_username, vname=vaccine_name)
            reservation.save_to_db()

            # Decrease vaccine doses by 1
            vaccine.decrease_available_doses(1)

            print(f"Appointment ID {reservation.get_id()}, Caregiver username {caregiver_username}")

        except sqlite3.Error as e:
            print(f"DEBUG: SQLite error when creating reservation: {e}")
            print("Please try again")
            cm.close_connection()
            return
        except Exception as e:
            print(f"DEBUG: Error when creating reservation: {e}")
            print("Please try again")
            cm.close_connection()
            return
                
        cm.close_connection()
    
    except ValueError:
        print("DEBUG: ValueError in date parsing")
        print("Please try again")
        return
    except Exception as e:
        print(f"DEBUG: Unexpected error: {e}")
        print("Please try again")
        return