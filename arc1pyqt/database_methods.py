import sqlite3
from datetime import datetime
import pytz

#This is the template structure of the database
def database_structure_template(db_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    # Experiment table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Experiment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_name TEXT NOT NULL
        )
    ''')

    # Experimental detail table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Experimental_Detail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            resistance REAL,
            amplitude_V REAL,
            pulse_width_s REAL,
            tag TEXT NOT NULL,
            readtag TEXT,
            readvoltage REAL,
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # Material table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Material (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            top TEXT,
            bottom TEXT,
            insulator TEXT,
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # Size table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Size (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            cross_sectional_area TEXT,
            thickness REAL,
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # Process table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Process (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            temperature REAL,
            additional_parameters TEXT,
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # Location table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Location (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            wafer TEXT,
            die TEXT,
            wordline INTEGER,
            bitline INTEGER,
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # Read function table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Read_Function (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            read_type TEXT,                   -- read_type (e.g., TIA4P )
            read_voltage REAL,                -- Read voltage (e.g., 0.20 V)
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # Pulsing function table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Pulsing_Function (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            positive_pulse_voltage_V REAL,      -- Positive pulse voltage (V)
            positive_pulse_duration REAL,       -- Positive pulse duration
            positive_duration_unit TEXT,        -- Positive duration unit (us, ms, etc.)
            negative_pulse_voltage_V REAL,      -- Negative pulse voltage (V)
            negative_pulse_duration REAL,       -- Negative pulse duration
            negative_duration_unit TEXT,        -- Negative duration unit (us, ms, etc.)
            lock BOOLEAN,                       -- Lock option (True/False for whether Lock is enabled)
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')
    # FormFinder function table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS FormFinder_Function (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            voltage_min_V REAL,
            voltage_step_V REAL,
            voltage_max_V REAL,
            pulse_width_min_us REAL,
            pulse_width_step_percent REAL,
            pulse_width_max_us REAL,
            interpulse_time_ms REAL,
            nr_of_pulses INTEGER,
            resistance_threshold REAL,
            resistance_threshold_percent REAL,
            series_resistance TEXT,
            pulse_width_progression TEXT,
            negative_amplitude BOOLEAN,
            use_rthr BOOLEAN,
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # CurveTracer function table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CurveTracer_Function (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            positive_voltage_max_V REAL,
            negative_voltage_max_V REAL,
            voltage_step_V REAL,
            start_voltage_V REAL,
            step_width_ms REAL,
            cycles INTEGER,
            interpulse_time_ms REAL,
            positive_current_cutoff_uA REAL,
            negative_current_cutoff_uA REAL,
            halt_and_return BOOLEAN,
            bias_type TEXT,
            iv_span TEXT,
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # ParameterFit function table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ParameterFit_Function (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            pulses INTEGER,
            pulse_width_s REAL,
            bias_interpulse_s REAL,
            iv_interpulse_s REAL,
            iv_pulse_width_s REAL,
            iv_type TEXT,
            iv_start_V REAL,
            iv_step_V REAL,
            run_iv BOOLEAN,
            positive_polarity_v_start_V REAL,
            positive_polarity_v_step_V REAL,
            positive_polarity_v_stop_V REAL,
            positive_polarity_iv_stop_V REAL,
            negative_polarity_v_start_V REAL,
            negative_polarity_v_step_V REAL,
            negative_polarity_v_stop_V REAL,
            negative_polarity_iv_stop_V REAL,
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # Create the template for SwitchSeeker_Function table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SwitchSeeker_Function (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            reads_in_trailer_card INTEGER,
            programming_pulses INTEGER,
            pulse_duration_ms REAL,
            voltage_min_V REAL,
            voltage_step_V REAL,
            voltage_max_V REAL,
            max_switching_cycles INTEGER,
            tolerance_band_percent REAL,
            interpulse_time_ms REAL,
            resistance_threshold INTEGER,
            seeker_algorithm TEXT,
            stage_II_polarity TEXT,
            skip_stage_I BOOLEAN,
            read_after_pulse BOOLEAN,
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # ConvergeToState function table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ConvergeToState_Function (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            target_R INTEGER,            -- Target resistance
            initial_polarity TEXT,       -- Initial polarity (Positive/Negative)
            pw_min_ms REAL,              -- Pulse width minimum (ms)
            pw_step_percent REAL,        -- Pulse width step (%)
            pw_max_ms REAL,              -- Pulse width maximum (ms)             
            interpulse_time_ms REAL,     -- Interpulse time (ms)            
            rt_tolerance_percent REAL,   -- Rt tolerance (%)
            ro_tolerance_percent REAL,   -- Ro tolerance (%)            
            voltage_min_V REAL,          -- Voltage minimum (V)
            voltage_step_V REAL,         -- Voltage step (V)
            voltage_max_V REAL,          -- Voltage maximum (V)
            pulses INTEGER,              -- Number of pulses
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # Chronoamperometry function table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Chronoamperometry_Function (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            bias_V REAL,                 -- Bias voltage
            bias_duration REAL,          -- Bias duration
            duration_unit TEXT,          -- Duration unit (s/ms/us)
            number_of_reads INTEGER,     -- Number of reads
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # Endurance function table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Endurance_Function (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            positive_pulse_amplitude_V REAL,      -- Positive pulse amplitude (V)
            positive_pulse_width_us REAL,         -- Positive pulse width (us)
            positive_current_cutoff_uA REAL,      -- Positive current cut-off (uA)
            num_positive_pulses INTEGER,          -- Number of positive pulses
            cycles INTEGER,                       -- Number of cycles
            interpulse_time_ms REAL,              -- Interpulse time (ms)
            negative_pulse_amplitude_V REAL,      -- Negative pulse amplitude (V)
            negative_pulse_width_us REAL,         -- Negative pulse width (us)
            negative_current_cutoff_uA REAL,      -- Negative current cut-off (uA)
            num_negative_pulses INTEGER,          -- Number of negative pulses
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # MultiBias function table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MultiBias_Function (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            active_wordlines TEXT,             -- Active Wordlines (e.g., "1 2")
            active_bitline INTEGER,            -- Active Bitline
            write_amplitude_V REAL,            -- WRITE amplitude (V)
            write_pulse_width_us REAL,         -- WRITE pulse width (us)
            read_voltage_V REAL,               -- READ voltage (V)
            current_on_active_bitline_uA REAL, -- Current on Active Bitline (uA)
            read_or_write TEXT,                -- read or write the user type
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # MultiStateSeeker function table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MultiStateSeeker_Function (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            single_phase_run BOOLEAN,            -- Single phase run (checkbox)
            phase TEXT,                          -- Phase (Phase I, II, III)
    
            -- Phase I - Polarity inference
            phase_I_reads INTEGER,               -- Reads
            phase_I_prog_pulses INTEGER,         -- Programming pulses
            phase_I_pulse_width_ms REAL,         -- Pulse width (ms)
            phase_I_voltage_min_V REAL,          -- Voltage min (V)
            phase_I_voltage_step_V REAL,         -- Voltage step (V)
            phase_I_voltage_max_V REAL,          -- Voltage max (V)
            phase_I_interpulse_ms REAL,          -- Interpulse time (ms)
            phase_I_tolerance_band_percent REAL, -- Tolerance band (%)
            phase_I_read_after_pulse BOOLEAN,    -- Read after pulse (checkbox)
    
            -- Phase II - Pulsed stability calibration
            phase_II_pulse_voltage_V REAL,       -- Pulse voltage (V)
            phase_II_pulse_width_ms REAL,        -- Pulse width (ms)
            phase_II_state_mode TEXT,            -- State mode (As calculated, etc.)
            phase_II_stability_test TEXT,        -- Stability test (Linear fit, etc.)
            phase_II_max_time INTEGER,           -- Max time (s)
            phase_II_tolerance_percent REAL,     -- Tolerance (%)
    
            -- Phase III - State assessment
            phase_III_mode TEXT,                 -- Mode (Voltage sweep, etc.)
            phase_III_reads INTEGER,             -- Reads
            phase_III_max_prog_pulses INTEGER,   -- Max Programming pulses
            phase_III_pulse_width_ms REAL,       -- Pulse width (ms)
            phase_III_voltage_bias_V REAL,       -- Voltage bias (V)
            phase_III_voltage_min_V REAL,        -- Voltage min (V)
            phase_III_voltage_step_V REAL,       -- Voltage step (V)
            phase_III_voltage_max_V REAL,        -- Voltage max (V)
            phase_III_interpulse_ms REAL,        -- Interpulse time (ms)
            phase_III_retention_time REAL,       -- Retention time
            phase_III_retention_unit TEXT,       -- Retention time unit (ms, s, etc.)
            phase_III_std_deviations TEXT,       -- Standard deviations (e.g., 3σ)
            phase_III_monotonicity TEXT,         -- Monotonicity (Stop on reversal, etc.)
            phase_III_reset_counter BOOLEAN,     -- Reset counter after step? (checkbox)
    
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # VolatilityRead function table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS VolatilityRead_Function (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            pulse_amplitude_V REAL,           -- Pulse Amplitude (V)
            pulse_width_us REAL,              -- Pulse Width (us)
            read_batch_size INTEGER,          -- Read Batch Size (B)
            avg_cycles_per_point_M INTEGER,   -- Average cycles per point M
            stop_time_s REAL,                 -- Stop time (s)
            stop_t_metric REAL,               -- Stop t-metric
            stop_tolerance_percent REAL,      -- Stop Tolerance (%/batch)
            stop_option TEXT,                 -- Stop Option (e.g., LinearFit)
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')

    # Retention function table template
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Retention_Function (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            read_every INTEGER,            -- Read every (value)
            read_every_unit TEXT,          -- Read every unit (s, ms, etc.)
            read_for INTEGER,              -- Read for (value)
            read_for_unit TEXT,            -- Read for unit (min, s, etc.)
            FOREIGN KEY (experiment_id) REFERENCES Experiment(id)
        )
    ''')


