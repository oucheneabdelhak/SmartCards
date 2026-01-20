from Crypto.Cipher import DES
import random
from smartcard.System import readers
from smartcard.util import toHexString

def des_cbc_encrypt(data, key, iv=bytes(8)):
    """Encrypt data using DES in CBC mode"""
    cipher = DES.new(key, DES.MODE_CBC, iv=iv)
    if len(data) % 8 != 0:
        data = data + bytes(8 - len(data) % 8)
    return cipher.encrypt(data)

def des_cbc_decrypt(data, key, iv=bytes(8)):
    """Decrypt data using DES in CBC mode"""
    cipher = DES.new(key, DES.MODE_CBC, iv=iv)
    return cipher.decrypt(data)

def generate_reader_challenge():
    """Generate random 8-byte challenge"""
    return bytes([random.randint(0, 255) for _ in range(8)])

def rotate_left(data, n=1):
    """Rotate bytes left by n positions"""
    return data[n:] + data[:n]


def to_3bytes(value):
    """Convert integer to 3-byte little-endian list"""
    return [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF]

def to_4bytes(value):
    """Convert integer to 4-byte little-endian list"""
    return [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF, (value >> 24) & 0xFF]

def from_4bytes(byte_list):
    """Convert 4-byte little-endian list to integer"""
    return byte_list[0] | (byte_list[1] << 8) | (byte_list[2] << 16) | (byte_list[3] << 24)




