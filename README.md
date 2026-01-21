DESFire EV1 Python Library

A comprehensive Python library for interfacing with MIFARE DESFire EV1 smart cards using PC/SC readers.
Features
Card Operations

    Initialize connection to DESFire EV1 cards

    Get card version information

    Authenticate using DES CBC mode

    Format card (use with caution!)

    Transaction management (commit/abort)

Application Management

    Create, select, and delete applications

    List existing applications

    Change key settings

File System Support

All four DESFire EV1 file types:

    Standard Data Files - General read/write storage

    Value Files - Integer storage with credit/debit operations

    Linear Record Files - Fixed-size sequential records

    Cyclic Record Files - Fixed-size overwriting records

Installation
Prerequisites

    PC/SC compatible card reader

    Python 3.6+

    MIFARE DESFire EV1 card

Required Packages

    pip install pyscard pycryptodome

Quick Start
Basic Usage

    from DesFireEV1 import DesfireCard, ApplicationManager, FileManager
    
    # Connect to card
    card = DesfireCard(reader_index=0)
    
    # Authenticate with default key
    default_key = bytes([0x00] * 8)
    card.authenticate([0x00], default_key)
    
    # Create application
    app_mgr = ApplicationManager(card)
    app_mgr.create_application([0x00, 0x00, 0x01])
    
    # Select application
    card.select_application([0x00, 0x00, 0x01])
    
    # Create and use a standard file
    file_mgr = FileManager(card)
    file_mgr.create_standard_file(0x01, file_size=32)
    file_mgr.write_data(0x01, 0, b"Hello DESFire!")
    data = file_mgr.read_data(0x01, 0, 14)
    
Run Complete Example

    python example_workflow.py
File Structure

    DESFireEV1/
    ├── DesFireEV1.py          # Main library with all functionality
    ├── example_workflow.py    # Complete demonstration
    └── README.md              # This file

API Reference
DesfireCard Class

    __init__(reader_index=0) - Connect to card

    get_version() - Get card version

    select_application(aid) - Select application

    authenticate(key_number, key_value) - Authenticate with key

    format_card() - Format entire card

    commit_transaction() - Commit writes

    abort_transaction() - Abort writes

ApplicationManager Class

    list_applications() - List all apps

    create_application(aid, key_settings, num_keys) - Create app

    delete_application(aid) - Delete app

FileManager Class

    list_files() - List files in app

    get_file_type(file_id) - Detect file type

    delete_file(file_id) - Delete file

Standard Files

    create_standard_file() - Create standard file

    write_data() - Write to file

    read_data() - Read from file

Value Files

    create_value_file() - Create value file

    credit_value() - Add value

    debit_value() - Subtract value

    get_value() - Read value

Record Files

    create_linear_record_file() - Create linear record file

    create_cyclic_record_file() - Create cyclic record file

    write_record() - Write record

    read_records() - Read records

    clear_record_file() - Clear records

Example Workflow

The example_workflow.py demonstrates:

    Card initialization - Connect and read version

    Authentication - PICC and application level

    Application creation - Create test application

    File creation - All four file types

    Operations - Read/write for each file type

    Cleanup - Delete files or format card

Troubleshooting
Common Issues

No card readers found:

    Ensure PC/SC service is running

    Check reader connection

    Run with admin privileges if needed

Authentication failed:

    Verify card uses DES authentication

    Check key value (default: 8 bytes of 0x00)

    Ensure card is not locked

File creation errors:

    Check available memory

    Verify authentication

    Ensure file ID is unique (0x00 to 0x1F)

Status Codes

    0x9100 - Success

    0x9101 - Permission denied

    0x9103 - Key not found

    0x910C - Insufficient memory

    0x91AE - Authentication error

Security Notes

⚠️ Important Security Considerations:

    Default Keys - Library uses default keys for demonstration. In production, use unique secure keys.

    Authentication - This implements DES CBC mode. For higher security, consider AES.

    Key Management - Store keys securely. Never hardcode in source code.

    Formatting - format_card() erases ALL data including keys. Use with caution.

    Transactions - Use commit_transaction() after writes for data integrity.

Use Cases

    Access Control Systems - User credentials and permissions

    Loyalty Programs - Points tracking with value files

    Data Logging - Audit trails with record files

    IoT Devices - Configuration storage

    Ticketing Systems - Limited-use tokens
