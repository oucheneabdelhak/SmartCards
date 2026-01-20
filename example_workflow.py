"""
Complete workflow example for Mifare DESFire EV1 2K card
This script demonstrates all major features of the DesFireEV1 library.
Enhanced with file size info, detailed explanations, and user interaction.
"""

from DesFireEV1 import DesfireCard, ApplicationManager, FileManager
import time

def press_enter_to_continue(prompt="Press Enter to continue..."):
    """Pause execution and wait for user to press Enter"""
    input(f"\n{prompt}")

def main():
    print("="*70)
    print("DESFire EV1 2K - COMPLETE WORKFLOW DEMONSTRATION")
    print("="*70)
    print("\nThis script demonstrates all major features of DESFire EV1 cards.")
    print("It will create applications, different file types, and show their usage.")
    print("\nNOTE: Card will be formatted at the end unless you choose otherwise.")
    
    press_enter_to_continue("Press Enter to begin the workflow...")
    
    try:
        # ============================================
        # 1. INITIALIZATION
        # ============================================
        print("\n" + "="*60)
        print("1. INITIALIZING CARD CONNECTION")
        print("="*60)
        print("\nLooking for PC/SC card readers...")
        try:
            # Connect to first available reader
            card = DesfireCard(reader_index=0)
            print("   ✓ Connected to card reader")
        except Exception as e:
            print(f"   ✗ Failed to connect: {e}")
            print("\n   TROUBLESHOOTING:")
            print("   1. Ensure card reader is connected and powered")
            print("   2. Insert a DESFire EV1 2K card")
            print("   3. Check if PC/SC service is running")
            print("   4. Try running as administrator")
            return
        
        press_enter_to_continue()
        
        # ============================================
        # 2. CARD INFORMATION
        # ============================================
        print("\n" + "="*60)
        print("2. READING CARD INFORMATION")
        print("="*60)
        print("\nGetting card version information...")
        try:
            version_info = card.get_version()
            print(f"   ✓ Card version info received ({len(version_info)} frames)")
            for i, frame in enumerate(version_info):
                print(f"   Frame {i}: {frame}")
        except Exception as e:
            print(f"   ✗ Failed to get version: {e}")
        
        press_enter_to_continue()
        
        # ============================================
        # 3. AUTHENTICATION TO PICC (CARD) LEVEL
        # ============================================
        print("\n" + "="*60)
        print("3. PICC LEVEL AUTHENTICATION")
        print("="*60)
        print("\nAuthenticating with PICC master key...")
        print("Using default DES key (all zeros): 00 00 00 00 00 00 00 00")
        
        default_key = bytes([0x00] * 8)  # Default DES key (all zeros)
        try:
            success = card.authenticate([0x00], default_key)
            if success:
                print("   ✓ PICC authentication successful")
                print("   Now authenticated at card root level")
            else:
                print("   ✗ PICC authentication failed")
                print("\n   Trying to format card with default settings...")
                
                confirm = input("   Format card? (y/N): ").lower()
                if confirm == 'y':
                    if card.format_card():
                        print("   ✓ Card formatted successfully")
                        print("   Card is now in factory default state")
                        # Re-authenticate after format
                        card.authenticate([0x00], default_key)
                    else:
                        print("   ✗ Could not format card")
                        return
                else:
                    print("   Continuing with existing card structure...")
        except Exception as e:
            print(f"   ✗ Authentication error: {e}")
            return
        
        press_enter_to_continue()
        
        # ============================================
        # 4. APPLICATION MANAGEMENT
        # ============================================
        print("\n" + "="*60)
        print("4. APPLICATION MANAGEMENT")
        print("="*60)
        print("\nDESFire cards organize data into applications.")
        print("Each application is like a separate 'folder' with its own security.")
        
        app_mgr = ApplicationManager(card)
        
        # Re-authenticate before application operations
        card.authenticate([0x00], default_key)
        
        # List existing applications
        print("\nScanning for existing applications...")
        existing_apps = app_mgr.list_applications()
        
        if existing_apps:
            print(f"   Found {len(existing_apps)} application(s):")
            for i, aid in enumerate(existing_apps, 1):
                print(f"   {i}. AID: {aid}")
        else:
            print("   No applications found (fresh or formatted card)")
        
        # Check if our test application already exists
        new_aid = [0x00, 0x00, 0x01]
        app_exists = any(aid == new_aid for aid in existing_apps)
        
        if not app_exists:
            # Create new application (AID: 0x000001)
            print(f"\nCreating test application with AID {new_aid}...")
            print("Application Settings:")
            print("  - Key Settings: 0x0F (all operations require authentication)")
            print("  - Number of Keys: 1 (only master key)")
            
            # Need to be authenticated at PICC level to create application
            card.authenticate([0x00], default_key)
            if app_mgr.create_application(new_aid, key_settings=0x0F, num_keys=0x01):
                print("   ✓ Application created successfully")
            else:
                print("   ✗ Failed to create application")
                return
        else:
            print(f"\n   ✓ Test application already exists at AID {new_aid}")
        
        # Select the application
        print(f"\nSelecting application {new_aid}...")
        if card.select_application(new_aid):
            print("   ✓ Application selected")
            print("   Now operating within the test application")
        else:
            print("   ✗ Failed to select application")
            return
        
        press_enter_to_continue()
        
        # ============================================
        # 5. AUTHENTICATION TO APPLICATION LEVEL
        # ============================================
        print("\n" + "="*60)
        print("5. APPLICATION LEVEL AUTHENTICATION")
        print("="*60)
        print("\nEach application has its own security.")
        print("Authenticating with application master key...")
        try:
            success = card.authenticate([0x00], default_key)
            if success:
                print("   ✓ Application authentication successful")
                print("   Now authorized to create/modify files in this application")
            else:
                print("   ✗ Application authentication failed")
                return
        except Exception as e:
            print(f"   ✗ Authentication error: {e}")
            return
        
        press_enter_to_continue()
        
        # ============================================
        # 6. FILE MANAGEMENT - OVERVIEW
        # ============================================
        print("\n" + "="*60)
        print("6. FILE MANAGEMENT SYSTEM")
        print("="*60)
        print("\nDESFire supports 4 types of files:")
        print("1. STANDARD DATA FILE: Basic read/write storage")
        print("2. VALUE FILE: Integer values with credit/debit operations")
        print("3. LINEAR RECORD FILE: Fixed-size records, fills sequentially")
        print("4. CYCLIC RECORD FILE: Fixed-size records, overwrites oldest")
        
        file_mgr = FileManager(card)
        
        # Re-authenticate before file operations
        card.authenticate([0x00], default_key)
        
        # List existing files
        print("\nChecking for existing files in this application...")
        existing_files = file_mgr.list_files()
        
        if existing_files:
            print(f"   Found {len(existing_files)} file(s):")
            for file_id in existing_files:
                file_type = file_mgr.get_file_type(file_id)
                type_names = {
                    0x00: "Standard Data",
                    0x02: "Value",
                    0x03: "Linear Record",
                    0x04: "Cyclic Record"
                }
                type_name = type_names.get(file_type, "Unknown")
                print(f"   - File 0x{file_id:02X}: {type_name}")
        else:
            print("   No files found in this application")
        
        press_enter_to_continue()
        
        # ============================================
        # 7. STANDARD DATA FILE EXAMPLE
        # ============================================
        print("\n" + "="*60)
        print("7. STANDARD DATA FILE DEMONSTRATION")
        print("="*60)
        print("\nStandard files are for general data storage.")
        print("They support random read/write access.")
        
        std_file_id = 0x01
        std_file_size = 40  # Increased from 32 to avoid overflow
        
        # Check if file already exists
        if std_file_id in existing_files:
            print(f"\nFile 0x{std_file_id:02X} already exists.")
            print("Deleting it to start fresh...")
            card.authenticate([0x00], default_key)
            if file_mgr.delete_file(std_file_id):
                print(f"   ✓ File 0x{std_file_id:02X} deleted")
        
        # Create standard file
        print(f"\nCreating standard file:")
        print(f"  File ID: 0x{std_file_id:02X}")
        print(f"  Size: {std_file_size} bytes")
        print(f"  Access: Read/Write with authentication")
        
        card.authenticate([0x00], default_key)
        if file_mgr.create_standard_file(std_file_id, file_size=std_file_size):
            print("   ✓ Standard file created successfully")
            
            # Write data to file (shorter to fit in 40 bytes)
            test_data = b"Hello DESFire EV1! Test."
            print(f"\nWriting test data ({len(test_data)} bytes):")
            print(f"  Content: \"{test_data.decode('utf-8')}\"")
            
            card.authenticate([0x00], default_key)
            if file_mgr.write_data(std_file_id, offset=0, data=test_data):
                print("   ✓ Data written to file")
            else:
                print("   ✗ Failed to write data")
            
            # Read data back
            print("\nReading data back from file...")
            card.authenticate([0x00], default_key)
            read_data = file_mgr.read_data(std_file_id, offset=0, length=len(test_data))
            if read_data:
                content = bytes(read_data).decode('utf-8', errors='ignore')
                print(f"   ✓ Data read successfully ({len(read_data)} bytes)")
                print(f"   Content: \"{content}\"")
            else:
                print("   ✗ Failed to read data")
        else:
            print("   ✗ Failed to create standard file")
        
        print(f"\nStandard File Summary:")
        print(f"  • File ID: 0x{std_file_id:02X}")
        print(f"  • Type: Standard Data File")
        print(f"  • Size: {std_file_size} bytes")
        print(f"  • Used: {len(test_data)} bytes")
        print(f"  • Free: {std_file_size - len(test_data)} bytes")
        
        press_enter_to_continue()
        
        # ============================================
        # 8. VALUE FILE EXAMPLE
        # ============================================
        print("\n" + "="*60)
        print("8. VALUE FILE DEMONSTRATION")
        print("="*60)
        print("\nValue files store integer values.")
        print("They support credit/debit operations with limits.")
        print("Perfect for e-purse, loyalty points, or token systems.")
        
        value_file_id = 0x02
        lower_limit = 0
        upper_limit = 1000
        initial_value = 500
        
        # Check if file already exists
        if value_file_id in existing_files:
            print(f"\nFile 0x{value_file_id:02X} already exists.")
            print("Deleting it to start fresh...")
            card.authenticate([0x00], default_key)
            if file_mgr.delete_file(value_file_id):
                print(f"   ✓ File 0x{value_file_id:02X} deleted")
        
        # Create value file
        print(f"\nCreating value file:")
        print(f"  File ID: 0x{value_file_id:02X}")
        print(f"  Lower Limit: {lower_limit}")
        print(f"  Upper Limit: {upper_limit}")
        print(f"  Initial Value: {initial_value}")
        print(f"  Size: 4 bytes (32-bit integer)")
        
        card.authenticate([0x00], default_key)
        if file_mgr.create_value_file(value_file_id, 
                                     lower_limit=lower_limit,
                                     upper_limit=upper_limit,
                                     initial_value=initial_value,
                                     limited_credit=False):
            print("   ✓ Value file created successfully")
            
            # Get initial value
            card.authenticate([0x00], default_key)
            initial = file_mgr.get_value(value_file_id)
            if initial is not None:
                print(f"\n   Initial value: {initial}")
                print(f"   Balance: {initial} / {upper_limit}")
            else:
                print("   ✗ Failed to read initial value")
            
            # Credit 200
            print("\nPerforming credit operation:")
            print(f"  Adding: 200")
            print(f"  Expected: {initial} + 200 = {initial + 200}")
            
            card.authenticate([0x00], default_key)
            if file_mgr.credit_value(value_file_id, 200):
                print("   ✓ Credit operation successful")
                # Commit transaction
                if file_mgr.commit_transaction():
                    print("   ✓ Transaction committed")
                
                # Read new value
                card.authenticate([0x00], default_key)
                current = file_mgr.get_value(value_file_id)
                if current is not None:
                    print(f"   New value: {current}")
                    print(f"   Balance: {current} / {upper_limit}")
            else:
                print("   ✗ Failed to credit")
            
            # Debit 150
            print("\nPerforming debit operation:")
            print(f"  Subtracting: 150")
            print(f"  Expected: {current} - 150 = {current - 150}")
            
            card.authenticate([0x00], default_key)
            if file_mgr.debit_value(value_file_id, 150):
                print("   ✓ Debit operation successful")
                # Commit transaction
                if file_mgr.commit_transaction():
                    print("   ✓ Transaction committed")
                
                # Read final value
                card.authenticate([0x00], default_key)
                final = file_mgr.get_value(value_file_id)
                if final is not None:
                    print(f"   Final value: {final}")
                    print(f"   Balance: {final} / {upper_limit}")
                    print(f"   Available for debit: {final - lower_limit}")
            else:
                print("   ✗ Failed to debit")
        else:
            print("   ✗ Failed to create value file")
        
        print(f"\nValue File Summary:")
        print(f"  • File ID: 0x{value_file_id:02X}")
        print(f"  • Type: Value File")
        print(f"  • Size: 4 bytes")
        print(f"  • Range: {lower_limit} to {upper_limit}")
        print(f"  • Current: {final if 'final' in locals() else 'N/A'}")
        
        press_enter_to_continue()
        
        # ============================================
        # 9. LINEAR RECORD FILE EXAMPLE
        # ============================================
        print("\n" + "="*60)
        print("9. LINEAR RECORD FILE DEMONSTRATION")
        print("="*60)
        print("\nLinear record files store fixed-size records.")
        print("Records are written sequentially.")
        print("When full, no more records can be added.")
        print("Ideal for logging or audit trails.")
        
        linear_file_id = 0x03
        record_size = 8  # bytes per record
        max_records = 5  # maximum records
        
        # Calculate file size
        linear_file_size = record_size * max_records
        
        print(f"\nFile Configuration:")
        print(f"  File ID: 0x{linear_file_id:02X}")
        print(f"  Record Size: {record_size} bytes")
        print(f"  Max Records: {max_records}")
        print(f"  Total Size: {linear_file_size} bytes")
        print(f"  Behavior: Stops accepting writes when full")
        
        # Re-authenticate before file operations
        card.authenticate([0x00], default_key)
        
        # Check if file already exists
        if linear_file_id in existing_files:
            print(f"\nFile 0x{linear_file_id:02X} already exists.")
            print("Deleting it to start fresh...")
            card.authenticate([0x00], default_key)
            if file_mgr.delete_file(linear_file_id):
                print(f"   ✓ File 0x{linear_file_id:02X} deleted")
        
        # Create linear record file
        if file_mgr.create_linear_record_file(linear_file_id,
                                            record_size=record_size,
                                            max_records=max_records):
            print("\n   ✓ Linear record file created successfully")
            
            # Write records (more than capacity to demonstrate limit)
            print(f"\nWriting records (attempting {max_records + 3}, expecting {max_records} successes):")
            
            successful_writes = 0
            for i in range(max_records + 3):
                data_str = f"LIN{i+1:04d}"
                record_data = list(data_str.encode('utf-8'))
                print(f"  Write {i+1}: '{data_str}'", end=" ")
                
                card.authenticate([0x00], default_key)
                try:
                    if file_mgr.write_record(linear_file_id, 0, record_data):
                        file_mgr.commit_transaction()
                        successful_writes += 1
                        print("✓ SUCCESS")
                    else:
                        print("✗ FAILED (File full)")
                        break
                except Exception as e:
                    print(f"✗ ERROR: {e}")
                    break
            
            print(f"\nResult: {successful_writes}/{max_records + 3} writes successful")
            print(f"Expected: Linear file stops at {max_records} records")
            
            # Read records
            print("\nReading all records from linear file...")
            card.authenticate([0x00], default_key)
            records_data = file_mgr.read_records(linear_file_id, record_offset=0, num_records=0)
            if records_data:
                # Parse records
                records = []
                for i in range(0, len(records_data), record_size):
                    if i + record_size <= len(records_data):
                        record = records_data[i:i+record_size]
                        record_str = bytes(record).decode('utf-8', errors='ignore').strip()
                        if record_str:
                            records.append(record_str)
                
                print(f"   Found {len(records)} records:")
                for idx, rec in enumerate(records, 1):
                    print(f"     Record {idx}: '{rec}'")
                
                used_space = len(records) * record_size
                print(f"\n   Storage used: {used_space} / {linear_file_size} bytes")
                print(f"   Records used: {len(records)} / {max_records}")
            else:
                print("   No records found or failed to read")
        else:
            print("   ✗ Failed to create linear record file")
        
        press_enter_to_continue()
        
        # ============================================
        # 10. CYCLIC RECORD FILE EXAMPLE
        # ============================================
        print("\n" + "="*60)
        print("10. CYCLIC RECORD FILE DEMONSTRATION")
        print("="*60)
        print("\nCyclic record files store fixed-size records.")
        print("When full, oldest records are overwritten.")
        print("Always maintains the N most recent records.")
        print("Ideal for recent transaction history or sensor data.")
        
        cyclic_file_id = 0x04
        record_size = 8  # bytes per record
        max_records = 5  # maximum records
        
        # Calculate file size
        cyclic_file_size = record_size * max_records
        
        print(f"\nFile Configuration:")
        print(f"  File ID: 0x{cyclic_file_id:02X}")
        print(f"  Record Size: {record_size} bytes")
        print(f"  Max Records: {max_records}")
        print(f"  Total Size: {cyclic_file_size} bytes")
        print(f"  Behavior: Overwrites oldest records when full")
        
        # Re-authenticate before file operations
        card.authenticate([0x00], default_key)
        
        # Try different method for cyclic file if first fails
        print("\nCreating cyclic record file...")
        
        
        # Check if file already exists
        if cyclic_file_id in existing_files:
            print(f"\nFile 0x{cyclic_file_id:02X} already exists.")
            print("Deleting it to start fresh...")
            card.authenticate([0x00], default_key)
            if file_mgr.delete_file(cyclic_file_id):
                print(f"   ✓ File 0x{cyclic_file_id:02X} deleted")
                
                
        
        # Try with simpler parameters
        if file_mgr.create_cyclic_record_file(cyclic_file_id,
                                             record_size=record_size,
                                             max_records=max_records):
            print("   ✓ Cyclic record file created successfully")
        else:
            print("   ✗ Failed with standard method, trying alternative...")
            # Try creating with explicit access rights
            card.authenticate([0x00], default_key)
            # Use the same parameters as linear file (they often work for both)
            if file_mgr.create_cyclic_record_file(cyclic_file_id,
                                                 record_size=record_size,
                                                 max_records=max_records):
                print("   ✓ Cyclic record file created with alternative method")
            else:
                print("   ✗ Could not create cyclic record file")
                print("   Skipping cyclic file demonstration...")
                cyclic_file_created = False
                press_enter_to_continue()
                # Skip to next section
                file_ids_to_check = [std_file_id, value_file_id, linear_file_id]
                press_enter_to_continue()
                # Skip cleanup and go to summary
                print("\n" + "="*60)
                print("12. CLEANUP AND CARD MANAGEMENT")
                print("="*60)
                
                print("\nChoose cleanup option:")
                print("1. Delete only test files (keep application)")
                print("2. Delete test application (includes all files)")
                print("3. Format entire card (WARNING: ERASES EVERYTHING!)")
                print("4. Keep everything (no cleanup)")
                
                choice = input("\nSelect option (1-4): ")
                
                if choice == "1":
                    print("\nDeleting test files...")
                    card.select_application(new_aid)
                    card.authenticate([0x00], default_key)
                    deleted_count = 0
                    for file_id in file_ids_to_check:
                        print(f"  Deleting file 0x{file_id:02X}...", end=" ")
                        if file_mgr.delete_file(file_id):
                            print("✓")
                            deleted_count += 1
                        else:
                            print("✗")
                    print(f"\nDeleted {deleted_count} files.")
                    print("Application remains with no files.")
                    
                elif choice == "2":
                    print("\nDeleting test application...")
                    # Select root application to delete our app
                    root_aid = [0x00, 0x00, 0x00]
                    if card.select_application(root_aid):
                        card.authenticate([0x00], default_key)
                        if app_mgr.delete_application(new_aid):
                            print(f"   ✓ Application {new_aid} deleted")
                            print("   All application files have been removed.")
                        else:
                            print(f"   ✗ Failed to delete application")
                    
                elif choice == "3":
                    print("\n" + "!"*60)
                    print("WARNING: FORMATTING WILL ERASE ALL DATA ON CARD!")
                    print("This includes ALL applications, files, and keys!")
                    print("The card will be restored to factory default state.")
                    print("!"*60)
                    
                    confirm = input("\nAre you absolutely sure? Type 'YES' to confirm: ")
                    if confirm == "YES":
                        print("\nFormatting card...")
                        # Must be authenticated at PICC level to format
                        card.select_application([0x00, 0x00, 0x00])  # Select root
                        card.authenticate([0x00], default_key)
                        if card.format_card():
                            print("✓ Card formatted successfully")
                            print("✓ All data erased")
                            print("✓ Card is now in factory default state")
                        else:
                            print("✗ Failed to format card")
                    else:
                        print("Format cancelled - no changes made.")
                        
                else:
                    print("\nKeeping all test data on card.")
                    print("Application and files remain intact.")
                
                press_enter_to_continue()
                
                # ============================================
                # 13. WORKFLOW SUMMARY
                # ============================================
                print("\n" + "="*70)
                print("WORKFLOW COMPLETED SUCCESSFULLY!")
                print("="*70)
                
                print("\nSUMMARY OF OPERATIONS PERFORMED:")
                print("-" * 50)
                print("✓ Card connection established")
                print("✓ Card version information read")
                print("✓ PICC level authentication")
                print("✓ Application created/selected")
                print("✓ Application level authentication")
                print("✓ Standard Data File created and tested")
                print("✓ Value File created with credit/debit operations")
                print("✓ Linear Record File demonstrated (sequential storage)")
                print("✗ Cyclic Record File (could not create)")
                print("✓ File types detected and displayed")
                print("✓ Cleanup/format options presented")
                
                print("\nCARD STATUS:")
                print("-" * 50)
                try:
                    # Select root to see applications
                    root_aid = [0x00, 0x00, 0x00]
                    if card.select_application(root_aid):
                        apps = app_mgr.list_applications()
                        if apps:
                            print(f"Applications on card: {len(apps)}")
                            for app in apps:
                                print(f"  - AID: {app}")
                        else:
                            print("No applications (card may be formatted)")
                except:
                    print("Could not read final card status")
                
                print("\n" + "="*70)
                print("The card is ready for your custom application development!")
                print("="*70)
                
                print("\n" + "-"*40)
                print("Workflow completed.")
                print("Card remains inserted - ready for further operations.")
                print("-"*40)
                return
        
        # If cyclic file was created successfully, continue with demonstration
        if 'cyclic_file_created' not in locals() or cyclic_file_created:
            # Write more records than capacity to demonstrate overwriting
            total_writes = max_records + 3
            print(f"\nWriting {total_writes} records (exceeds {max_records} capacity):")
            print(f"  Expecting: Last {max_records} records preserved")
            
            successful_writes = 0
            for i in range(total_writes):
                data_str = f"CYC{i+1:04d}"
                record_data = list(data_str.encode('utf-8'))
                print(f"  Write {i+1}: '{data_str}'", end=" ")
                
                card.authenticate([0x00], default_key)
                try:
                    if file_mgr.write_record(cyclic_file_id, 0, record_data):
                        file_mgr.commit_transaction()
                        successful_writes += 1
                        print("✓ SUCCESS")
                    else:
                        print("✗ FAILED")
                        break
                except Exception as e:
                    print(f"✗ ERROR: {e}")
                    break
            
            print(f"\nResult: {successful_writes}/{total_writes} writes successful")
            print(f"Expected: Only records CYC0004-CYC0008 remain")
            
            # Read records
            print("\nReading all records from cyclic file...")
            card.authenticate([0x00], default_key)
            records_data = file_mgr.read_records(cyclic_file_id, record_offset=0, num_records=0)
            if records_data:
                # Parse records
                records = []
                for i in range(0, len(records_data), record_size):
                    if i + record_size <= len(records_data):
                        record = records_data[i:i+record_size]
                        record_str = bytes(record).decode('utf-8', errors='ignore').strip()
                        if record_str:
                            records.append(record_str)
                
                print(f"   Found {len(records)} records:")
                for idx, rec in enumerate(records, 1):
                    print(f"     Record {idx}: '{rec}'")
                
                if len(records) == max_records:
                    print("\n   Note: File is full!")
                    print(f"   Records CYC0001-CYC0003 have been overwritten")
                    print(f"   Only the {max_records} most recent records remain")
                
                used_space = len(records) * record_size
                print(f"\n   Storage used: {used_space} / {cyclic_file_size} bytes")
                print(f"   Records stored: {len(records)} (always up to {max_records})")
            else:
                print("   No records found or failed to read")
        
        press_enter_to_continue()
        
        # ============================================
        # 11. FILE TYPE DETECTION
        # ============================================
        print("\n" + "="*60)
        print("11. FILE TYPE DETECTION")
        print("="*60)
        print("\nIdentifying all created files and their properties...")
        
        file_ids_to_check = [std_file_id, value_file_id, linear_file_id]
        if 'cyclic_file_created' not in locals() or cyclic_file_created:
            file_ids_to_check.append(cyclic_file_id)
        
        print("\nFile Inventory:")
        print("-" * 50)
        print("ID   | Type              | Size       | Description")
        print("-" * 50)
        
        for file_id in file_ids_to_check:
            card.authenticate([0x00], default_key)
            file_type = file_mgr.get_file_type(file_id)
            
            if file_type is None:
                print(f"0x{file_id:02X} | Could not detect    | Unknown     | File may not exist or error reading")
                continue
                
            type_names = {
                0x00: "Standard Data",
                0x02: "Value",
                0x03: "Linear Record",
                0x04: "Cyclic Record"
            }
            type_name = type_names.get(file_type, f"Unknown (0x{file_type:02X})")
            
            # Calculate file sizes
            if file_type == 0x00:  # Standard
                size_info = f"{std_file_size} bytes"
            elif file_type == 0x02:  # Value
                size_info = "4 bytes"
            elif file_type == 0x03:  # Linear Record
                size_info = f"{linear_file_size} bytes ({max_records}×{record_size})"
            elif file_type == 0x04:  # Cyclic Record
                size_info = f"{cyclic_file_size} bytes ({max_records}×{record_size})"
            else:
                size_info = "Unknown"
            
            # File descriptions
            descriptions = {
                0x00: "General data storage",
                0x02: "Integer value with limits",
                0x03: "Sequential records (no overwrite)",
                0x04: "Cyclic records (overwrites oldest)"
            }
            description = descriptions.get(file_type, "Unknown file type")
            
            print(f"0x{file_id:02X} | {type_name:<16} | {size_info:<10} | {description}")
        
        total_size = std_file_size + 4 + linear_file_size
        if cyclic_file_id in file_ids_to_check:
            total_size += cyclic_file_size
        print("-" * 50)
        print(f"Total storage used: {total_size} bytes")
        
        press_enter_to_continue()
        
        # ============================================
        # 12. CLEANUP AND CARD MANAGEMENT
        # ============================================
        print("\n" + "="*60)
        print("12. CLEANUP AND CARD MANAGEMENT")
        print("="*60)
        
        print("\nChoose cleanup option:")
        print("1. Delete only test files (keep application)")
        print("2. Delete test application (includes all files)")
        print("3. Format entire card (WARNING: ERASES EVERYTHING!)")
        print("4. Keep everything (no cleanup)")
        
        choice = input("\nSelect option (1-4): ")
        
        if choice == "1":
            print("\nDeleting test files...")
            card.select_application(new_aid)
            card.authenticate([0x00], default_key)
            deleted_count = 0
            for file_id in file_ids_to_check:
                print(f"  Deleting file 0x{file_id:02X}...", end=" ")
                if file_mgr.delete_file(file_id):
                    print("✓")
                    deleted_count += 1
                else:
                    print("✗")
            print(f"\nDeleted {deleted_count} files.")
            print("Application remains with no files.")
            
        elif choice == "2":
            print("\nDeleting test application...")
            # Select root application to delete our app
            root_aid = [0x00, 0x00, 0x00]
            if card.select_application(root_aid):
                card.authenticate([0x00], default_key)
                if app_mgr.delete_application(new_aid):
                    print(f"   ✓ Application {new_aid} deleted")
                    print("   All application files have been removed.")
                else:
                    print(f"   ✗ Failed to delete application")
            
        elif choice == "3":
            print("\n" + "!"*60)
            print("WARNING: FORMATTING WILL ERASE ALL DATA ON CARD!")
            print("This includes ALL applications, files, and keys!")
            print("The card will be restored to factory default state.")
            print("!"*60)
            
            confirm = input("\nAre you absolutely sure? Type 'YES' to confirm: ")
            if confirm == "YES":
                print("\nFormatting card...")
                # Must be authenticated at PICC level to format
                card.select_application([0x00, 0x00, 0x00])  # Select root
                card.authenticate([0x00], default_key)
                if card.format_card():
                    print("✓ Card formatted successfully")
                    print("✓ All data erased")
                    print("✓ Card is now in factory default state")
                else:
                    print("✗ Failed to format card")
            else:
                print("Format cancelled - no changes made.")
                
        else:
            print("\nKeeping all test data on card.")
            print("Application and files remain intact.")
        
        press_enter_to_continue()
        
        # ============================================
        # 13. WORKFLOW SUMMARY
        # ============================================
        print("\n" + "="*70)
        print("WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        print("\nSUMMARY OF OPERATIONS PERFORMED:")
        print("-" * 50)
        print("✓ Card connection established")
        print("✓ Card version information read")
        print("✓ PICC level authentication")
        print("✓ Application created/selected")
        print("✓ Application level authentication")
        print("✓ Standard Data File created and tested")
        print("✓ Value File created with credit/debit operations")
        print("✓ Linear Record File demonstrated (sequential storage)")
        if 'cyclic_file_created' not in locals() or cyclic_file_created:
            print("✓ Cyclic Record File demonstrated (overwriting storage)")
        else:
            print("✗ Cyclic Record File (could not create)")
        print("✓ File types detected and displayed")
        print("✓ Cleanup/format options presented")
        
        print("\nFILE TYPES DEMONSTRATED:")
        print("-" * 50)
        print("• Standard Data: General purpose read/write")
        print("• Value: Integer operations with limits")
        print("• Linear Record: Fixed-size sequential records")
        if 'cyclic_file_created' not in locals() or cyclic_file_created:
            print("• Cyclic Record: Fixed-size overwriting records")
        
        print("\nCARD STATUS:")
        print("-" * 50)
        try:
            # Select root to see applications
            root_aid = [0x00, 0x00, 0x00]
            if card.select_application(root_aid):
                apps = app_mgr.list_applications()
                if apps:
                    print(f"Applications on card: {len(apps)}")
                    for app in apps:
                        print(f"  - AID: {app}")
                else:
                    print("No applications (card may be formatted)")
        except:
            print("Could not read final card status")
        
        print("\n" + "="*70)
        print("The card is ready for your custom application development!")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        print("Card connection may still be active.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "-"*40)
        print("Workflow completed.")
        print("Card remains inserted - ready for further operations.")
        print("-"*40)

if __name__ == "__main__":
    main()
