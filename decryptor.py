import hashlib
import datetime

class PasswordDecryptor:
    @staticmethod
    def decrypt_password(date):
        # Decrypt the password based on the date
        year, week, _ = date.isocalendar()
        password_str = f"{year}{week}"
        return hashlib.sha256(password_str.encode()).hexdigest()

if __name__ == "__main__":
    # Here we demonstrate the usage of decrypt_password function
    current_date = datetime.datetime.now()
    decrypted_password = PasswordDecryptor.decrypt_password(current_date)
    print(f"Decrypted password for the current date is: {decrypted_password}")