#This is the first location of the experiment
def inserting_data_into_database_setFirstLocation(db_file, wafer, die, CB_word, CB_bit):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)


    # Query to get the latest experiment_id from the Experiment table
    cursor.execute('''
           SELECT MAX(id) FROM Experiment
       ''')

    # Fetch the result (the latest experiment ID)
    latest_experiment_id = cursor.fetchone()[0]


    # Insert Location data:
    cursor.execute('''
        INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
        VALUES (?, ?, ?, ?, ?)
    ''', (latest_experiment_id, wafer, die, CB_word, CB_bit))

    # Commit the transaction
    conn.commit()
    conn.close()

def inserting_data_into_database_allFunction_experimentalDetail(db_file, resistance, amplitude, pulse_width,
                                                                          tag, readTag, readVoltage):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)


    # Query to get the latest experiment_id from the Experiment table
    cursor.execute('''
           SELECT MAX(id) FROM Experiment
       ''')

    # Fetch the result (the latest experiment ID)
    latest_experiment_id = cursor.fetchone()[0]

    # Experimental_Detail table Part:
    # Insert records into the Experimental_Detail table
    cursor.execute('''
        INSERT INTO Experimental_Detail (
            experiment_id, resistance, amplitude_V, pulse_width_s, tag, readtag, readvoltage
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        latest_experiment_id, resistance, amplitude, pulse_width,
        tag, readTag, readVoltage
    ))

    # Commit the transaction
    conn.commit()
    conn.close()

def inserting_data_into_database_single_and_all_Read(db_file, wafer, insulator, cross_sectional_area, die, CB_word, CB_bit,
                                                     resistance, amplitude, pulse_width, tag, readTag, readVoltage,
                                                     read_type, read_voltage):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)

    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'Read_Single_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'Read_Single_{current_time_uk}_1'
    else:
        experiment_name = f'Read_Single_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))

    # Insert Location data:
    cursor.execute('''
        INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_experiment_id, wafer, die, CB_word, CB_bit))

    # Insert data into the Read_Function table
    cursor.execute('''
        INSERT INTO Read_Function (
            experiment_id, read_type, read_voltage
        ) VALUES (?, ?, ?)
    ''', (current_experiment_id, read_type, read_voltage))

    # Experimental_Detail table Part:
    # Insert records into the Experimental_Detail table
    cursor.execute('''
        INSERT INTO Experimental_Detail (
            experiment_id, resistance, amplitude_V, pulse_width_s, tag, readtag, readvoltage
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        current_experiment_id, resistance, amplitude, pulse_width,
        tag, readTag, readVoltage
    ))

    # Commit the transaction
    conn.commit()
    conn.close()

def inserting_data_into_database_pulse(db_file, wafer, insulator, cross_sectional_area, die, CB_word, CB_bit,
                                       resistance, amplitude, pulse_width, tag, readTag, readVoltage,
                                       positive_pulse_voltage_V, positive_pulse_duration,
                                       positive_duration_unit, negative_pulse_voltage_V, negative_pulse_duration,
                                       negative_duration_unit, lock):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)

    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'Pulse_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'Pulse_{current_time_uk}_1'
    else:
        experiment_name = f'Pulse_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))

    # Insert Location data:
    cursor.execute('''
        INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_experiment_id, wafer, die, CB_word, CB_bit))

    # Insert data into the Pulsing_Function table
    cursor.execute('''
        INSERT INTO Pulsing_Function (
            experiment_id, positive_pulse_voltage_V, positive_pulse_duration, positive_duration_unit,
            negative_pulse_voltage_V, negative_pulse_duration, negative_duration_unit, lock
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (current_experiment_id, positive_pulse_voltage_V, positive_pulse_duration, positive_duration_unit,
          negative_pulse_voltage_V, negative_pulse_duration, negative_duration_unit, lock))

    # Experimental_Detail table Part:
    # Insert records into the Experimental_Detail table
    cursor.execute('''
        INSERT INTO Experimental_Detail (
            experiment_id, resistance, amplitude_V, pulse_width_s, tag, readtag, readvoltage
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        current_experiment_id, resistance, amplitude, pulse_width,
        tag, readTag, readVoltage
    ))

    # Commit the transaction
    conn.commit()
    conn.close()


