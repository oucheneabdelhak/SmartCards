DESFire EV1 Python Library

A comprehensive Python library for interfacing with MIFARE DESFire EV1 smart cards using PC/SC readers. This library provides a complete implementation for card management, application creation, file handling, and all four DESFire EV1 file types.
Features
Core Functionality

    Card Communication: PC/SC reader integration with automatic ATR detection

    Authentication: DES CBC mode authentication at both PICC and application levels

    Transaction Management: Commit/abort transactions with data integrity

    Card Formatting: Full card format capability (use with caution!)

Application Management

    Create, select, and delete applications

    List existing applications

    Change key settings

File System Support

All four DESFire EV1 file types are supported:

    Standard Data Files: General-purpose read/write storage

    Value Files: Integer storage with credit/debit operations and limits

    Linear Record Files: Fixed-size sequential records (no overwrite)

    Cyclic Record Files: Fixed-size records that overwrite oldest when full

File Structure
text

DESFireEV1/
├── DesFireEV1.py          # Main library with all DESFire EV1 functionality
├── example_workflow.py    # Complete demonstration of all features
└── README.md              # This documentation

Installation
Prerequisites

    PC/SC compatible card reader

    Python 3.6+

    MIFARE DESFire EV1 card (2K recommended for testing)

Required Packages
bash

pip install pyscard pycryptodome

Quick Start
Basic Usage
python

from DesFireEV1 import DesfireCard, ApplicationManager, FileManager

# Connect to card
card = DesfireCard(reader_index=0)

# Authenticate with default key (all zeros)
default_key = bytes([0x00] * 8)
card.authenticate([0x00], default_key)

# Create application manager
app_mgr = ApplicationManager(card)
app_mgr.create_application([0x00, 0x00, 0x01])

# Select application
card.select_application([0x00, 0x00, 0x01])

# Create file manager
file_mgr = FileManager(card)

# Create and use a standard file
file_mgr.create_standard_file(0x01, file_size=32)
file_mgr.write_data(0x01, 0, b"Hello DESFire!")
data = file_mgr.read_data(0x01, 0, 14)

Running the Complete Example
bash

python example_workflow.py

The example workflow demonstrates:

    Card initialization and version reading

    PICC and application level authentication

    Creation of all four file types

    Read/write operations for each file type

    Credit/debit operations for value files

    Record management for linear/cyclic files

    Cleanup options (delete files, applications, or format card)

API Reference
DesfireCard Class

    __init__(reader_index=0): Initialize connection to card reader

    get_version(): Get card version information (3 frames)

    select_application(aid): Select application by 3-byte AID

    authenticate(key_number, key_value): Authenticate with DES key

    format_card(): Format entire card (deletes everything)

    commit_transaction(): Validate pending writes

    abort_transaction(): Cancel pending writes

ApplicationManager Class

    list_applications(): List all application IDs

    create_application(aid, key_settings, num_keys): Create new application

    delete_application(aid): Delete application

    change_key_settings(new_settings): Change PICC key settings

FileManager Class

    list_files(): List all file IDs in current application

    get_file_type(file_id): Detect file type

    delete_file(file_id): Delete file

Standard File Operations

    create_standard_file(file_id, file_size, comm_settings, access_rights)

    write_data(file_id, offset, data)

    read_data(file_id, offset, length)

Value File Operations

    create_value_file(file_id, lower_limit, upper_limit, initial_value, limited_credit, comm_settings, access_rights)

    credit_value(file_id, amount): Add value

    debit_value(file_id, amount): Subtract value

    get_value(file_id): Read current value

Record File Operations

    create_linear_record_file(file_id, record_size, max_records, comm_settings, access_rights)

    create_cyclic_record_file(file_id, record_size, max_records, comm_settings, access_rights)

    write_record(file_id, offset, data)

    read_records(file_id, record_offset, num_records)

    clear_record_file(file_id): Clear all records

File Types Explained
1. Standard Data Files

    Purpose: General data storage

    Features: Random read/write access

    Size: Configurable (up to card capacity)

    Use Case: Storing configuration, user data, or any binary data

2. Value Files

    Purpose: Integer value storage with arithmetic operations

    Features: Credit/debit operations with limits, transaction support

    Size: Fixed 4 bytes (32-bit integer)

    Use Case: E-purse, loyalty points, token systems

3. Linear Record Files

    Purpose: Fixed-size record storage

    Features: Sequential writes, stops when full

    Behavior: Never overwrites existing records

    Use Case: Audit trails, logging, sequential data

4. Cyclic Record Files

    Purpose: Fixed-size record storage with overwrite

    Features: Always accepts writes, overwrites oldest when full

    Behavior: Maintains N most recent records

    Use Case: Recent transaction history, sensor data, rolling logs

Security Notes

⚠️ Important Security Considerations:

    Default Keys: The library uses default DES keys (all zeros) for demonstration. In production, always use unique, secure keys.

    Authentication: DESFire EV1 supports multiple authentication modes. This library implements DES CBC mode. For higher security, consider AES authentication.

    Key Management: Store keys securely. Never hardcode production keys in source code.

    Card Formatting: format_card() erases ALL data including keys. Use with extreme caution.

    Transaction Integrity: Always use commit_transaction() after multiple writes to ensure data integrity.

Troubleshooting
Common Issues

    "No card readers found"

        Ensure PC/SC service is running

        Check reader is properly connected

        Run with administrator privileges if needed

    Authentication failures

        Verify card uses DES authentication (not AES)

        Check key value (default is 8 bytes of 0x00)

        Ensure card is not locked or disabled

    File creation errors

        Check available memory on card

        Verify authentication level

        Ensure file ID is unique (0x00 to 0x1F)

    APDU errors

        Check SW1/SW2 status codes against DESFire EV1 manual

        Ensure proper sequence of operations

Status Code Reference

    0x9100: Success

    0x9101: Permission denied

    0x9103: Key not found

    0x910C: Insufficient memory

    0x910E: Invalid parameter

    0x911C: Command not supported

    0x91AE: Authentication error

Use Cases
Potential Applications

    Access Control: Store user credentials and permissions

    Loyalty Programs: Value files for points tracking

    Data Logging: Record files for audit trails

    IoT Devices: Configuration storage and data collection

    Ticketing Systems: Limited-use tokens or passes

Industry Applications

    Public transportation

    Building access systems

    Payment systems

    Inventory management

    Healthcare records

Contributing

Contributions are welcome! Please:

    Fork the repository

    Create a feature branch

    Add tests for new functionality

    Submit a pull request

License

This project is provided for educational and development purposes. Check LICENSE file for details.
Support

For issues, questions, or feature requests:

    Check the troubleshooting section

    Review DESFire EV1 documentation

    Submit a GitHub issue

Disclaimer

This software is provided as-is. The authors are not responsible for any data loss, security breaches, or damages resulting from the use of this code. Always test thoroughly in a development environment before deploying to production.

Happy coding with DESFire EV1! 🚀

Note: MIFARE DESFire is a registered trademark of NXP Semiconductors.