class DesfireCard:
    def __init__(self, reader_index=0):
        """Initialize connection to card"""
        r = readers()
        self.reader = r[reader_index]
        self.connection = self.reader.createConnection()
        self.connection.connect()
        print(f"Connected to: {self.reader}")
        print(f"ATR: {toHexString(self.connection.getATR())}")
    
    def transmit(self, apdu):
        """Send APDU and return response"""
        return self.connection.transmit(apdu)
    
    def get_version(self):
        """Get card version info (3 frames)"""
        apdu = [0x90, 0x60, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.transmit(apdu)
        
        frames = [data]
        while sw2 == 0xAF:
            apdu = [0x90, 0xAF, 0x00, 0x00, 0x00]
            data, sw1, sw2 = self.transmit(apdu)
            frames.append(data)
        
        return frames
    
    def select_application(self, aid):
        """Select application by AID"""
        apdu = [0x90, 0x5A, 0x00, 0x00, 0x03] + aid + [0x00]
        data, sw1, sw2 = self.transmit(apdu)
        return sw1 == 0x91 and sw2 == 0x00
    
    def authenticate(self, key_number, key_value):
        """Authenticate with DES key"""
        # Request challenge
        apdu = [0x90, 0x0A, 0x00, 0x00, 0x01] + key_number + [0x00]
        encrypted_challenge, sw1, sw2 = self.transmit(apdu)
        
        # Decrypt and rotate card challenge
        card_challenge = des_cbc_decrypt(bytes(encrypted_challenge), key_value)
        rotated = rotate_left(card_challenge, 1)
        
        # Generate reader challenge and combine
        reader_challenge = generate_reader_challenge()
        response_data = reader_challenge + rotated
        
        # Encrypt and send
        encrypted_response = des_cbc_encrypt(response_data, key_value)
        apdu = [0x90, 0xAF, 0x00, 0x00, 0x10] + list(encrypted_response) + [0x00]
        data, sw1, sw2 = self.transmit(apdu)
        
        return sw1 == 0x91 and sw2 == 0x00
    
    def format_card(self):
        """Format entire card (deletes everything)"""
        apdu = [0x90, 0xFC, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.transmit(apdu)
        return sw1 == 0x91 and sw2 == 0x00
    
    def commit_transaction(self):
        """Validate all pending writes in current application"""
        apdu = [0x90, 0xC7, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.transmit(apdu)
        print(f"Commit transaction - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00

    def abort_transaction(self):
        """Cancel all pending writes in current application"""
        apdu = [0x90, 0xA7, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.transmit(apdu)
        print(f"Abort transaction - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    


class ApplicationManager:
    def __init__(self, card):
        """Initialize with DesfireCard instance"""
        self.card = card
    
    def list_applications(self):
        """List all application IDs"""
        apdu = [0x90, 0x6A, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        
        if sw1 == 0x91 and sw2 == 0x00:
            aids = [data[i:i+3] for i in range(0, len(data), 3)]
            for aid in aids:
                print(f"Application: {toHexString(aid)}")
            return aids
        return []
    
    def create_application(self, aid, key_settings=0x0F, num_keys=0x01):
        """Create new application"""
        apdu = [0x90, 0xCA, 0x00, 0x00, 0x05] + aid + [key_settings, num_keys, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Create app {toHexString(aid)} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def delete_application(self, aid):
        """Delete application"""
        apdu = [0x90, 0xDA, 0x00, 0x00, 0x03] + aid + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Delete {toHexString(aid)} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def change_key_settings(self, new_settings):
        """Change PICC key settings"""
        apdu = [0x90, 0x54, 0x00, 0x00, 0x01, new_settings, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Change key settings - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    

class FileManager:
    def __init__(self, card):
        """Initialize with DesfireCard instance"""
        self.card = card
    
    def list_files(self):
        """List all file IDs in current application"""
        apdu = [0x90, 0x6F, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        
        if sw1 == 0x91 and sw2 == 0x00:
            file_ids = list(data)
            print(f"Files: {[f'0x{fid:02X}' for fid in file_ids]}")
            return file_ids
        return []
    
    def delete_file(self, file_id):
        """Delete file"""
        apdu = [0x90, 0xDF, 0x00, 0x00, 0x01, file_id, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Delete file {file_id} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def get_file_type(self, file_id):
        apdu = [0x90, 0xF5, 0x00, 0x00, 0x01, file_id, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        if sw1 != 0x91 or sw2 != 0x00 or not data:
            return None

        file_type = data[0]
        mapping = {
            0x00: "Standard data",
            0x01: "Backup data",
            0x02: "Value",
            0x03: "Linear record",
            0x04: "Cyclic record",
        }
        print(f"File {file_id} type: {mapping.get(file_type, 'Unknown')} (0x{file_type:02X})")
        return file_type

    
    # Standard File
    def create_standard_file(self, file_id, file_size, comm_settings=0x00, access_rights=[0x00, 0x00]):
        """Create standard data file"""
        size_bytes = to_3bytes(file_size)
        apdu = [0x90, 0xCD, 0x00, 0x00, 0x07, file_id, comm_settings] + access_rights + size_bytes + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Create standard file {file_id} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def write_data(self, file_id, offset, data):
        """Write data to standard file"""
        offset_bytes = to_3bytes(offset)
        length_bytes = to_3bytes(len(data))
        
        # Convert data from bytes to list if needed
        if isinstance(data, bytes):
            data_list = list(data)
        else:
            data_list = data
            
        apdu = [0x90, 0x3D, 0x00, 0x00, 7 + len(data_list), file_id] + offset_bytes + length_bytes + data_list + [0x00]
        response, sw1, sw2 = self.card.transmit(apdu)
        print(f"Write to file {file_id} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def read_data(self, file_id, offset, length):
        """Read data from standard file"""
        offset_bytes = to_3bytes(offset)
        length_bytes = to_3bytes(length)
        apdu = [0x90, 0xBD, 0x00, 0x00, 0x07, file_id] + offset_bytes + length_bytes + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Read from file {file_id} - Status: {sw1:02X} {sw2:02X}")
        print(f"Data: {bytes(data).decode('utf-8', errors='ignore')}")
        return data
    
    
    # Value File
    def create_value_file(self, file_id, lower_limit, upper_limit, initial_value, limited_credit=False, comm_settings=0x00, access_rights=[0x00, 0x00]):
        """Create value file"""
        lower_bytes = to_4bytes(lower_limit)
        upper_bytes = to_4bytes(upper_limit)
        initial_bytes = to_4bytes(initial_value)
        limited = 0x01 if limited_credit else 0x00
        apdu = [0x90, 0xCC, 0x00, 0x00, 0x11, file_id, comm_settings] + access_rights + lower_bytes + upper_bytes + initial_bytes + [limited, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Create value file {file_id} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def credit_value(self, file_id, amount):
        """Add value"""
        amount_bytes = to_4bytes(amount)
        apdu = [0x90, 0x0C, 0x00, 0x00, 0x05, file_id] + amount_bytes + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Credit {amount} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def debit_value(self, file_id, amount):
        """Subtract value"""
        amount_bytes = to_4bytes(amount)
        apdu = [0x90, 0xDC, 0x00, 0x00, 0x05, file_id] + amount_bytes + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Debit {amount} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def get_value(self, file_id):
        """Read current value"""
        apdu = [0x90, 0x6C, 0x00, 0x00, 0x01, file_id, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        if sw1 == 0x91 and sw2 == 0x00:
            value = from_4bytes(data)
            print(f"Value: {value}")
            return value
        return None
    
    # Record Files
    def create_linear_record_file(self, file_id, record_size, max_records, comm_settings=0x00, access_rights=[0x00, 0x00]):
        """Create linear record file"""
        size_bytes = to_3bytes(record_size)
        max_bytes = to_3bytes(max_records)
        apdu = [0x90, 0xC1, 0x00, 0x00, 0x0A, file_id, comm_settings] + access_rights + size_bytes + max_bytes + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Create linear record file {file_id} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def create_cyclic_record_file(self, file_id, record_size, max_records, comm_settings=0x00, access_rights=[0x00, 0x00]):
        """Create cyclic record file"""
        size_bytes = to_3bytes(record_size)
        max_bytes = to_3bytes(max_records)
        apdu = [0x90, 0xC0, 0x00, 0x00, 0x0A, file_id, comm_settings] + access_rights + size_bytes + max_bytes + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Create cyclic record file {file_id} - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def write_record(self, file_id, offset, data):
        """Write record"""
        offset_bytes = to_3bytes(offset)
        length_bytes = to_3bytes(len(data))
        
        # Convert data from bytes to list if needed
        if isinstance(data, bytes):
            data_list = list(data)
        else:
            data_list = data
            
        apdu = [0x90, 0x3B, 0x00, 0x00, 7 + len(data_list), file_id] + offset_bytes + length_bytes + data_list + [0x00]
        response, sw1, sw2 = self.card.transmit(apdu)
        print(f"Write record - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def read_records(self, file_id, record_offset, num_records):
        """Read records"""
        offset_bytes = to_3bytes(record_offset)
        num_bytes = to_3bytes(num_records)
        apdu = [0x90, 0xBB, 0x00, 0x00, 0x07, file_id] + offset_bytes + num_bytes + [0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Read records - Status: {sw1:02X} {sw2:02X}")
        print(f"Data: {bytes(data).decode('utf-8', errors='ignore')}")
        return data
    
    def clear_record_file(self, file_id):
        """Clear all records"""
        apdu = [0x90, 0xEB, 0x00, 0x00, 0x01, file_id, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Clear records - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
    
    def commit_transaction(self):
        """Validate all pending writes in current application"""
        apdu = [0x90, 0xC7, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Commit transaction - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00

    def abort_transaction(self):
        """Cancel all pending writes in current application"""
        apdu = [0x90, 0xA7, 0x00, 0x00, 0x00]
        data, sw1, sw2 = self.card.transmit(apdu)
        print(f"Abort transaction - Status: {sw1:02X} {sw2:02X}")
        return sw1 == 0x91 and sw2 == 0x00