def inserting_data_into_database_singleRead_FormFinder_setParameters(db_file, insulator, cross_sectional_area, left_1,
                                                                     left_2, left_3, left_4, left_5, left_6, left_7,
                                                                     right_1, right_2, right_3, right_4, right_5,
                                                                     right_6, right_7):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)


    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'FormFinder_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'FormFinder_{current_time_uk}_1'
    else:
        experiment_name = f'FormFinder_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))


    # Insert parameters into FormFinder_Function table
    cursor.execute('''
        INSERT INTO FormFinder_Function (
            experiment_id, voltage_min_V, voltage_step_V, voltage_max_V, pulse_width_min_us, 
            pulse_width_step_percent, pulse_width_max_us, interpulse_time_ms, nr_of_pulses,
            resistance_threshold, resistance_threshold_percent, series_resistance, pulse_width_progression,
            negative_amplitude, use_rthr
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (current_experiment_id, left_1, left_2, left_3, left_4, left_5, left_6,
                                           left_7, right_1, right_2, right_3, right_4, right_5, right_6, right_7))


    # Commit the transaction
    conn.commit()
    conn.close()
def inserting_data_into_database_allOrRangeRead_FormFinder_setParameters(db_file, wafer, insulator, cross_sectional_area,
                                                                      die, CB_word, CB_bit):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)


    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'FormFinder_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'FormFinder_{current_time_uk}_1'
    else:
        experiment_name = f'FormFinder_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))

    # Insert Location data:
    cursor.execute('''
        INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_experiment_id, wafer, die, CB_word, CB_bit))

    # Insert data into the FormFinder_Function table with values identical to the last record
    # Select only the specific columns you need
    cursor.execute('''
        SELECT voltage_min_V, voltage_step_V, voltage_max_V, pulse_width_min_us, pulse_width_step_percent,
               pulse_width_max_us, interpulse_time_ms, nr_of_pulses, resistance_threshold, 
               resistance_threshold_percent, series_resistance, pulse_width_progression,
               negative_amplitude, use_rthr
        FROM FormFinder_Function 
        WHERE experiment_id = (SELECT MAX(experiment_id) FROM FormFinder_Function)
    ''')

    last_record = cursor.fetchone()

    if last_record:
        # Unpack the values from the last record
        (
            voltage_min_V, voltage_step_V, voltage_max_V, pulse_width_min_us, pulse_width_step_percent,
            pulse_width_max_us, interpulse_time_ms, nr_of_pulses, resistance_threshold,
            resistance_threshold_percent, series_resistance, pulse_width_progression,
            negative_amplitude, use_rthr
        ) = last_record

        # Insert a new record with the same values as the previous one, but with a new experiment_id
        cursor.execute('''
            INSERT INTO FormFinder_Function (
                experiment_id, voltage_min_V, voltage_step_V, voltage_max_V, pulse_width_min_us, 
                pulse_width_step_percent, pulse_width_max_us, interpulse_time_ms, nr_of_pulses,
                resistance_threshold, resistance_threshold_percent, series_resistance, pulse_width_progression,
                negative_amplitude, use_rthr
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            current_experiment_id,  # Use the new experiment_id
            voltage_min_V,          # Copy values from the last record
            voltage_step_V,
            voltage_max_V,
            pulse_width_min_us,
            pulse_width_step_percent,
            pulse_width_max_us,
            interpulse_time_ms,
            nr_of_pulses,
            resistance_threshold,
            resistance_threshold_percent,
            series_resistance,
            pulse_width_progression,
            negative_amplitude,
            use_rthr
        ))

    # Commit the transaction
    conn.commit()
    conn.close()

def inserting_data_into_database_singleRead_CurveTracer_setParameters(db_file, insulator, cross_sectional_area,
                                                                      positive_voltage_max_V,
                                                                      negative_voltage_max_V, voltage_step_V,
                                                                      start_voltage_V, step_width_ms, cycles,
                                                                      interpulse_time_ms, positive_current_cutoff_uA,
                                                                      negative_current_cutoff_uA, halt_and_return,
                                                                      bias_type, iv_span):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)


    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'CurveTracer_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'CurveTracer_{current_time_uk}_1'
    else:
        experiment_name = f'CurveTracer_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))

    # # Insert Location data:
    # cursor.execute('''
    #     INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
    #     VALUES (?, ?, ?, ?, ?)
    # ''', (current_experiment_id, wafer, die, CB_word, CB_bit))

    # Insert data into the CurveTracer_Function table
    cursor.execute('''
        INSERT INTO CurveTracer_Function (
            experiment_id, positive_voltage_max_V, negative_voltage_max_V, voltage_step_V, start_voltage_V,
            step_width_ms, cycles, interpulse_time_ms, positive_current_cutoff_uA, negative_current_cutoff_uA,
            halt_and_return, bias_type, iv_span
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        current_experiment_id,  # Foreign key from the Experiment table
        positive_voltage_max_V,  # Maximum positive voltage (V)
        negative_voltage_max_V,  # Maximum negative voltage (V)
        voltage_step_V,          # Voltage step (V)
        start_voltage_V,         # Starting voltage (V)
        step_width_ms,            # Step width (ms)
        cycles,                  # Number of cycles
        interpulse_time_ms,       # Interpulse time (ms)
        positive_current_cutoff_uA, # Positive current cutoff (uA)
        negative_current_cutoff_uA, # Negative current cutoff (uA)
        halt_and_return,         # Boolean flag for halting and returning
        bias_type,               # Bias type (e.g., 'Staircase')
        iv_span                  # IV span (e.g., 'Start towards V+')
    ))


    # Commit the transaction
    conn.commit()
    conn.close()
def inserting_data_into_database_allOrRangeRead_CurveTracer_setParameters(db_file, wafer, insulator, cross_sectional_area,
                                                                      die, CB_word, CB_bit):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)


    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'CurveTracer_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'CurveTracer_{current_time_uk}_1'
    else:
        experiment_name = f'CurveTracer_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))

    # Insert Location data:
    cursor.execute('''
        INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_experiment_id, wafer, die, CB_word, CB_bit))

    # Insert data into the CurveTracer_Function table with values identical to the last record
    # Select only the specific columns you need
    cursor.execute('''
        SELECT positive_voltage_max_V, negative_voltage_max_V, voltage_step_V, start_voltage_V,
               step_width_ms, cycles, interpulse_time_ms, positive_current_cutoff_uA, negative_current_cutoff_uA,
               halt_and_return, bias_type, iv_span
        FROM CurveTracer_Function 
        WHERE experiment_id = (SELECT MAX(experiment_id) FROM CurveTracer_Function)
    ''')

    last_record = cursor.fetchone()

    if last_record:
        # Unpack the values from the last record
        (
            positive_voltage_max_V, negative_voltage_max_V, voltage_step_V, start_voltage_V,
            step_width_ms, cycles, interpulse_time_ms, positive_current_cutoff_uA, negative_current_cutoff_uA,
            halt_and_return, bias_type, iv_span
        ) = last_record

        # Insert a new record with the same values as the previous one, but with a new experiment_id
        cursor.execute('''
            INSERT INTO CurveTracer_Function (
                experiment_id, positive_voltage_max_V, negative_voltage_max_V, voltage_step_V, start_voltage_V,
                step_width_ms, cycles, interpulse_time_ms, positive_current_cutoff_uA, negative_current_cutoff_uA,
                halt_and_return, bias_type, iv_span
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            current_experiment_id,  # Use the new experiment_id
            positive_voltage_max_V,  # Copy values from the last record
            negative_voltage_max_V,
            voltage_step_V,
            start_voltage_V,
            step_width_ms,
            cycles,
            interpulse_time_ms,
            positive_current_cutoff_uA,
            negative_current_cutoff_uA,
            halt_and_return,
            bias_type,
            iv_span
        ))

    # Commit the transaction
    conn.commit()
    conn.close()


def inserting_data_into_database_singleRead_ParameterFit_setParameters(db_file, insulator,cross_sectional_area, pulses,
                                                                       pulse_width_s, bias_interpulse_s, iv_interpulse_s,
                                                                       iv_pulse_width_s, iv_type,iv_start_V, iv_step_V,
                                                                       run_iv, positive_polarity_v_start_V,
                                                                       positive_polarity_v_step_V,
                                                                       positive_polarity_v_stop_V,
                                                                       positive_polarity_iv_stop_V,
                                                                       negative_polarity_v_start_V,
                                                                       negative_polarity_v_step_V,
                                                                       negative_polarity_v_stop_V,
                                                                       negative_polarity_iv_stop_V):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)


    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'ParameterFit_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'ParameterFit_{current_time_uk}_1'
    else:
        experiment_name = f'ParameterFit_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))


    # Insert data into the ParameterFit_Function table
    cursor.execute('''
        INSERT INTO ParameterFit_Function (
            experiment_id, pulses, pulse_width_s, bias_interpulse_s, iv_interpulse_s, iv_pulse_width_s, iv_type, 
            iv_start_V, iv_step_V, run_iv, positive_polarity_v_start_V, positive_polarity_v_step_V, 
            positive_polarity_v_stop_V, positive_polarity_iv_stop_V, negative_polarity_v_start_V, 
            negative_polarity_v_step_V, negative_polarity_v_stop_V, negative_polarity_iv_stop_V
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        current_experiment_id,       # Foreign key from Experiment table
        pulses,                      # Number of pulses
        pulse_width_s,               # Pulse width in seconds
        bias_interpulse_s,           # Bias interpulse time in seconds
        iv_interpulse_s,             # IV interpulse time in seconds
        iv_pulse_width_s,            # IV pulse width in seconds
        iv_type,                     # Type of IV (e.g., 'Staircase')
        iv_start_V,                  # IV starting voltage
        iv_step_V,                   # IV step voltage
        run_iv,                      # Boolean for running IV or not
        positive_polarity_v_start_V, # Positive polarity starting voltage
        positive_polarity_v_step_V,  # Positive polarity step voltage
        positive_polarity_v_stop_V,  # Positive polarity stopping voltage
        positive_polarity_iv_stop_V, # Positive polarity IV stopping voltage
        negative_polarity_v_start_V, # Negative polarity starting voltage
        negative_polarity_v_step_V,  # Negative polarity step voltage
        negative_polarity_v_stop_V,  # Negative polarity stopping voltage
        negative_polarity_iv_stop_V  # Negative polarity IV stopping voltage
    ))

    # Commit the transaction
    conn.commit()
    conn.close()

def inserting_data_into_database_allOrRangeRead_ParameterFit_setParameters(db_file, wafer, insulator, cross_sectional_area,
                                                                           die, CB_word, CB_bit):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)

    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'ParameterFit_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'ParameterFit_{current_time_uk}_1'
    else:
        experiment_name = f'ParameterFit_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))

    # Insert Location data:
    cursor.execute('''
        INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_experiment_id, wafer, die, CB_word, CB_bit))

    # Insert data into the ParameterFit_Function table with values identical to the last record
    # Select only the specific columns you need
    cursor.execute('''
        SELECT pulses, pulse_width_s, bias_interpulse_s, iv_interpulse_s, iv_pulse_width_s, iv_type, 
               iv_start_V, iv_step_V, run_iv, positive_polarity_v_start_V, positive_polarity_v_step_V, 
               positive_polarity_v_stop_V, positive_polarity_iv_stop_V, negative_polarity_v_start_V, 
               negative_polarity_v_step_V, negative_polarity_v_stop_V, negative_polarity_iv_stop_V
        FROM ParameterFit_Function 
        WHERE experiment_id = (SELECT MAX(experiment_id) FROM ParameterFit_Function)
    ''')

    last_record = cursor.fetchone()

    if last_record:
        # Unpack the values from the last record
        (
            pulses, pulse_width_s, bias_interpulse_s, iv_interpulse_s, iv_pulse_width_s, iv_type,
            iv_start_V, iv_step_V, run_iv, positive_polarity_v_start_V, positive_polarity_v_step_V,
            positive_polarity_v_stop_V, positive_polarity_iv_stop_V, negative_polarity_v_start_V,
            negative_polarity_v_step_V, negative_polarity_v_stop_V, negative_polarity_iv_stop_V
        ) = last_record

        # Insert a new record with the same values as the previous one, but with a new experiment_id
        cursor.execute('''
            INSERT INTO ParameterFit_Function (
                experiment_id, pulses, pulse_width_s, bias_interpulse_s, iv_interpulse_s, iv_pulse_width_s, iv_type, 
                iv_start_V, iv_step_V, run_iv, positive_polarity_v_start_V, positive_polarity_v_step_V, 
                positive_polarity_v_stop_V, positive_polarity_iv_stop_V, negative_polarity_v_start_V, 
                negative_polarity_v_step_V, negative_polarity_v_stop_V, negative_polarity_iv_stop_V
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            current_experiment_id,  # Use the new experiment_id
            pulses,                 # Copy values from the last record
            pulse_width_s,
            bias_interpulse_s,
            iv_interpulse_s,
            iv_pulse_width_s,
            iv_type,
            iv_start_V,
            iv_step_V,
            run_iv,
            positive_polarity_v_start_V,
            positive_polarity_v_step_V,
            positive_polarity_v_stop_V,
            positive_polarity_iv_stop_V,
            negative_polarity_v_start_V,
            negative_polarity_v_step_V,
            negative_polarity_v_stop_V,
            negative_polarity_iv_stop_V
        ))

    # Commit the transaction
    conn.commit()
    conn.close()


def inserting_data_into_database_singleRead_SwitchSeeker_setParameters(db_file, insulator, cross_sectional_area,
                                                                       reads_in_trailer_card, programming_pulses,
                                                                       pulse_duration_ms, voltage_min_V, voltage_step_V,
                                                                       voltage_max_V, max_switching_cycles,
                                                                       tolerance_band_percent, interpulse_time_ms,
                                                                       resistance_threshold, seeker_algorithm,
                                                                       stage_II_polarity, skip_stage_I, read_after_pulse):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)


    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'SwitchSeeker_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'SwitchSeeker_{current_time_uk}_1'
    else:
        experiment_name = f'SwitchSeeker_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))


    # Insert into SwitchSeeker_Function table
    cursor.execute('''
        INSERT INTO SwitchSeeker_Function (
            experiment_id, reads_in_trailer_card, programming_pulses, pulse_duration_ms, voltage_min_V, voltage_step_V,
            voltage_max_V, max_switching_cycles, tolerance_band_percent, interpulse_time_ms, resistance_threshold,
            seeker_algorithm, stage_II_polarity, skip_stage_I, read_after_pulse
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        current_experiment_id, reads_in_trailer_card, programming_pulses, pulse_duration_ms, voltage_min_V, voltage_step_V,
        voltage_max_V, max_switching_cycles, tolerance_band_percent, interpulse_time_ms, resistance_threshold,
        seeker_algorithm, stage_II_polarity, skip_stage_I, read_after_pulse
    ))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()


def inserting_data_into_database_allOrRangeRead_SwitchSeeker_setParameters(db_file, wafer, insulator,
                                                                           cross_sectional_area, die, CB_word, CB_bit):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)

    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'SwitchSeeker_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'SwitchSeeker_{current_time_uk}_1'
    else:
        experiment_name = f'SwitchSeeker_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))

    # Insert Location data:
    cursor.execute('''
        INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_experiment_id, wafer, die, CB_word, CB_bit))

    # Insert data into the SwitchSeeker_Function table with values identical to the last record
    # Select only the specific columns you need
    cursor.execute('''
        SELECT reads_in_trailer_card, programming_pulses, pulse_duration_ms, voltage_min_V, voltage_step_V, voltage_max_V,
               max_switching_cycles, tolerance_band_percent, interpulse_time_ms, resistance_threshold,
               seeker_algorithm, stage_II_polarity, skip_stage_I, read_after_pulse
        FROM SwitchSeeker_Function 
        WHERE experiment_id = (SELECT MAX(experiment_id) FROM SwitchSeeker_Function)
    ''')

    last_record = cursor.fetchone()

    if last_record:
        # Unpack the values from the last record
        (
            reads_in_trailer_card, programming_pulses, pulse_duration_ms, voltage_min_V, voltage_step_V, voltage_max_V,
            max_switching_cycles, tolerance_band_percent, interpulse_time_ms, resistance_threshold,
            seeker_algorithm, stage_II_polarity, skip_stage_I, read_after_pulse
        ) = last_record

        # Insert a new record with the same values as the previous one, but with a new experiment_id
        cursor.execute('''
            INSERT INTO SwitchSeeker_Function (
                experiment_id, reads_in_trailer_card, programming_pulses, pulse_duration_ms, voltage_min_V, voltage_step_V,
                voltage_max_V, max_switching_cycles, tolerance_band_percent, interpulse_time_ms, resistance_threshold,
                seeker_algorithm, stage_II_polarity, skip_stage_I, read_after_pulse
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            current_experiment_id,  # Use the new experiment_id
            reads_in_trailer_card,  # Copy values from the last record
            programming_pulses,
            pulse_duration_ms,
            voltage_min_V,
            voltage_step_V,
            voltage_max_V,
            max_switching_cycles,
            tolerance_band_percent,
            interpulse_time_ms,
            resistance_threshold,
            seeker_algorithm,
            stage_II_polarity,
            skip_stage_I,
            read_after_pulse
        ))

    # Commit the transaction
    conn.commit()
    conn.close()

def inserting_data_into_database_singleRead_Chronoamperometry_setParameters(
db_file, insulator, cross_sectional_area, bias_V, bias_duration, duration_unit, number_of_reads
):
    """
    Inserts Chronoamperometry experiment data into the database.

    Parameters:
        db_file (str): Path to the database file.
        insulator (str): Insulating material.
        cross_sectional_area (float): Cross-sectional area.
        bias_V (float): Bias voltage.
        bias_duration (float): Bias duration.
        duration_unit (str): Duration unit (e.g., s/ms/us).
        number_of_reads (int): Number of reads.
    """

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create table templates if they don't exist
        database_structure_template(db_file)

        # Get the current UK time and format it as a string
        uk_timezone = pytz.timezone('Europe/London')
        current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

        # Generate a new experiment name based on the current time
        cursor.execute(
            'SELECT COUNT(*) FROM Experiment WHERE experiment_name LIKE ?',
            (f'Chronoamperometry_{current_time_uk}%',)
        )
        count = cursor.fetchone()[0]
        experiment_name = (
            f'Chronoamperometry_{current_time_uk}_{count + 1}'
            if count > 0 else f'Chronoamperometry_{current_time_uk}_1'
        )

        # Insert the new experiment name into the Experiment table
        cursor.execute(
            'INSERT INTO Experiment (experiment_name) VALUES (?)',
            (experiment_name,)
        )
        current_experiment_id = cursor.lastrowid

        # Insert Material data
        cursor.execute(
            'INSERT INTO Material (experiment_id, top, bottom, insulator) VALUES (?, ?, ?, ?)',
            (current_experiment_id, None, None, insulator)
        )

        # Insert Size data
        cursor.execute(
            'INSERT INTO Size (experiment_id, cross_sectional_area, thickness) VALUES (?, ?, ?)',
            (current_experiment_id, cross_sectional_area, None)
        )

        # Insert Process data
        cursor.execute(
            'INSERT INTO Process (experiment_id, temperature, additional_parameters) VALUES (?, ?, ?)',
            (current_experiment_id, None, None)
        )

        # Insert into Chronoamperometry_Function table
        cursor.execute(
            'INSERT INTO Chronoamperometry_Function (experiment_id, bias_V, bias_duration, duration_unit, number_of_reads) '
            'VALUES (?, ?, ?, ?, ?)',
            (current_experiment_id, bias_V, bias_duration, duration_unit, number_of_reads)
        )

        # Commit the transaction
        conn.commit()
        print(f"Experiment '{experiment_name}' data has been successfully inserted into the database.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

def inserting_data_into_database_allOrRangeRead_Chronoamperometry_setParameters(db_file, wafer, insulator,
                                                                               cross_sectional_area, die, CB_word, CB_bit):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)

    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'Chronoamperometry_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'Chronoamperometry_{current_time_uk}_1'
    else:
        experiment_name = f'Chronoamperometry_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))

    # Insert Location data:
    cursor.execute('''
        INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_experiment_id, wafer, die, CB_word, CB_bit))

    # Insert data into the Chronoamperometry_Function table with values identical to the last record
    cursor.execute('''
        SELECT bias_V, bias_duration, duration_unit, number_of_reads
        FROM Chronoamperometry_Function 
        WHERE experiment_id = (SELECT MAX(experiment_id) FROM Chronoamperometry_Function)
    ''')

    last_record = cursor.fetchone()

    if last_record:
        cursor.execute('''
            INSERT INTO Chronoamperometry_Function (experiment_id, bias_V, bias_duration, duration_unit, number_of_reads)
            VALUES (?, ?, ?, ?, ?)
        ''', (current_experiment_id, *last_record))
    else:
        print("No previous data found in Chronoamperometry_Function table.")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def inserting_data_into_database_singleRead_ConvergeToState_setParameters(db_file, insulator, cross_sectional_area,
                                                                          target_R, initial_polarity, pw_min_ms,
                                                                          pw_step_percent, pw_max_ms,
                                                                          interpulse_time_ms, rt_tolerance_percent,
                                                                          ro_tolerance_percent, voltage_min_V,
                                                                          voltage_step_V, voltage_max_V, pulses):
    """
    Inserts ConvergeToState experiment data into the database.

    Parameters:
        db_file (str): Path to the database file.
        insulator (str): Insulating material.
        cross_sectional_area (float): Cross-sectional area.
        target_R (int): Target resistance.
        initial_polarity (str): Initial polarity (Positive/Negative).
        pw_min_ms (float): Minimum pulse width (milliseconds).
        pw_step_percent (float): Pulse width step percentage.
        pw_max_ms (float): Maximum pulse width (milliseconds).
        interpulse_time_ms (float): Interpulse time (milliseconds).
        rt_tolerance_percent (float): Rt tolerance percentage.
        ro_tolerance_percent (float): Ro tolerance percentage.
        voltage_min_V (float): Minimum voltage (volts).
        voltage_step_V (float): Voltage step (volts).
        voltage_max_V (float): Maximum voltage (volts).
        pulses (int): Number of pulses.
    """

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create table structures (assuming you have a function to do this)
        database_structure_template(db_file)

        # Get the current UK time and format it as a string
        uk_timezone = pytz.timezone('Europe/London')
        current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

        # Generate a unique experiment name
        cursor.execute('SELECT COUNT(*) FROM Experiment WHERE experiment_name LIKE ?',
                       (f'ConvergeToState_{current_time_uk}%',))
        count = cursor.fetchone()[0]

        if count == 0:
            experiment_name = f'ConvergeToState_{current_time_uk}_1'
        else:
            experiment_name = f'ConvergeToState_{current_time_uk}_{count + 1}'

        # Insert the new experiment name into the Experiment table
        cursor.execute('INSERT INTO Experiment (experiment_name) VALUES (?)', (experiment_name,))
        current_experiment_id = cursor.lastrowid

        # Insert Material data
        cursor.execute('INSERT INTO Material (experiment_id, top, bottom, insulator) VALUES (?, ?, ?, ?)',
                       (current_experiment_id, None, None, insulator))  # Top and Bottom set to None

        # Insert Size data
        cursor.execute('INSERT INTO Size (experiment_id, cross_sectional_area, thickness) VALUES (?, ?, ?)',
                       (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

        # Insert Process data
        cursor.execute('INSERT INTO Process (experiment_id, temperature, additional_parameters) VALUES (?, ?, ?)',
                       (current_experiment_id, None, None))  # temperature and additional_parameters set to None

        # Insert into ConvergeToState_Function table
        cursor.execute(
            'INSERT INTO ConvergeToState_Function (experiment_id, target_R, initial_polarity, pw_min_ms, '
            'pw_step_percent, pw_max_ms, interpulse_time_ms, rt_tolerance_percent, ro_tolerance_percent, '
            'voltage_min_V, voltage_step_V, voltage_max_V, pulses) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (current_experiment_id, target_R, initial_polarity, pw_min_ms, pw_step_percent, pw_max_ms,
             interpulse_time_ms, rt_tolerance_percent, ro_tolerance_percent, voltage_min_V, voltage_step_V,
             voltage_max_V, pulses))

        # Commit the transaction and close the connection
        conn.commit()
        print(f"Experiment '{experiment_name}' data has been successfully inserted into the database.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()
def inserting_data_into_database_allOrRangeRead_ConvergeToState_setParameters(db_file, wafer, insulator,
                                                                             cross_sectional_area, die, CB_word, CB_bit):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)

    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'ConvergeToState_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'ConvergeToState_{current_time_uk}_1'
    else:
        experiment_name = f'ConvergeToState_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))

    # Insert Location data:
    cursor.execute('''
        INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_experiment_id, wafer, die, CB_word, CB_bit))

    # Insert data into the ConvergeToState_Function table with values identical to the last record
    cursor.execute('''
        SELECT target_R, initial_polarity, pw_min_ms, pw_step_percent, pw_max_ms, interpulse_time_ms, rt_tolerance_percent,
               ro_tolerance_percent, voltage_min_V, voltage_step_V, voltage_max_V, pulses
        FROM ConvergeToState_Function 
        WHERE experiment_id = (SELECT MAX(experiment_id) FROM ConvergeToState_Function)
    ''')

    last_record = cursor.fetchone()

    if last_record:
        cursor.execute('''
            INSERT INTO ConvergeToState_Function (experiment_id, target_R, initial_polarity, pw_min_ms, pw_step_percent, 
                                                  pw_max_ms, interpulse_time_ms, rt_tolerance_percent, ro_tolerance_percent, 
                                                  voltage_min_V, voltage_step_V, voltage_max_V, pulses)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (current_experiment_id, *last_record))
    else:
        print("No previous data found in ConvergeToState_Function table.")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
def inserting_data_into_database_singleRead_Endurance_setParameters(
    db_file, insulator, cross_sectional_area, positive_pulse_amplitude_V, positive_pulse_width_us,
    positive_current_cutoff_uA, num_positive_pulses, cycles, interpulse_time_ms,
    negative_pulse_amplitude_V, negative_pulse_width_us, negative_current_cutoff_uA, num_negative_pulses
):
    """
    Inserts Endurance experiment data into the database.

    Parameters:
        db_file (str): Path to the database file.
        insulator (str): Insulating material.
        cross_sectional_area (float): Cross-sectional area.
        positive_pulse_amplitude_V (float): Positive pulse amplitude (V).
        positive_pulse_width_us (float): Positive pulse width (us).
        positive_current_cutoff_uA (float): Positive current cut-off (uA).
        num_positive_pulses (int): Number of positive pulses.
        cycles (int): Number of cycles.
        interpulse_time_ms (float): Interpulse time (ms).
        negative_pulse_amplitude_V (float): Negative pulse amplitude (V).
        negative_pulse_width_us (float): Negative pulse width (us).
        negative_current_cutoff_uA (float): Negative current cut-off (uA).
        num_negative_pulses (int): Number of negative pulses.
    """

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create table templates if they don't exist
        database_structure_template(db_file)

        # Get the current UK time and format it as a string
        uk_timezone = pytz.timezone('Europe/London')
        current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

        # Generate a new experiment name based on the current time
        cursor.execute(
            'SELECT COUNT(*) FROM Experiment WHERE experiment_name LIKE ?',
            (f'Endurance_{current_time_uk}%',)
        )
        count = cursor.fetchone()[0]
        experiment_name = (
            f'Endurance_{current_time_uk}_{count + 1}'
            if count > 0 else f'Endurance_{current_time_uk}_1'
        )

        # Insert the new experiment name into the Experiment table
        cursor.execute(
            'INSERT INTO Experiment (experiment_name) VALUES (?)',
            (experiment_name,)
        )
        current_experiment_id = cursor.lastrowid

        # Insert Material data
        cursor.execute(
            'INSERT INTO Material (experiment_id, top, bottom, insulator) VALUES (?, ?, ?, ?)',
            (current_experiment_id, None, None, insulator)
        )

        # Insert Size data
        cursor.execute(
            'INSERT INTO Size (experiment_id, cross_sectional_area, thickness) VALUES (?, ?, ?)',
            (current_experiment_id, cross_sectional_area, None)
        )

        # Insert Process data
        cursor.execute(
            'INSERT INTO Process (experiment_id, temperature, additional_parameters) VALUES (?, ?, ?)',
            (current_experiment_id, None, None)
        )

        # Insert into Endurance_Function table
        cursor.execute(
            '''INSERT INTO Endurance_Function (
                experiment_id, positive_pulse_amplitude_V, positive_pulse_width_us, positive_current_cutoff_uA, 
                num_positive_pulses, cycles, interpulse_time_ms, negative_pulse_amplitude_V, negative_pulse_width_us, 
                negative_current_cutoff_uA, num_negative_pulses
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                current_experiment_id, positive_pulse_amplitude_V, positive_pulse_width_us, positive_current_cutoff_uA,
                num_positive_pulses, cycles, interpulse_time_ms, negative_pulse_amplitude_V, negative_pulse_width_us,
                negative_current_cutoff_uA, num_negative_pulses
            )
        )

        # Commit the transaction
        conn.commit()
        print(f"Experiment '{experiment_name}' data has been successfully inserted into the database.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

def inserting_data_into_database_allOrRangeRead_Endurance_setParameters(db_file, wafer, insulator,
                                                                        cross_sectional_area, die, CB_word, CB_bit):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)

    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'Endurance_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'Endurance_{current_time_uk}_1'
    else:
        experiment_name = f'Endurance_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))

    # Insert Location data:
    cursor.execute('''
        INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_experiment_id, wafer, die, CB_word, CB_bit))

    # Insert data into the Endurance_Function table with values identical to the last record
    cursor.execute('''
        SELECT positive_pulse_amplitude_V, positive_pulse_width_us, positive_current_cutoff_uA, num_positive_pulses,
               cycles, interpulse_time_ms, negative_pulse_amplitude_V, negative_pulse_width_us, 
               negative_current_cutoff_uA, num_negative_pulses
        FROM Endurance_Function 
        WHERE experiment_id = (SELECT MAX(experiment_id) FROM Endurance_Function)
    ''')

    last_record = cursor.fetchone()

    if last_record:
        cursor.execute('''
            INSERT INTO Endurance_Function (experiment_id, positive_pulse_amplitude_V, positive_pulse_width_us, 
                                            positive_current_cutoff_uA, num_positive_pulses, cycles, interpulse_time_ms, 
                                            negative_pulse_amplitude_V, negative_pulse_width_us, 
                                            negative_current_cutoff_uA, num_negative_pulses)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (current_experiment_id, *last_record))
    else:
        print("No previous data found in Endurance_Function table.")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def inserting_data_into_database_singleRead_MultiBias_setParameters(
    db_file, insulator, cross_sectional_area, active_wordlines, active_bitline, write_amplitude_V,
    write_pulse_width_us, read_voltage_V, current_on_active_bitline_uA, read_or_write
):
    """
    Inserts MultiBias experiment data into the database.

    Parameters:
        db_file (str): Path to the database file.
        insulator (str): Insulating material.
        cross_sectional_area (float): Cross-sectional area.
        active_wordlines (str): Active Wordlines (e.g., "1 2").
        active_bitline (int): Active Bitline.
        write_amplitude_V (float): WRITE amplitude (V).
        write_pulse_width_us (float): WRITE pulse width (us).
        read_voltage_V (float): READ voltage (V).
        current_on_active_bitline_uA (float): Current on Active Bitline (uA).
        read_or_write (str): Indicates whether the operation is a 'read' or 'write'.
    """

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create table templates if they don't exist
        database_structure_template(db_file)

        # Get the current UK time and format it as a string
        uk_timezone = pytz.timezone('Europe/London')
        current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

        # Generate a new experiment name based on the current time
        cursor.execute(
            'SELECT COUNT(*) FROM Experiment WHERE experiment_name LIKE ?',
            (f'MultiBias_{current_time_uk}%',)
        )
        count = cursor.fetchone()[0]
        experiment_name = (
            f'MultiBias_{current_time_uk}_{count + 1}'
            if count > 0 else f'MultiBias_{current_time_uk}_1'
        )

        # Insert the new experiment name into the Experiment table
        cursor.execute(
            'INSERT INTO Experiment (experiment_name) VALUES (?)',
            (experiment_name,)
        )
        current_experiment_id = cursor.lastrowid

        # Insert Material data
        cursor.execute(
            'INSERT INTO Material (experiment_id, top, bottom, insulator) VALUES (?, ?, ?, ?)',
            (current_experiment_id, None, None, insulator)
        )

        # Insert Size data
        cursor.execute(
            'INSERT INTO Size (experiment_id, cross_sectional_area, thickness) VALUES (?, ?, ?)',
            (current_experiment_id, cross_sectional_area, None)
        )

        # Insert Process data
        cursor.execute(
            'INSERT INTO Process (experiment_id, temperature, additional_parameters) VALUES (?, ?, ?)',
            (current_experiment_id, None, None)
        )

        # Insert into MultiBias_Function table
        cursor.execute(
            '''INSERT INTO MultiBias_Function (
                experiment_id, active_wordlines, active_bitline, write_amplitude_V, write_pulse_width_us, 
                read_voltage_V, current_on_active_bitline_uA, read_or_write
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                current_experiment_id, active_wordlines, active_bitline, write_amplitude_V, write_pulse_width_us,
                read_voltage_V, current_on_active_bitline_uA, read_or_write
            )
        )

        # Commit the transaction
        conn.commit()
        print(f"Experiment '{experiment_name}' data has been successfully inserted into the database.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

def inserting_data_into_database_allOrRangeRead_MultiBias_setParameters(db_file, wafer, insulator,
                                                                        cross_sectional_area, die, CB_word, CB_bit):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)

    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'MultiBias_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'MultiBias_{current_time_uk}_1'
    else:
        experiment_name = f'MultiBias_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))

    # Insert Location data:
    cursor.execute('''
        INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_experiment_id, wafer, die, CB_word, CB_bit))

    # Insert data into the MultiBias_Function table with values identical to the last record
    cursor.execute('''
        SELECT active_wordlines, active_bitline, write_amplitude_V, write_pulse_width_us, read_voltage_V, 
               current_on_active_bitline_uA, read_or_write
        FROM MultiBias_Function 
        WHERE experiment_id = (SELECT MAX(experiment_id) FROM MultiBias_Function)
    ''')

    last_record = cursor.fetchone()

    if last_record:
        cursor.execute('''
            INSERT INTO MultiBias_Function (experiment_id, active_wordlines, active_bitline, write_amplitude_V, 
                                            write_pulse_width_us, read_voltage_V, current_on_active_bitline_uA,
                                            read_or_write)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (current_experiment_id, *last_record))
    else:
        print("No previous data found in MultiBias_Function table.")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
def inserting_data_into_database_singleRead_MultiStateSeeker_setParameters(
    db_file, insulator, cross_sectional_area, single_phase_run, phase, phase_I_reads, phase_I_prog_pulses,
    phase_I_pulse_width_ms, phase_I_voltage_min_V, phase_I_voltage_step_V, phase_I_voltage_max_V,
    phase_I_interpulse_ms, phase_I_tolerance_band_percent, phase_I_read_after_pulse, phase_II_pulse_voltage_V,
    phase_II_pulse_width_ms, phase_II_state_mode, phase_II_stability_test, phase_II_max_time,
    phase_II_tolerance_percent, phase_III_mode, phase_III_reads, phase_III_max_prog_pulses, phase_III_pulse_width_ms,
    phase_III_voltage_bias_V, phase_III_voltage_min_V, phase_III_voltage_step_V, phase_III_voltage_max_V,
    phase_III_interpulse_ms, phase_III_retention_time, phase_III_retention_unit, phase_III_std_deviations,
    phase_III_monotonicity, phase_III_reset_counter
):
    """
    Inserts MultiStateSeeker experiment data into the database.

    Parameters:
        db_file (str): Path to the database file.
        insulator (str): Insulating material.
        cross_sectional_area (float): Cross-sectional area.
        single_phase_run (bool): Single phase run (checkbox).
        phase (str): Phase (Phase I, II, III).
        (Other phase-specific parameters follow...)
    """

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create table templates if they don't exist
        database_structure_template(db_file)

        # Get the current UK time and format it as a string
        uk_timezone = pytz.timezone('Europe/London')
        current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

        # Generate a new experiment name based on the current time
        cursor.execute(
            'SELECT COUNT(*) FROM Experiment WHERE experiment_name LIKE ?',
            (f'MultiStateSeeker_{current_time_uk}%',)
        )
        count = cursor.fetchone()[0]
        experiment_name = (
            f'MultiStateSeeker_{current_time_uk}_{count + 1}'
            if count > 0 else f'MultiStateSeeker_{current_time_uk}_1'
        )

        # Insert the new experiment name into the Experiment table
        cursor.execute(
            'INSERT INTO Experiment (experiment_name) VALUES (?)',
            (experiment_name,)
        )
        current_experiment_id = cursor.lastrowid

        # Insert Material data
        cursor.execute(
            'INSERT INTO Material (experiment_id, top, bottom, insulator) VALUES (?, ?, ?, ?)',
            (current_experiment_id, None, None, insulator)
        )

        # Insert Size data
        cursor.execute(
            'INSERT INTO Size (experiment_id, cross_sectional_area, thickness) VALUES (?, ?, ?)',
            (current_experiment_id, cross_sectional_area, None)
        )

        # Insert Process data
        cursor.execute(
            'INSERT INTO Process (experiment_id, temperature, additional_parameters) VALUES (?, ?, ?)',
            (current_experiment_id, None, None)
        )
        print("fail")
        # Insert into MultiStateSeeker_Function table
        cursor.execute(
            '''INSERT INTO MultiStateSeeker_Function (
                experiment_id, single_phase_run, phase, phase_I_reads, phase_I_prog_pulses, phase_I_pulse_width_ms,     
                phase_I_voltage_min_V, phase_I_voltage_step_V, phase_I_voltage_max_V, phase_I_interpulse_ms,           
                phase_I_tolerance_band_percent, phase_I_read_after_pulse, phase_II_pulse_voltage_V,                    
                phase_II_pulse_width_ms, phase_II_state_mode, phase_II_stability_test, phase_II_max_time,               
                phase_II_tolerance_percent, phase_III_mode, phase_III_reads, phase_III_max_prog_pulses,                 
                phase_III_pulse_width_ms, phase_III_voltage_bias_V, phase_III_voltage_min_V, phase_III_voltage_step_V,  
                phase_III_voltage_max_V, phase_III_interpulse_ms, phase_III_retention_time, phase_III_retention_unit,   
                phase_III_std_deviations, phase_III_monotonicity, phase_III_reset_counter                               
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                current_experiment_id, single_phase_run, phase, phase_I_reads, phase_I_prog_pulses,
                phase_I_pulse_width_ms, phase_I_voltage_min_V, phase_I_voltage_step_V, phase_I_voltage_max_V,
                phase_I_interpulse_ms,
                phase_I_tolerance_band_percent, phase_I_read_after_pulse, phase_II_pulse_voltage_V,
                phase_II_pulse_width_ms,
                phase_II_state_mode, phase_II_stability_test, phase_II_max_time, phase_II_tolerance_percent,
                phase_III_mode,
                phase_III_reads, phase_III_max_prog_pulses, phase_III_pulse_width_ms, phase_III_voltage_bias_V,
                phase_III_voltage_min_V, phase_III_voltage_step_V, phase_III_voltage_max_V, phase_III_interpulse_ms,
                phase_III_retention_time, phase_III_retention_unit, phase_III_std_deviations, phase_III_monotonicity,
                phase_III_reset_counter
            )
        )

        print("fail2")
        # Commit the transaction
        conn.commit()
        print(f"Experiment '{experiment_name}' data has been successfully inserted into the database.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e} :inserting_data_into_database_singleRead_MultiStateSeeker_setParameters")

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

def inserting_data_into_database_allOrRangeRead_MultiStateSeeker_setParameters(db_file, wafer, insulator,
                                                                               cross_sectional_area, die, CB_word, CB_bit):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)

    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'MultiStateSeeker_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'MultiStateSeeker_{current_time_uk}_1'
    else:
        experiment_name = f'MultiStateSeeker_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))

    # Insert Location data:
    cursor.execute('''
        INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_experiment_id, wafer, die, CB_word, CB_bit))

    # Insert data into the MultiStateSeeker_Function table with values identical to the last record
    cursor.execute('''
        SELECT single_phase_run, phase, phase_I_reads, phase_I_prog_pulses, phase_I_pulse_width_ms, phase_I_voltage_min_V,
               phase_I_voltage_step_V, phase_I_voltage_max_V, phase_I_interpulse_ms, phase_I_tolerance_band_percent,
               phase_I_read_after_pulse, phase_II_pulse_voltage_V, phase_II_pulse_width_ms, phase_II_state_mode,
               phase_II_stability_test, phase_II_max_time, phase_II_tolerance_percent, phase_III_mode, phase_III_reads,
               phase_III_max_prog_pulses, phase_III_pulse_width_ms, phase_III_voltage_bias_V, phase_III_voltage_min_V,
               phase_III_voltage_step_V, phase_III_voltage_max_V, phase_III_interpulse_ms, phase_III_retention_time,
               phase_III_retention_unit, phase_III_std_deviations, phase_III_monotonicity, phase_III_reset_counter
        FROM MultiStateSeeker_Function 
        WHERE experiment_id = (SELECT MAX(experiment_id) FROM MultiStateSeeker_Function)
    ''')

    last_record = cursor.fetchone()

    if last_record:
        cursor.execute('''
            INSERT INTO MultiStateSeeker_Function (
                experiment_id, single_phase_run, phase, phase_I_reads, phase_I_prog_pulses, phase_I_pulse_width_ms,     
                phase_I_voltage_min_V, phase_I_voltage_step_V, phase_I_voltage_max_V, phase_I_interpulse_ms,           
                phase_I_tolerance_band_percent, phase_I_read_after_pulse, phase_II_pulse_voltage_V,                    
                phase_II_pulse_width_ms, phase_II_state_mode, phase_II_stability_test, phase_II_max_time,               
                phase_II_tolerance_percent, phase_III_mode, phase_III_reads, phase_III_max_prog_pulses,                 
                phase_III_pulse_width_ms, phase_III_voltage_bias_V, phase_III_voltage_min_V, phase_III_voltage_step_V,  
                phase_III_voltage_max_V, phase_III_interpulse_ms, phase_III_retention_time, phase_III_retention_unit,   
                phase_III_std_deviations, phase_III_monotonicity, phase_III_reset_counter                               
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (current_experiment_id, *last_record))
    else:
        print("No previous data found in MultiStateSeeker_Function table.")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def inserting_data_into_database_singleRead_Retention_setParameters(
    db_file, insulator, cross_sectional_area, read_every, read_every_unit, read_for, read_for_unit
):
    """
    Inserts Retention experiment data into the database.

    Parameters:
        db_file (str): Path to the database file.
        insulator (str): Insulating material.
        cross_sectional_area (float): Cross-sectional area.
        read_every (int): Read every (value).
        read_every_unit (str): Read every unit (s, ms, etc.).
        read_for (int): Read for (value).
        read_for_unit (str): Read for unit (min, s, etc.).
    """

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create table templates if they don't exist
        database_structure_template(db_file)

        # Get the current UK time and format it as a string
        uk_timezone = pytz.timezone('Europe/London')
        current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

        # Generate a new experiment name based on the current time
        cursor.execute(
            'SELECT COUNT(*) FROM Experiment WHERE experiment_name LIKE ?',
            (f'Retention_{current_time_uk}%',)
        )
        count = cursor.fetchone()[0]
        experiment_name = (
            f'Retention_{current_time_uk}_{count + 1}'
            if count > 0 else f'Retention_{current_time_uk}_1'
        )

        # Insert the new experiment name into the Experiment table
        cursor.execute(
            'INSERT INTO Experiment (experiment_name) VALUES (?)',
            (experiment_name,)
        )
        current_experiment_id = cursor.lastrowid

        # Insert Material data
        cursor.execute(
            'INSERT INTO Material (experiment_id, top, bottom, insulator) VALUES (?, ?, ?, ?)',
            (current_experiment_id, None, None, insulator)
        )

        # Insert Size data
        cursor.execute(
            'INSERT INTO Size (experiment_id, cross_sectional_area, thickness) VALUES (?, ?, ?)',
            (current_experiment_id, cross_sectional_area, None)
        )

        # Insert Process data
        cursor.execute(
            'INSERT INTO Process (experiment_id, temperature, additional_parameters) VALUES (?, ?, ?)',
            (current_experiment_id, None, None)
        )

        # Insert into Retention_Function table
        cursor.execute(
            '''INSERT INTO Retention_Function (
                experiment_id, read_every, read_every_unit, read_for, read_for_unit
            ) VALUES (?, ?, ?, ?, ?)''',
            (
                current_experiment_id, read_every, read_every_unit, read_for, read_for_unit
            )
        )

        # Commit the transaction
        conn.commit()
        print(f"Experiment '{experiment_name}' data has been successfully inserted into the database.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

def inserting_data_into_database_allOrRangeRead_Retention_setParameters(db_file, wafer, insulator,
                                                                        cross_sectional_area, die, CB_word, CB_bit):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)

    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'Retention_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'Retention_{current_time_uk}_1'
    else:
        experiment_name = f'Retention_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))

    # Insert Location data:
    cursor.execute('''
        INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_experiment_id, wafer, die, CB_word, CB_bit))

    # Insert data into the Retention_Function table with values identical to the last record
    cursor.execute('''
        SELECT read_every, read_every_unit, read_for, read_for_unit
        FROM Retention_Function 
        WHERE experiment_id = (SELECT MAX(experiment_id) FROM Retention_Function)
    ''')

    last_record = cursor.fetchone()

    if last_record:
        cursor.execute('''
            INSERT INTO Retention_Function (experiment_id, read_every, read_every_unit, read_for, read_for_unit)
            VALUES (?, ?, ?, ?, ?)
        ''', (current_experiment_id, *last_record))
    else:
        print("No previous data found in Retention_Function table.")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def inserting_data_into_database_singleRead_VolatilityRead_setParameters(
    db_file, insulator, cross_sectional_area, pulse_amplitude_V, pulse_width_us, read_batch_size,
    avg_cycles_per_point_M, stop_time_s, stop_t_metric, stop_tolerance_percent, stop_option
):
    """
    Inserts VolatilityRead experiment data into the database.

    Parameters:
        db_file (str): Path to the database file.
        insulator (str): Insulating material.
        cross_sectional_area (float): Cross-sectional area.
        pulse_amplitude_V (float): Pulse Amplitude (V).
        pulse_width_us (float): Pulse Width (us).
        read_batch_size (int): Read Batch Size (B).
        avg_cycles_per_point_M (int): Average cycles per point (M).
        stop_time_s (float): Stop time (s).
        stop_t_metric (float): Stop t-metric.
        stop_tolerance_percent (float): Stop Tolerance (%/batch).
        stop_option (str): Stop Option (e.g., LinearFit).
    """

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create table templates if they don't exist
        database_structure_template(db_file)

        # Get the current UK time and format it as a string
        uk_timezone = pytz.timezone('Europe/London')
        current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

        # Generate a new experiment name based on the current time
        cursor.execute(
            'SELECT COUNT(*) FROM Experiment WHERE experiment_name LIKE ?',
            (f'VolatilityRead_{current_time_uk}%',)
        )
        count = cursor.fetchone()[0]
        experiment_name = (
            f'VolatilityRead_{current_time_uk}_{count + 1}'
            if count > 0 else f'VolatilityRead_{current_time_uk}_1'
        )

        # Insert the new experiment name into the Experiment table
        cursor.execute(
            'INSERT INTO Experiment (experiment_name) VALUES (?)',
            (experiment_name,)
        )
        current_experiment_id = cursor.lastrowid

        # Insert Material data
        cursor.execute(
            'INSERT INTO Material (experiment_id, top, bottom, insulator) VALUES (?, ?, ?, ?)',
            (current_experiment_id, None, None, insulator)
        )

        # Insert Size data
        cursor.execute(
            'INSERT INTO Size (experiment_id, cross_sectional_area, thickness) VALUES (?, ?, ?)',
            (current_experiment_id, cross_sectional_area, None)
        )

        # Insert Process data
        cursor.execute(
            'INSERT INTO Process (experiment_id, temperature, additional_parameters) VALUES (?, ?, ?)',
            (current_experiment_id, None, None)
        )

        # Insert into VolatilityRead_Function table
        cursor.execute(
            '''INSERT INTO VolatilityRead_Function (
                experiment_id, pulse_amplitude_V, pulse_width_us, read_batch_size, avg_cycles_per_point_M, stop_time_s, 
                stop_t_metric, stop_tolerance_percent, stop_option
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                current_experiment_id, pulse_amplitude_V, pulse_width_us, read_batch_size, avg_cycles_per_point_M,
                stop_time_s, stop_t_metric, stop_tolerance_percent, stop_option
            )
        )

        # Commit the transaction
        conn.commit()
        print(f"Experiment '{experiment_name}' data has been successfully inserted into the database.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

def inserting_data_into_database_allOrRangeRead_VolatilityRead_setParameters(db_file, wafer, insulator,
                                                                             cross_sectional_area, die, CB_word, CB_bit):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table templates if they don't exist:
    database_structure_template(db_file)

    # Experiment table Part:
    # Get the current UK time and format it as a string
    uk_timezone = pytz.timezone('Europe/London')
    current_time_uk = datetime.now(uk_timezone).strftime('%Y-%m-%d_%H:%M:%S')

    # Initialize a variable to track the current experiment_id
    current_experiment_id = None

    # Generate a new experiment name
    cursor.execute('''
        SELECT COUNT(*) FROM Experiment 
        WHERE experiment_name LIKE ?
    ''', (f'VolatilityRead_{current_time_uk}%',))
    count = cursor.fetchone()[0]

    # Generate an experiment name with a suffix based on the record count
    if count == 0:
        experiment_name = f'VolatilityRead_{current_time_uk}_1'
    else:
        experiment_name = f'VolatilityRead_{current_time_uk}_{count + 1}'

    # Insert the new experiment name into the Experiment table
    cursor.execute('''
        INSERT INTO Experiment (experiment_name)
        VALUES (?)
    ''', (experiment_name,))

    # Get the ID of the newly inserted experiment
    current_experiment_id = cursor.lastrowid

    # Insert data related to the current experiment into the Material, Size, Process, Location tables
    # Insert Material data:
    cursor.execute('''
        INSERT INTO Material (experiment_id, top, bottom, insulator)
        VALUES (?, ?, ?, ?)
    ''', (current_experiment_id, None, None, insulator))  # Top and Bottom as None

    # Insert Size data:
    cursor.execute('''
        INSERT INTO Size (experiment_id, cross_sectional_area, thickness)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, cross_sectional_area, None))  # Only inserting cross_sectional_area

    # Insert Process data:
    cursor.execute('''
        INSERT INTO Process (experiment_id, temperature, additional_parameters)
        VALUES (?, ?, ?)
    ''', (current_experiment_id, None, None))

    # Insert Location data:
    cursor.execute('''
        INSERT INTO Location (experiment_id, wafer, die, wordline, bitline)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_experiment_id, wafer, die, CB_word, CB_bit))

    # Insert data into the VolatilityRead_Function table with values identical to the last record
    cursor.execute('''
        SELECT pulse_amplitude_V, pulse_width_us, read_batch_size, avg_cycles_per_point_M, stop_time_s, stop_t_metric,
               stop_tolerance_percent, stop_option
        FROM VolatilityRead_Function 
        WHERE experiment_id = (SELECT MAX(experiment_id) FROM VolatilityRead_Function)
    ''')

    last_record = cursor.fetchone()

    if last_record:
        cursor.execute('''
            INSERT INTO VolatilityRead_Function (experiment_id, pulse_amplitude_V, pulse_width_us, read_batch_size,
                                                 avg_cycles_per_point_M, stop_time_s, stop_t_metric, 
                                                 stop_tolerance_percent, stop_option)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (current_experiment_id, *last_record))
    else:
        print("No previous data found in VolatilityRead_Function table.")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
